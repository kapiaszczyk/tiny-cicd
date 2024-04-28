"""Service part for the tiny CI/CD system"""

import os
import git
import subprocess
import docker
import shutil
import json

from tiny_cicd_logger import Logger

# deployments_dir = os.getenv('DEPLOYMENTS_DIR')
deployments_dir = "/deployments"

logger = Logger("tiny-cicd")


class TinyCICDService:
    """Tiny CI/CD service class."""

    def __init__(self):
        self.status = "IDLE"
        self.repo_name = ""
        self.repo_directory = ""
        self.repo_url = ""
        self.project_type = ""
        self.pipeline_dir = os.getcwd()
        self.deployments = deployments_dir

        
    def to_json(self):
        data = {
            "status": self.status,
            "repo_name": self.repo_name,
            "repo_directory": self.repo_directory,
            "repo_url": self.repo_url,
            "project_type": self.project_type,
            "pipeline_dir": self.pipeline_dir,
            "deployments": self.deployments
        }
        return json.dumps(data)


    def get_status(self):
        """Get CI/CD pipeline status."""
        return self.status
    

    def get_pipeline_details(self):
        return f"Status: {self.status}, Repo name: {self.repo_name}, Repo type: {self.project_type}, Working dir: {self.pipeline_dir}"


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

        self.test_code()

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

        self.run_tests_in_docker_container()

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
    

    def run_tests_in_docker_container(self):
        """Runs testing suite in a sibling container"""

        image_tag = self.build_test_image()

        if not image_tag:
            logger.log("Failed to build Docker image. Aborting.")
            return  

        client = docker.from_env()

        try:
            container = client.containers.run(
                image=image_tag,
                detach=True,
            )

            result = container.wait()
            container.remove()

            exit_code = result["StatusCode"]
            
            if exit_code == 0:
                logger.log("Tests passed")
            else:
                logger.log("Tests failed")
        except docker.errors.ContainerError as e:
            logger.log(f"Error running tests in Docker container: {e}")
        except docker.errors.ImageNotFound as e:
            logger.log(f"Docker image not found: {e}")
        except Exception as e:
            logger.log(f"An unexpected error occurred: {e}")

        self.cleanup_after_tests(client, image_tag)
    

    def build_java_test_image(self):
        """Creates a container for testing Java applications."""
        return True
    

    def build_dotnet_test_image(self):
        """Creates a container for testing .NET applications."""
        return True


    def build_test_image(self):
        """Builds a Docker image for testing Python applications."""

        logger.log("Building a docker image")

        image_tag = f"testrunner-{self.repo_name}".lower()

        filename = "Dockerfile"

        # Check if project directory contains a Dockerfile and remove it if it does
        # A Dockerfile will clash with the test image
        source_path = os.path.join((self.pipeline_dir + "/test-runner/" + self.project_type.lower()), filename)
        destination_path = os.getcwd()

        if os.path.exists(destination_path + "/Dockerfile") :
            os.remove((destination_path + "/Dockerfile"))
        shutil.copy(source_path, destination_path)
        print(f"File '{filename}' copied successfully from '{source_path}' to '{destination_path}'.")

        docker_build_cmd = [
            "docker", "build",
            "-t", image_tag,    
            "."
        ]

        try:
            subprocess.check_call(docker_build_cmd)
            print(f"Successfully built Docker image: {image_tag}")
            return image_tag
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image: {e}")
            return None
    

    def build_go_test_image(self):
        """Creates a container for testing Go applications."""
        return True

    def cleanup_after_tests(self, docker_client, image_tag):

        client = docker_client

        try:
            image = client.images.get(image_tag)
            client.images.remove(image.id)

            print(f"Successfully removed Docker image: {image_tag}")
            return True
        except docker.errors.ImageNotFound:
            print(f"Docker image not found: {image_tag}")
            return False
        except Exception as e:
            print(f"An error occurred while removing Docker image: {e}")
            return False