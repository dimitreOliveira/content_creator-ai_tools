import logging
from enum import Enum

import gradio as gr
from dotenv import load_dotenv
from gitingest import ingest

from common import load_config
from utils import (
    build_prompt,
    count_tokens,
    count_tokens_with_file,
    generate_content,
    generate_content_with_file,
    setup_gemini_client,
    upload_file,
)

CONFIG_PATH = "configs.yaml"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ContentInputType(Enum):
    BLOG_POST = "Blog post"
    CODE_SCRIPT = "Code"


class ContentOutputType(Enum):
    BLOG_POST = "Blog post"
    README = "GitHub README.md file"
    CODE_BASE = "Code base"
    CODE_IMPROVEMENT = "Code improvement"
    VIDEO_WALKTHROUGH = "Video walkthrough"


def generate_fn(
    file_input,
    parsed_repository_tree,
    parsed_repository_content,
    additional_prompt,
    input_type,
    output_type,
):
    """Generates content based on user input and configurations.

    Args:
        file_input: The path to the input file.
        parsed_repository_tree: GitHub repository directory structure parsed as a txt input.
        parsed_repository_content: GitHub repository content parsed as a txt input.
        additional_prompt: Additional instructions from the user.
        input_type: The type of the input content.
        output_type: The desired output content type.

    Returns:
       The generated text output.
    """
    if not input_type:
        raise gr.Error("Choose an input type")

    if not output_type:
        raise gr.Error("Choose an output type")

    if not file_input and (
        (not parsed_repository_tree) and (not parsed_repository_content)
    ):
        raise gr.Error("Provide an input file (repository or file)")

    if file_input and (parsed_repository_tree and parsed_repository_content):
        raise gr.Error("Provide only a single input (repository or file)")

    prompt = build_prompt(input_type, output_type)
    logging.info(f"Base prompt:\n{prompt}")

    if file_input:
        prompt = f"{prompt}\n{additional_prompt}"

        gr.Info("Uploading file...")
        logging.info("Uploading file...")
        file_upload = upload_file(client, file_input)
        logging.info(f"Uploaded file: {file_upload.uri}")

        gr.Info("Counting prompt token count...")
        logging.info("Counting prompt token count...")
        token_count = count_tokens_with_file(
            client, prompt, file_upload, client_configs["model_id"]
        )
        gr.Info(f"Prompt had {token_count} tokens")
        logging.info(f"Prompt had {token_count} tokens")

        gr.Info("Generating output...")
        logging.info("Generating output...")
        output = generate_content_with_file(
            client,
            prompt,
            file_upload,
            client_configs["model_id"],
            client_configs["generation_config"],
        )

    if parsed_repository_tree and parsed_repository_content:
        prompt = f"{parsed_repository_tree}\n{parsed_repository_content}\n{prompt}\n{additional_prompt}"

        gr.Info("Counting prompt token count...")
        logging.info("Counting prompt token count...")
        token_count = count_tokens(client, prompt, client_configs["model_id"])
        gr.Info(f"Prompt had {token_count} tokens")
        logging.info(f"Prompt had {token_count} tokens")

        gr.Info("Generating output...")
        logging.info("Generating output...")
        output = generate_content(
            client,
            prompt,
            client_configs["model_id"],
            client_configs["generation_config"],
        )

    logging.info("Output generated")

    return {
        generated_content: output,
        content_row: gr.Row(visible=True),
    }


def iterate_fn(prompt, additional_prompt):
    """Generates content based on user input and configurations.

    Args:
        prompt: Base prompt used for the iteration.
        additional_prompt: Additional instructions from the user.

    Returns:
       The generated text output.
    """

    if not prompt:
        raise gr.Error("Input prompt is empty")

    if not additional_prompt:
        raise gr.Error("Iteration prompt is empty")

    prompt = f"{prompt}\n{additional_prompt}"

    gr.Info("Generating output...")
    logging.info("Generating output...")
    output = generate_content(
        client,
        prompt,
        client_configs["model_id"],
        client_configs["generation_config"],
    )
    logging.info("Output generated")

    return output


