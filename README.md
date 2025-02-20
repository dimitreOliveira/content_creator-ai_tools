# Content Creator AI Tools

This application provides an AI-powered solution for generating different types of technical content, such as blog posts, README files, code improvements, and video walkthroughs, based on provided inputs.
It can process either regular text, local files or GitHub repositories to serve as context for content generation. The purpose of this tool is to streamline the content creation process using the power of AI models.

I have also written a blog post about this project, make sure to check "[Supercharge Your Technical Content Creation with Gemini](https://medium.com/google-developer-experts/supercharge-your-technical-content-creation-with-gemini-5311af82d807)"!
---

The current iteration of this applicaiton leverages Gemini through the [Google AI studio](https://aistudio.google.com/) and [Vertex AI](https://cloud.google.com/vertex-ai) API to generate content.

**Supported input types**
- Blog post
- Code

**Supported output types**
- Blog post
- GitHub README.md file
- Code base
- Code improvement
- Video walkthrough

## How it works

![](./assets/diagram.jpg)

The application provides a user-friendly interface built with Gradio. You can input text, a file or a repository path, specify the input and output content types, and provide additional instructions. The application then uses the Gemini AI model to generate the desired content.

1. Select the type of the input content in the "Input type" dropdown.
2. Choose the desired output content type from the "What kind of content would you like to create?" dropdown.
3. Provide an input of one of the supported options below.
    1. Providing a GitHub Repository: Enter the URL or local path of a Git repository in the "Provide a URL or path to a local repository" textbox.
    2. Providing a Text: Enter a text at the "Provide a text content as input" textbox.
    3. Providing a File: Upload a single file using the "Select a file to upload" section.
4. If a repository is provided, optionally add parameters on how to parse the repository.
5. If a repository is provided, the application parses the repository structure, summarize its contents, and extract individual file contents.
6. Optionally, add specific instructions or context in the "Additional prompt information" field.
7. Click the "Generate content" button.
8. The generated content will be displayed in the "Generated content" textbox.
9. You can further refine the generated content by adding instructions in the "Keep iterate over the content" field and clicking "Iterate over the content".

## Setup

### Prerequisites

1. **Clone the repository:**
```bash
git clone https://github.com/dimitreOliveira/content_creator-ai_tools.git
cd content_creator-ai_tools
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv content_creator_ai_tools
source content_creator_ai_tools/bin/activate
```

3. **Install the dependencies:**
```bash
make build
```
Alternatively, you can use `pip`:
```bash
pip install -r requirements.txt
```

4.1 **Set up the local permission:**

#### If If you are using [Google AI studio](https://aistudio.google.com/) as the provider.

-   Obtain an API key from [Google AI studio](https://aistudio.google.com/).
-   Set the `GEMINI_API_KEY` environment variable with your API key. You can do this by adding the following line to your `.bashrc`, `.zshrc`, or similar shell configuration file:
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
```
Or, you can create a `.env` file in the root directory with the following content (recommended):
```
GEMINI_API_KEY=YOUR_API_KEY
```
If using a .env file, ensure you have python-dotenv installed (it should be if you ran make build).

#### If you are using [Vertex AI](https://cloud.google.com/vertex-ai) as the provider.

Make sure that your project [supports Vertex AI](https://cloud.google.com/vertex-ai/docs/start/cloud-environment#console) then [login with the local SDK](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
```bash
gcloud auth application-default login
```

## Usage (Makefile Commands)

The Makefile provides convenient commands for common tasks:

- Runs the Gradio application, then you can access in your web browser, link will be at the logs.
```bash
make app
```

- Installs the required dependencies to run the app.
```bash
make build
```

- Runs linting and formatting tools (isort, black, flake8, mypy) to ensure code quality and consistency.
```bash
make lint
```

## Examples

### Example 1: Generating a Blog Post from a Code Script
1.  Select "Code" as the input type.
2.  Select "Blog post" as the output type.
3.  Upload a Python script containing code.
4.  Provide additional instructions such as "Summarize the code and describe its functionality" in the prompt section.
5.  Click on "Generate content".

![](./assets/example-file_input.png)

### Example 2: Creating a README from a GitHub Repository
1.  Select "Code base" as the input type.
2.  Select "GitHub README.md file" as the output type.
3.  Enter the URL or local path of the GitHub repository to parse.
4.  Click on "Parse GitHub repository" to fetch repository summary, tree structure, and file content.
5.  Provide additional instructions such as "Explain how to set up the environment and run the app" in the prompt section.
6.  Click on "Generate content".

![](./assets/example-repository_input.png)

### Example 3: Creating a Video Walkthrough from a Blog Post
1.  Select "Blog post" as the input type.
2.  Select "Video walkthrough" as the output type.
3.  Input the blog post into the "Input text field".
4.  Provide additional instructions such as "The video walkthrough must be engaging and suited for short content" in the prompt section.
5.  Click on "Generate content".

![](./assets/example-text_input.png)

## Configs

The application's behavior can be configured using the `configs.yaml` file.

The application supports both AI Studio and Vertex AI. Edit the `configs.yaml` file to select your preferred provider.

```yaml
generate_public_url: false # Set to true to generate a public shareable link
llm_model_configs:
    provider: ai_studio # One of [ai_studio, vertex_ai]
    model_id: gemini-2.0-pro-exp-02-05 # Or any other supported model
    generation_config:
        temperature: 0.7
        top_p: 0.95
        top_k: 40
        max_output_tokens: 10000
vertex_ai:  # Only needed if provider is "vertex_ai"
    project: "{your-gcp-project-id}"
    location: "{your-gcp-project-location}"
```

* **`generate_public_url`**: If the app will generate a public shareable link, if `true`, check logs for the URL (Gradio public URLs expires after 72 hours).
*   **`llm_model_configs`:**
    *   **`provider`:**  Specifies the Gemini API provider: `"ai_studio"` or `"vertex_ai"`.
    *   **`model_id`:** The ID of the Gemini model to use (e.g., `"gemini-2.0-flash-exp"`).
    *   **`generation_config`:** Parameters to control the content generation process.
        *   **`temperature`:** Controls the randomness of the output (0.0 is deterministic, 1.0 is most random).
        *   **`top_p`:**  Controls the diversity of the output (nucleus sampling).
        *   **`top_k`:**  Controls the diversity of the output (top-k sampling).
        *   **`max_output_tokens`:** The maximum number of tokens to generate.
*   **`vertex_ai`:** (Only required if `provider` is `"vertex_ai"`)
    *   **`project`:** Your Google Cloud project ID.
    *   **`location`:** The Google Cloud region (e.g., `"us-central1"`).

## Contributing

Contributions to this project are welcome! Feel free to fork the repository, make changes, and submit a pull request. Before submitting, please ensure your code passes the linting checks by running:
```bash
make lint
```

## Disclaimers and Acknowledgements
- Google Cloud credits are provided for this project as part of the #VertexAISprint
- This application utilizes external APIs (like Google Gemini) which may have their own terms of service and usage limitations.
- The quality of the generated content depends on the input provided and the capabilities of the underlying AI model.
- Ensure you have the necessary permissions and comply with the terms of service for the underlying AI model.
- The application is for informational and creative purposes. Always review and verify the generated content before using it.

## References
- [Google Gen AI SDK [Docs]](https://googleapis.github.io/python-genai)
- [Google Gen AI SDK [GitHub]](https://github.com/googleapis/python-genai)

## TODO (not in any particular order)
- Add support to add multiple files to the prompt in any order (e.g. [file, text], [file, text, file, file], etc)
- Add support for local open-source models
- Add support to TTS audio generation
- Add support to image generation
    - create a set X of optional illustrations for content
- Add support to video generation
    - create a set X of optional videos for content