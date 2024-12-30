from enum import Enum


class ContentInputType(Enum):
    BLOG_POST = "Blog post"
    CODE_SCRIPT = "Code"


class ContentOutputType(Enum):
    BLOG_POST = "Blog post"
    README = "GitHub README.md file"
    CODE_BASE = "Code base"
    CODE_IMPROVEMENT = "Code improvement"
    VIDEO_WALKTHROUGH = "Video walkthrough"
