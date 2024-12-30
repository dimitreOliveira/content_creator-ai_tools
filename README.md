# Creator AI Tools

This application provides an AI-powered solution for generating different types of content, such as blog posts, README files, code improvements, and video walkthroughs, based on provided inputs. It can process either local files or GitHub repositories to serve as context for content generation. The purpose of this tool is to streamline the content creation process using the power of AI models.

## How to Use

This application provides a Gradio interface with two main content generation workflows:
1.  **File Upload**: Users can upload a file, then specify the input and output content types. An AI model will then generate content according to that input.
2.  **GitHub Repository**: Users can input a repository path and parse the project's content. An AI model will then generate content using the repository's directory structure and file content as context.

## Examples

### Example 1: Generating a Blog Post from a Code Script
1.  Select "Code" as the input type.
2.  Select "Blog post" as the output type.
3.  Upload a Python script containing code.
4.  Provide additional instructions such as "Summarize the code and describe its functionality" in the prompt section.
5.  Click on "Generate content."

### Example 2: Creating a README for a GitHub Repository
1.  Enter the URL or local path of the GitHub repository to parse.
2.  Click on "Parse GitHub repository" to fetch repository summary, tree structure, and file content.
3.  Select "Code base" as the input type.
4.  Select "GitHub README.md file" as the output type.
5.  Provide additional instructions such as "Explain how to set up the environment and run the app" in the prompt section.
6.  Click on "Generate content."

## Usage

### Interface Elements
*   **File Input:** Allows users to upload a file that serves as the basis for the content generation.
*   **Repository Path:** Allows users to input a path to a repository to parse.
*   **Parsing Parameters:**
    *   **Max File Size:** Filters out any files bigger than this size, in MB.
    *   **Include Patterns:** Includes files matching these patterns (e.g.: `README.md, src/, *.py`).
    *   **Exclude Patterns:** Excludes files matching these patterns (e.g.: `LICENSE, assets/, *.toml, .*`).
*   **Parsed Output:**
    *   **Summary:** Text summary of the parsed repository
    *   **Tree:** Directory structure of the repository.
    *   **Content:** Content of all files in the repository.
*   **Input Type:** Specifies the type of content to process: "Blog post" or "Code".
*   **Output Type:** Specifies the type of content to generate: "Blog post," "GitHub README.md file", "Code base", "Code improvement," or "Video walkthrough."
*   **Additional Prompt Information:** Provides a space for users to provide further instructions for the content generation.
*   **Generated Content:** Output of the AI content generation.
*   **Iterate over the content:** Option to perform additional iterations over the created content.

### Workflow

1.  **Select Input**: Choose whether to use a local file upload or a GitHub repository.
2.  **Parse Repository (Optional)**: If using a GitHub repository, input the path and click "Parse GitHub repository".
3.  **Specify Content Types**: Select the input type and desired output type.
4.  **Additional Prompt**: Enter any additional instructions to guide the AI model.
5.  **Generate Content**: Click the "Generate content" button.
6.  **Review and Iterate**: Review the generated content, and iterate if needed using the "Iterate over the content" section.

## Setup

### Prerequisites

*   Python 3.8+
*   pip
*   A Google Gemini API key (set as `GEMINI_API_KEY` in your environment variables)

### Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```
2.  Install the requirements:
    ```bash
    make build
    ```
3.  Copy `configs.yaml` to your working directory.

### Running the Application
   Run the application using the following command:
    ```bash
    make app
    ```

## App Workflow

The application workflow is designed as follows:

1.  **Configuration Loading**: Loads configurations from the `configs.yaml` file.
2.  **Environment Setup**: Loads environment variables from the `.env` file using python-dotenv.
3.  **Client Initialization**:
    *   Initializes the Gemini client using the loaded API key and settings in `config.yaml`.
    *   Initializes the repository parser.
4.  **Gradio Interface**:
    *   Launches the Gradio interface with the specified input and output fields.
    *   Provides functionalities to parse repositories and generate content using the AI model based on user input.
5.  **Content Generation**:
    *   The `generate_fn` function is triggered when the user clicks on "Generate content," performing the following steps:
        *   Checks input validations.
        *   Builds a prompt using the provided content.
        *   Uploads files to the Gemini API.
        *   Counts tokens.
        *   Generates content using the AI model.
        *   Returns the output to the Gradio interface.
6.  **Content Iteration**:
    *   The `iterate_fn` function is triggered when the user clicks on "Iterate over the content," performing the following steps:
        *   Checks input validations.
        *   Builds a prompt using the generated text and the user input.
        *   Counts tokens.
        *   Generates content using the AI model.
        *   Returns the output to the Gradio interface.
7. **Repository Parsing**:
    * The `parse_repository_fn` function is triggered when the user clicks on "Parse GitHub repository," performing the following steps:
        * Parses the directory tree, the summary and the content from the given repository.
        * Returns the parsed output to the Gradio interface.


## Configurations

### `configs.yaml`
The `configs.yaml` file contains the following configuration parameters:

*   **`ai_studio` or `vertex_ai`**: Contains AI provider specific configurations.
    *   **`model_id`**: Specifies the model to use (e.g., `gemini-2.0-flash-exp`).
    *   **`generation_config`**: Contains generation settings, such as `temperature`, `top_p`, `top_k`, and `max_output_tokens`.

## Makefile Commands

The Makefile provides shortcuts for common operations:

*   **`make app`**: Launches the Gradio app.
*   **`make build`**: Installs the required Python packages from `requirements.txt`.
*   **`make lint`**: Runs code formatting and linting tools (`isort`, `black`, `flake8`, `mypy`) to ensure code quality.

## Disclaimers

*   The generated content may not always be perfect and might require manual review.
*   Please ensure you have the necessary permissions to use the provided API keys.
*   Token limits may apply when generating content.
*   [Add placeholder for architecture diagram here]
*   [Add placeholder for screenshots here]