"""Service part for the tiny CI/CD system"""

import os
import git
import subprocess
from tiny_cicd_logger import Logger

deployments_dir = os.getenv('DEPLOYMENTS_DIR')

logger = Logger("tiny-cicd")


class TinyCICDService:
    """Tiny CI/CD service class."""

    def __init__(self):
        self.status = "IDLE"
        self.repo_name = ""
        self.repo_directory = ""
        self.repo_url = ""


    def get_status(self):
        """Get CI/CD pipeline status."""
        return self.status


    def trigger_pipeline(self, url):
        """Trigger the CI/CD pipeline."""

        self.status = "STARTING"

        logger.log("Pipeline triggered", "info")
        logger.log(f"Url is {url}", "info")
        logger.log(f"deployments_dir is {deployments_dir}", "info")

        self.repo_url = url
        self.repo_name = self.resolve_repository_name(url)
        self.repo_directory = deployments_dir + "/" + self.repo_name

        if self.is_repo_cloned(url) is True:
            self.pull_code(url)
        else:
            self.clone_repository(url)
            self.pull_code(url)

        self.status = "IDLE"

    def clone_repository(self, url):
        """Clone repository from GitHub"""

        self.status = "CLONING REPOSITORY"

        logger.log("Cloning code from the repository", "info")

        os.chdir(deployments_dir)
        subprocess.check_call(["git", "clone", url])


    def pull_code(self, url):
        """Pull code from GitHub."""

        self.status = "PULLING CODE"
        
        logger.log("Pulling code from the repository", "info")

        os.chdir(self.repo_directory)
        subprocess.check_call(["git", "pull", url])



    def test_code(self):
        """Test code."""


    def build_image(self):
        """Build Docker image."""


    def is_git_repo(self):
        """Check if the current directory is a git repository."""

    def is_repo_cloned(self, url):
        """Check if provided directory exists and/or create it"""

        logger.log("Checking if repository is cloned", "info")

        if not os.path.exists(deployments_dir):
            logger.log("Deployement directory does not exist", "info")
            logger.log("Creating directory repository", "info")
            os.makedirs(deployments_dir)
            self.is_repo_cloned(url)
        if os.path.exists(self.repo_directory):
            logger.log("Deployement directory exists", "info")
            logger.log(f"Checking for repository in {self.repo_directory}", "info")
            if self.is_git_repo(self.repo_directory):
                logger.log(f"Repository is cloned", "info")
                return True
            else:
                logger.log(f"Repository is not cloned but {self.repo_directory} exists", "info")
                logger.log(f"Deleting {self.repo_directory}")
                os.rmdir(self.repo_directory)
                return False
        else:
            logger.log("Repository is not cloned", "info")
            return False

    def resolve_repository_name(self, url):
        """Get repository name from the git repository url."""
        logger.log("Resolving repository name", "info")
        if url.endswith(".git"):
            name = url[:-4].split("/")[-1]
            logger.log(f"Name resolved to {name}", "info")
            return name
        else:
            name = url.split("/")[-1]
            logger.log(f"Name resolved to {name}", "info")
            return name
        
    def is_git_repo(self, path):
        try:
            _ = git.Repo(path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False
