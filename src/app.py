import logging
from enum import Enum

import gradio as gr
from dotenv import load_dotenv

from common import load_config
from utils import (
    build_prompt,
    count_tokens,
    generate_content,
    iterate_content,
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
    VIDEO_WALKTHROUGH = "Video walkthrough"


def generate_fn(file_input, additional_prompt, input_type, output_type):
    """Generates content based on user input and configurations.

    Args:
        file_input: The path to the input file.
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

    if not file_input:
        raise gr.Error("Provide and input file")

    prompt = build_prompt(input_type, output_type)
    logging.info(f"Base prompt:\n{prompt}")

    prompt = f"{prompt}\n{additional_prompt}"
    logging.info(f"Final prompt:\n{prompt}")

    file_upload = upload_file(client, file_input)
    logging.info(f"Uploaded file: {file_upload.uri}")

    logging.info("Counting prompt token count...")
    token_count = count_tokens(client, prompt, file_upload, client_configs["model_id"])
    logging.info(f"Prompt had {token_count} tokens")

    logging.info("Generating output...")
    output = generate_content(
        client,
        prompt,
        file_upload,
        client_configs["model_id"],
        client_configs["generation_config"],
    )
    logging.info("Output generated")

    return output


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
    logging.info(f"Iteration prompt:\n{prompt}")

    logging.info("Generating output...")
    output = iterate_content(
        client,
        prompt,
        client_configs["model_id"],
        client_configs["generation_config"],
    )
    logging.info("Output generated")

    return output


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

    # Build the Gradio app
    with gr.Blocks() as demo:

        with gr.Row():
            with gr.Column(scale=1, min_width=300):
                file_input = gr.File(
                    label="Select a file to upload", file_count="single"
                )

            with gr.Column(scale=2, min_width=300):
                radio_input_type = gr.Radio(
                    [x.value for x in list(ContentInputType)],
                    label="Input type",
                )

            with gr.Column(scale=2, min_width=300):
                radio_output_type = gr.Radio(
                    [x.value for x in list(ContentOutputType)],
                    label="What kind of content would you like to create?",
                )

        additional_prompt = gr.Textbox(
            label="Additional prompt information",
            info="Describe the kind of content that you want to generate",
        )

        with gr.Row():
            generated_content = gr.Textbox(label="Generated content")

        with gr.Row():
            generate_content_btn = gr.Button("Generate content")
            generate_content_btn.click(
                fn=generate_fn,
                inputs=[
                    file_input,
                    additional_prompt,
                    radio_input_type,
                    radio_output_type,
                ],
                outputs=generated_content,
            )

        with gr.Row():
            additional_steps = gr.Textbox(
                label="Keep iterate over the content",
                info="Describe what you want to modify over the content created",
            )

        with gr.Row():
            iterate_content_btn = gr.Button("Iterate over the content")
            iterate_content_btn.click(
                fn=iterate_fn,
                inputs=[
                    generated_content,
                    additional_steps,
                ],
                outputs=generated_content,
            )

    demo.launch()
