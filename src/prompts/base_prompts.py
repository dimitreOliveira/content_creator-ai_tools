DEFAULT_README_PROMPT = """
The readme must start with a summary of the app, what it does, and its purpose.
Create sections for "How to use", "Examples", "Usage", "Setup", "App workflow"
Also, add explanations about the configs and the Makefile commands.
Use placeholders for the screenshots and architecture diagrams.
Add disclaimers if necessary.
"""

DEFAULT_CODE_IMPROVEMENT_PROMPT = """
Refactor this code by fixing any existing bug or by adding any relevant performance update.
Add documentation and typing to all the relevant places.
Make sure that the code uses the best practices.
"""

DEFAULT_CODE_BASE_PROMPT = """
The code base must be object-oriented and make sure that the code uses the best practices.
Whenever necessary split the code into different files.
Create a `configs.json` file with all the necessary configuration parameters to run the project.
Create a `requirements.txt` file with all necessary dependencies.
"""

DEFAULT_BLOG_POST_PROMPT = """
The blog post must start with an engaging introduction about why its content is relevant.
Follow the introduction with a brief overview summary of its content.
The blog post should describe the main parts of the input step by step in an engaging way.
For the step-by-step description, when relevant, paste some code pieces from the source.
By the end add some closing thoughts and a conclusion summarizing the content.
If it makes sense add suggestions for the next steps.
"""
