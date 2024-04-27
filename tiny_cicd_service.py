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
        self.project_type = ""


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

        self.project_type = self.detect_project_type()

        self.status = "IDLE"

        self.test_code

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

        self.status = "RUNNING TESTS"

        logger.log("Running tests", "info")

        return None


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
        """Checks if given directory contains a git repository."""
        try:
            _ = git.Repo(path).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False


    def detect_project_type(self):
        """Detects the type of the project."""

        self.status = "DETECTING PROJECT TYPE"

        if self.is_maven_project() is True:
            return "MAVEN"
        elif self.is_dotnet_project() is True:
            return "DOTNET"
        elif self.is_python_project() is True:
            return "PYTHON"
        elif self.is_go_project() is True:
            return "GO"
        else:
            return "UNSUPPORTED"


    def is_maven_project(self):
        """Check if project is a Maven project (checks for pom.xml file)."""
        pom_xml_path = os.path.join(self.repo_directory, "pom.xml")
        return os.path.exists(pom_xml_path)


    def is_dotnet_project(self):
        """Check if project is a .NET project (checks for .csproj file)."""
        for filename in os.listdir(self.repo_directory):
            if filename.endswith(".csproj") or filename.endswith(".cs"):
                return True
        return False 
    

    def is_python_project(self):
        """Check if project is a Python project (checks for requirements.txt file)"""
        requirements_txt_path = os.path.join(self.repo_directory, "requirements.txt")
        setup_py_path = os.path.join(self.repo_directory, "setup.py")
        return os.path.exists(requirements_txt_path) or os.path.exists(setup_py_path)
    

    def is_go_project(self):
        """Check if project is a Go project (checks for go.mod file)"""
        go_mod_path = os.path.join(self.repo_directory, "go.mod")
        return os.path.exists(go_mod_path)
