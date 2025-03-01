from typing import Any, Dict, Optional, Tuple

import gradio as gr
from dotenv import load_dotenv

from client.gemini_client import AIStudioGeminiClient, VertexAIGeminiClient
from config.config_loader import load_config
from enums import ContentInputType, ContentOutputType
from prompts.base_prompts import (
    DEFAULT_BLOG_POST_PROMPT,
    DEFAULT_CODE_BASE_PROMPT,
    DEFAULT_CODE_IMPROVEMENT_PROMPT,
    DEFAULT_README_PROMPT,
)
from repository_parser import RepositoryParser
from utils.logger import setup_logger

CONFIG_PATH: str = "configs.yaml"
MAX_FILE_SIZE_MB: float = 10.0

logger = setup_logger(__name__)


def generate_fn(
    input_text: Optional[str],
    input_file: Optional[gr.FileData],
    parsed_repository_tree: Optional[str],
    parsed_repository_content: Optional[str],
    additional_prompt: str,
    input_type: Optional[str],
    output_type: Optional[str],
) -> Tuple[str, Any]:
    """Generates content based on user input and configurations.

    Args:
        input_text: The text input from the Gradio interface.
        input_file: The file input from the Gradio interface.
        parsed_repository_tree:
            GitHub repository directory structure parsed as a txt input.
        parsed_repository_content: GitHub repository content parsed as a txt input.
        additional_prompt: Additional instructions from the user.
        input_type: The type of the input content.
        output_type: The desired output content type.

    Returns:
       A tuple containing generated text output and UI update dictionary.
    """
    # Input validation
    if not input_type:
        raise gr.Error("Choose an input type")

    if not output_type:
        raise gr.Error("Choose an output type")

    if (
        not input_text
        and not input_file
        and not (parsed_repository_tree and parsed_repository_content)
    ):
        raise gr.Error("Provide an input file (text, repository or file)")

    # Ensure only one input is provided
    if (
        sum(
            map(
                bool,
                [
                    input_text,
                    input_file,
                    (parsed_repository_tree or parsed_repository_content),
                ],
            )
        )
        > 1
    ):
        raise gr.Error("Provide only a single input (text, repository or file)")

    prompt = f"Create a {output_type} based on this {input_type} input."
    logger.info(f"Base prompt:\n{prompt}")

    output: str = ""

    if parsed_repository_tree and parsed_repository_content:
        # Combine repository info with additional prompt
        prompt = (
            f"{parsed_repository_tree}\n{parsed_repository_content}\n",
            f"{prompt}\n{additional_prompt}",
        )

        gr.Info("Counting prompt token count...")
        token_count = geminiClient.count_tokens(prompt)
        gr.Info(f"Prompt had {token_count} tokens")

        gr.Info("Generating output...")
        output = geminiClient.generate_content(prompt)

    elif input_file:
        # For file input, use the file content in the prompt
        prompt = f"{prompt}\n{additional_prompt}"

        gr.Info("Uploading file...")
        file_upload = geminiClient.upload_file(input_file.name)

        gr.Info("Counting prompt token count...")
        token_count = geminiClient.count_tokens(prompt, file_upload)
        gr.Info(f"Prompt had {token_count} tokens")

        gr.Info("Generating output...")
        output = geminiClient.generate_content(prompt, file_upload)

    elif input_text:
        # For text input, use the provided text in the prompt
        prompt = f"{prompt}\n{additional_prompt}\n{input_text}"

        gr.Info("Counting prompt token count...")
        token_count = geminiClient.count_tokens(prompt)
        gr.Info(f"Prompt had {token_count} tokens")

        gr.Info("Generating output...")
        output = geminiClient.generate_content(prompt)

    gr.Info("Output generated")
    logger.info("Output generated")

    return [output, gr.Row(visible=True)]


def iterate_fn(prompt: str, additional_prompt: str) -> str:
    """Generates content iteratively based on the previous output
        and additional instructions.

    Args:
        prompt: The previous output or base prompt.
        additional_prompt: Additional instructions for the iteration.

    Returns:
       The generated text output.
    """
    # Input validation
    if not prompt:
        raise gr.Error("Input prompt is empty")

    if not additional_prompt:
        raise gr.Error("Iteration prompt is empty")

    prompt = f"{prompt}\n{additional_prompt}"

    gr.Info("Counting prompt token count...")
    token_count = geminiClient.count_tokens(prompt)
    gr.Info(f"Prompt had {token_count} tokens")

    gr.Info("Generating output...")
    output = geminiClient.generate_content(prompt)
    gr.Info("Output generated")

    return output


def parse_repository_fn(
    input_repository_path: str,
    max_file_size: float = MAX_FILE_SIZE_MB,
    include_patterns: Optional[str] = None,
    exclude_patterns: str = ".*",
) -> Tuple[str, str, str]:
    """Parses a git repository and extracts its structure and content.

    Args:
        input_repository_path: Path or URL to the repository.
        max_file_size: The maximum size of files to include (in MB).
        include_patterns: File patterns to include during parsing.
        exclude_patterns: File patterns to exclude during parsing.

    Returns:
        A tuple containing the repository summary, directory tree, and file contents.
    """
    # Convert max file size to bytes
    max_file_size_bytes = int(max_file_size * 1024 * 1024)
    gr.Info("Parsing repository")
    summary, tree, content = repositoryParser.parse_repository(
        input_repository_path,
        max_file_size_bytes,
        include_patterns,
        exclude_patterns,
    )
    gr.Info("Parsing finished")

    return summary, tree, content


