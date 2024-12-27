import logging
import os

from google import genai
from google.genai import types

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_gemini_client(api_key=None):
    """Sets up the Gemini API client.

    Args:
        api_key: The API key for Gemini API (optional).

    Returns:
       The Gemini API client object.
    """
    if not api_key:
        api_key = os.environ["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)


def upload_file(client, file_path):
    """Uploads a file to the Gemini API.

    Args:
        client: The Gemini API client.
        file_path: The path to the file to upload.

    Returns:
        The file upload object from the API.
    """
    file_upload = client.files.upload(path=file_path)
    return file_upload


def count_tokens(client, prompt, file_upload, model_id):
    """Counts the number of tokens in a prompt including file content.

    Args:
        client: The Gemini API client.
        prompt: The text prompt.
        file_upload: The file upload object.
        model_id: The ID of the Gemini model.

    Returns:
        The total number of tokens.
    """
    response = client.models.count_tokens(
        model=model_id,
        contents=[
            types.Content(
                parts=[
                    types.Part.from_uri(
                        file_uri=file_upload.uri, mime_type=file_upload.mime_type
                    ),
                ]
            ),
            prompt,
        ],
    )

    return response.total_tokens


def generate_content(client, prompt, file_upload, model_id, generation_config):
    """Generates content using the Gemini API.

    Args:
        client: The Gemini API client.
        prompt: The text prompt.
        file_upload: The file upload object.
        model_id: The ID of the Gemini model.
        generation_config: Configuration for content generation.

    Returns:
        The generated text output.
    """
    response = client.models.generate_content(
        model=model_id,
        config=types.GenerateContentConfig(
            temperature=generation_config["temperature"],
            top_p=generation_config["top_p"],
            top_k=generation_config["top_k"],
            max_output_tokens=generation_config["max_output_tokens"],
        ),
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_uri(
                        file_uri=file_upload.uri, mime_type=file_upload.mime_type
                    ),
                ],
            ),
            prompt,
        ],
    )

    return response.text


def iterate_content(client, prompt, model_id, generation_config):
    """Generates content using the Gemini API.

    Args:
        client: The Gemini API client.
        prompt: The text prompt.
        model_id: The ID of the Gemini model.
        generation_config: Configuration for content generation.

    Returns:
        The generated text output.
    """
    response = client.models.generate_content(
        model=model_id,
        config=types.GenerateContentConfig(
            temperature=generation_config["temperature"],
            top_p=generation_config["top_p"],
            top_k=generation_config["top_k"],
            max_output_tokens=generation_config["max_output_tokens"],
        ),
        contents=[prompt],
    )

    return response.text


def build_prompt(input_type, output_type):
    """Builds a base prompt based on input and output types.

    Args:
        input_type: The type of the input content.
        output_type: The desired output content type.

    Returns:
        The generated base prompt.
    """
    prompt = f"Create a '{output_type}' based on this '{input_type}' file input."
    return prompt
