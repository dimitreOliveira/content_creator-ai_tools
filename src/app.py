import logging

# import os
# import time
import gradio as gr
# import google.generativeai as genai
# from dotenv import load_dotenv
from enum import Enum

# from common import parse_configs

# CONFIGS_PATH = "configs.yaml"


class ContentInputType(Enum):
    BLOG_POST = "blog post"
    CODE_SCRIPT = "code script"


class ContentOutputType(Enum):
    BLOG_POST = "blog post"
    VIDEO_WALKTHROUGH = "video walkthrough"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# load_dotenv()

def create_prompt(input_type, output_type):
    prompt = f"Generate a '{output_type}' based on this '{input_type}'."
    return prompt


def generate_fn(file_input, prompt_content, input_type, output_type):
    if not input_type:
        raise gr.Error("Choose an input type")

    if not output_type:
        raise gr.Error("Choose an output type")

    if not file_input:
        raise gr.Error("Provide and input file")

    prompt = create_prompt(input_type, output_type)
    output = f"""
    Placeholder content generated
    Input file '{file_input}'
    Additional prompt information '{prompt_content}'
    Based on prompt '{prompt}'
    """
    return output


with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=2, min_width=300):
            file_input = gr.File(label="Select a file to upload", file_count="single")

        with gr.Column(scale=1, min_width=300):
            radio_input_type = gr.Radio(
                [x.value for x in list(ContentInputType)],
                label="Input type",
            )

        with gr.Column(scale=1, min_width=300):
            radio_output_type = gr.Radio(
                [x.value for x in list(ContentOutputType)],
                label="What kind of content would you like to create?",
            )

    prompt_content = gr.Textbox(
        label="Additional prompt information",
        info="Describe the kind of content that you want to generate",
    )

    generated_content = gr.Textbox(label="Generated content")
    generate_content_btn = gr.Button("Generate content")
    generate_content_btn.click(
        fn=generate_fn,
        inputs=(file_input, prompt_content, radio_input_type, radio_output_type),
        outputs=generated_content,
    )

demo.launch()