def base_prompt_fn(output_type: str, prompt: str) -> str:
    """Returns a base prompt string based on the selected output type.

    Args:
        output_type: The type of output to generate (e.g., README, code improvement).
        prompt: The current prompt (used if no specific base prompt is available).

    Returns:
        The appropriate base prompt.
    """
    # Return the corresponding default prompt based on output type
    if output_type == ContentOutputType.README.value:
        return DEFAULT_README_PROMPT.strip()
    elif output_type == ContentOutputType.CODE_IMPROVEMENT.value:
        return DEFAULT_CODE_IMPROVEMENT_PROMPT.strip()
    elif output_type == ContentOutputType.CODE_BASE.value:
        return DEFAULT_CODE_BASE_PROMPT.strip()
    elif output_type == ContentOutputType.BLOG_POST.value:
        return DEFAULT_BLOG_POST_PROMPT.strip()
    else:
        # If no specific prompt is found, return the current prompt
        return prompt


def show_markdown_fn(content: str, btn: str) -> Tuple[Dict[str, Any], str]:
    """Toggles the visibility of a markdown component for displaying generated content.

    Args:
        content: The generated content to display.
        btn: The current text of the toggle button.

    Returns:
        A tuple with the updated markdown component and the new button text.
    """
    # Toggle markdown visibility based on button text
    if btn == "Show the markdown version":
        btn_text = "Hide the markdown version"
        markdown = gr.Markdown(
            value=content,
            visible=True,
        )
    else:
        if not content:
            gr.Info("Generated content is empty")
        btn_text = "Show the markdown version"
        markdown = gr.Markdown(visible=False)

    return [markdown, btn_text]


# Gradio app
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Row():
                gr.Markdown("# Provide as input a file or a GitHub repository")

            with gr.Column(scale=1):
                with gr.Row():
                    with gr.Column(scale=1):
                        input_text = gr.Textbox(
                            label="Input option 1: Provide a text content as input",
                            lines=23,
                        )

                    with gr.Column(scale=1):
                        input_file = gr.File(
                            label="Input option 2: Select a file to upload",
                            file_count="single",
                        )

                        input_repository_path = gr.Textbox(
                            label=(
                                "Input option 3: "
                                "Provide a URL or path to a repository and parse it"
                            )
                        )

                        with gr.Accordion("Parsing params", open=False):
                            max_file_size = gr.Slider(
                                0.01,
                                100,
                                value=1.0,
                                step=0.1,
                                interactive=True,
                                label="Include files under (MB)",
                            )
                            include_patterns = gr.Textbox(
                                label="Include patterns (e.g.: README.md, src/, *.py)"
                            )
                            exclude_patterns = gr.Textbox(
                                label=(
                                    "Exclude patterns ",
                                    "(e.g.: LICENSE, assets/, *.toml, .*)",
                                )
                            )

                        with gr.Accordion("Parsed output", open=False):
                            input_summary_txt = gr.Textbox(label="Summary", lines=4)
                            input_tree_txt = gr.Textbox(
                                label="Tree", lines=10, show_copy_button=True
                            )
                            input_content_txt = gr.Textbox(
                                label="Content", lines=20, show_copy_button=True
                            )

                        parse_repository_btn = gr.Button("Parse GitHub repository")
                        parse_repository_btn.click(
                            fn=parse_repository_fn,
                            inputs=[
                                input_repository_path,
                                max_file_size,
                                include_patterns,
                                exclude_patterns,
                            ],
                            outputs=[
                                input_summary_txt,
                                input_tree_txt,
                                input_content_txt,
                            ],
                        )

    with gr.Row():
        additional_prompt = gr.Textbox(
            label="Additional prompt information",
            info="Describe the kind of content that you want to generate",
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
            radio_output_type.change(
                base_prompt_fn,
                [radio_output_type, additional_prompt],
                additional_prompt,
            )

    with gr.Row(visible=False) as content_row:
        with gr.Column(scale=1):
            generated_content = gr.Textbox(
                label="Generated content",
                interactive=True,
                show_copy_button=True,
            )

            generated_content_markdown = gr.Markdown(visible=False)

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
        with gr.Column(scale=5):
            generate_content_btn = gr.Button("Generate content")
            generate_content_btn.click(
                fn=generate_fn,
                inputs=[
                    input_text,
                    input_file,
                    input_tree_txt,
                    input_content_txt,
                    additional_prompt,
                    radio_input_type,
                    radio_output_type,
                ],
                outputs=[generated_content, content_row],
            )

        with gr.Column(scale=1):
            show_markdown_btn = gr.Button("Show to markdown version")
            show_markdown_btn.click(
                fn=show_markdown_fn,
                inputs=[generated_content, show_markdown_btn],
                outputs=[generated_content_markdown, show_markdown_btn],
            )

if __name__ == "__main__":
    # Load configurations
    app_configs = load_config(CONFIG_PATH)
    if not app_configs:
        exit()

    # Load environment variables
    load_dotenv()

    # Initialize the appropriate Gemini client based on configuration
    if app_configs["llm_model_configs"]["provider"] == "ai_studio":
        geminiClient = AIStudioGeminiClient(app_configs["llm_model_configs"])
        logger.info("Using AI Studio configuration")
    elif app_configs["llm_model_configs"]["provider"] == "vertex_ai":
        geminiClient = VertexAIGeminiClient(
            app_configs["llm_model_configs"],
            app_configs["vertex_ai"],
        )
        logger.info("Using Vertex AI configuration")
    else:
        raise gr.Error("Invalid configs: 'provider' must be 'ai_studio' or 'vertex_ai'")

    # Check if a public URL should be generated
    if app_configs["generate_public_url"]:
        logger.info("App generated a public shareable link, check logs for the URL")

    # Initialize the RepositoryParser
    repositoryParser = RepositoryParser()

    # Launch the Gradio app
    demo.launch(share=app_configs["generate_public_url"])
