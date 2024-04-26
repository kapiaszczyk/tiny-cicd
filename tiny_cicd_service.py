"""Service part for the tiny CI/CD system"""

import git
from tiny_cicd_logger import Logger

logger = Logger("tiny-cicd")


class TinyCICDService:
    """Tiny CI/CD service class."""

    def __init__(self):
        self.status = "IDLE"


    def get_status(self):
        """Get CI/CD pipeline status."""
        return self.status


    def trigger_pipeline(self, url):
        """Trigger the CI/CD pipeline."""


    def pull_code(self, url):
        """Pull code from GitHub."""


    def test_code(self):
        """Test code."""


    def build_image(self):
        """Build Docker image."""


    def is_git_repo(self):
        """Check if the current directory is a git repository."""