def parse_repository_fn(
    repository_path,
    max_file_size=(10 * 1024 * 1024),
    include_patterns=None,
    exclude_patterns=".*",
):
    max_file_size = max_file_size * (1024 * 1024)  # Convert Bytes to Megabytes
    gr.Info("Parsing repository")
    logging.info(
        f"""Parsing repository
                 Parsing params:
                    Repository path: {repository_path}
                    Max file size: {max_file_size}
                    Include patterns: {include_patterns}
                    Exclude patterns: {exclude_patterns}"""
    )

    summary, tree, content = ingest(
        source=repository_path,
        max_file_size=max_file_size,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
    )

    logging.info("Parse finished")
    logging.info(f"Parse summary\n{summary}")

    return summary, tree, content


# Gradio app
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                gr.Markdown("# Provide as input a file or a GitHub repository")

            with gr.Column(scale=1):
                with gr.Row():
                    with gr.Column(scale=1):
                        repository_path = gr.Textbox(
                            label="Provide a URL or path to a local repository"
                        )

                        with gr.Accordion("Parsing params", open=False):
                            max_file_size = gr.Slider(
                                0.01,
                                100,
                                value=1,
                                step=0.1,
                                interactive=True,
                                label="Include files under (MB)",
                            )
                            include_patterns = gr.Textbox(
                                label="Include patterns (e.g.: README.md, src/, *.py)"
                            )
                            exclude_patterns = gr.Textbox(
                                label="Exclude patterns (e.g.: LICENSE, assets/, *.toml, .*)"
                            )

                        with gr.Accordion("Parsed output", open=False):
                            summary_txt = gr.Textbox(label="Summary", lines=4)
                            tree_txt = gr.Textbox(
                                label="Tree", lines=10, show_copy_button=True
                            )
                            content_txt = gr.Textbox(
                                label="Content", lines=20, show_copy_button=True
                            )

                        parse_repository_btn = gr.Button("Parse GitHub repository")
                        parse_repository_btn.click(
                            fn=parse_repository_fn,
                            inputs=[
                                repository_path,
                                max_file_size,
                                include_patterns,
                                exclude_patterns,
                            ],
                            outputs=[summary_txt, tree_txt, content_txt],
                        )

                    with gr.Column(scale=1):
                        file_input = gr.File(
                            label="Select a file to upload", file_count="single"
                        )

    with gr.Row():
        gr.Markdown("## Define the desired inputs and outputs")

    with gr.Row():
        with gr.Column(scale=1):
            radio_input_type = gr.Radio(
                [x.value for x in list(ContentInputType)],
                label="Input type",
            )
        with gr.Column(scale=1):
            radio_output_type = gr.Radio(
                [x.value for x in list(ContentOutputType)],
                label="What kind of content would you like to create?",
            )

    with gr.Row():
        additional_prompt = gr.Textbox(
            label="Additional prompt information",
            info="Describe the kind of content that you want to generate",
        )

    with gr.Row(visible=False) as content_row:
        with gr.Column(scale=1):
            generated_content = gr.Textbox(
                label="Generated content", interactive=True, show_copy_button=True
            )

            additional_steps = gr.Textbox(
                label="Keep iterate over the content",
                info="Describe what you want to modify over the content created",
            )

            iterate_content_btn = gr.Button("Iterate over the content")
            iterate_content_btn.click(
                fn=iterate_fn,
                inputs=[
                    generated_content,
                    additional_steps,
                ],
                outputs=generated_content,
            )

    with gr.Row():
        generate_content_btn = gr.Button("Generate content")
        generate_content_btn.click(
            fn=generate_fn,
            inputs=[
                file_input,
                tree_txt,
                content_txt,
                additional_prompt,
                radio_input_type,
                radio_output_type,
            ],
            outputs=[generated_content, content_row],
        )

if __name__ == "__main__":
    # Load configurations
    app_configs = load_config(CONFIG_PATH)
    if not app_configs:
        exit()

    # Load env vars
    load_dotenv()

    # Setup Gemini client
    client = setup_gemini_client()
    # Only using AI Studio for now
    client_configs = app_configs["ai_studio"]

    demo.launch()
