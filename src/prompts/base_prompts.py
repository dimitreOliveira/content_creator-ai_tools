DEFAULT_README_PROMPT = (
    "The readme must start with a summary of the app, what it does, and its purpose.\n"
    "Create sections for 'How to use', 'Examples', 'Usage', 'Setup', "
    "and 'App workflow'.\n"
    "Also, add explanations about the configs and the Makefile commands.\n"
    "Use placeholders for the screenshots and architecture diagrams.\n"
    "Add disclaimers if necessary."
)

DEFAULT_CODE_IMPROVEMENT_PROMPT = (
    "Refactor this code by fixing any existing bug or by "
    "adding any relevant performance update.\n"
    "Add documentation and typing to all the relevant places.\n"
    "Make sure that the code uses the best practices.\n"
    "Outline with comments in the code the modification made.\n"
    "Only output the actual code, not the code diffs."
)

DEFAULT_CODE_BASE_PROMPT = (
    "The code base must be object-oriented and "
    "make sure that the code uses the best practices.\n"
    "Whenever necessary split the code into different files.\n"
    "Create a `configs.json` file with all the necessary "
    "configuration parameters to run the project.\n"
    "Create a `requirements.txt` file with all necessary dependencies."
)

DEFAULT_BLOG_POST_PROMPT = (
    "The blog post must start with an engaging introduction "
    "about why its content is relevant.\n"
    "Follow the introduction with a brief overview summary of its content.\n"
    "The blog post should describe the main parts of the input "
    "step by step in an engaging way.\n"
    "For the step-by-step description, when relevant, "
    "paste some code pieces from the source.\n"
    "By the end add some closing thoughts and a conclusion summarizing the content.\n"
    "If it makes sense add suggestions for the next steps."
)
