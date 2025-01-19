BASE_README_PROMPT = """
The readme must start with a summary of the app, what it does, and its purpose.
Create sections for "How to use", "Examples", "Usage", "Setup", "App workflow"
Also, add explanations about the configs and the Makefile commands.
Use placeholders for the screenshots and architecture diagrams.
Add disclaimers if necessary.
"""

BASE_CODE_IMPROVEMENT_PROMPT = """
Refactor this code by fixing any existing bug or by adding any relevant performance update.
Add documentation and typing to all the relevant places.
Make sure that the code uses the best practices.
"""

BASE_CODE_BASE_PROMPT = """
The code base must be object-oriented and make sure that the code uses the best practices.
Whenever necessary split the code into different files.
Create a `configs.json` file with all the necessary configuration parameters to run the project.
Create a `requirements.txt` file with all necessary dependencies.
"""
