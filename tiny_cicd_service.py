"""Service part for the tiny CI/CD system"""

import os
import git
import subprocess
import docker
import shutil
import json

from tiny_cicd_logger import Logger


deployments_dir = "deployments"
pipeline_dir = os.getcwd()

logger = Logger("tiny-cicd")


class TinyCICDService:
    """Tiny CI/CD service class."""

    def __init__(self):
        self.status = "IDLE"
        self.repo_name = ""
        self.repo_directory = ""
        self.repo_url = ""
        self.project_type = ""
        self.pipeline_dir = pipeline_dir
        self.deployment_dir = deployments_dir
        self.last_tag_number = ""


    def to_json(self):
        data = {
            "status": self.status,
            "repo_name": self.repo_name,
            "repo_directory": self.repo_directory,
            "repo_url": self.repo_url,
            "project_type": self.project_type,
            "pipeline_dir": self.pipeline_dir,
            "deployments": self.deployment_dir
        }
        return json.dumps(data)


    def get_status(self):
        """Get CI/CD pipeline status."""
        return self.status


    def get_pipeline_details(self):
        return self.to_json()


    def trigger_pipeline(self, url, repo_name):
        """Trigger the CI/CD pipeline."""

        self.repo_name = repo_name
        self.repo_url = url
        self.repo_directory = os.path.join(self.deployment_dir, repo_name)

        self.pull_code()

        self.test_code()


    def pull_code(self):
        """Pull code from GitHub."""

        git_service = GitService(self.repo_url, self.repo_directory, self.repo_name)
        git_service.resolve_code()

        self.project_type = UtilService().get_project_type(self.repo_directory)


    def test_code(self):
        """Test code."""

        self.status = "RUNNING TESTS"
        logger.log("Running tests", "info")

        test_runner = TestRunnerService()

        test_runner.run_tests(self.repo_name, self.project_type, self.pipeline_dir, self.repo_directory)

        return None


    def build_image(self):
        """Build Docker image."""


class TestRunnerService:
    """Service class for running tests in a Docker container."""

    def __init__(self):
        self.logger = Logger("TestRunnerService")
        self.saved_dockerfile_content = ""
        return

    def run_tests(self, repo_name, project_type, pipeline_dir, project_dir):
        """Runs test suite for the managed project."""

        image_tag = self.build_test_image(repo_name, project_type, pipeline_dir, project_dir)

        return self.run_test_container(image_tag, project_dir)

    def build_test_image(self, repo_name, project_type, pipeline_dir, project_dir):
        """Builds test image for the managed project."""
        image_tag = f"tiny-cicd-testrunner-{repo_name}".lower()
        dockerfile = "Dockerfile"

        self.logger.log(f"Building Docker image with tag: {image_tag}")

        if self.remove_existing_dockerfile(project_dir, dockerfile):
            self.copy_dockerfile(pipeline_dir, project_type, dockerfile, project_dir)

        os.chdir(project_dir)

        service = DockerService()

        if service.run_docker_build(image_tag):
            self.logger.log(f"Successfully built Docker image: {image_tag}")
            return image_tag
        else:
            self.logger.log(f"Error building Docker image.")
            return None

    def remove_existing_dockerfile(self, project_dir, dockerfile):
        """Removes existing Dockerfile from repository."""
        dockerfile_path = os.path.join(project_dir, dockerfile)
        if os.path.exists(dockerfile_path):
            self.logger.log(f"Removing existing Dockerfile from project directory: {project_dir}")
            service = DockerService()
            self.saved_dockerfile_content = service.read_dockerfile_content(dockerfile_path)
            os.remove(dockerfile_path)
            return True
        return False

    def copy_dockerfile(self, pipeline_dir, project_type, dockerfile, project_dir):
        """Copies the test Dockerfile template into the repository folder."""
        dockerfile_source_path = os.path.join(pipeline_dir, "test-runner", project_type.lower(), dockerfile)
        dockerfile_destination_path = project_dir

        shutil.copy(dockerfile_source_path, dockerfile_destination_path)
        self.logger.log(f"{dockerfile} copied successfully from '{dockerfile_source_path}' to '{dockerfile_destination_path}'.")


    def restore_dockerfile(self, project_dir):
        """Restores removed Dockerfile"""

        if(os.path.exists(os.path.join(project_dir, "Dockerfile"))):
            self.logger.log(f"Removing test Dockerfile from project directory: {project_dir}")
            os.remove(os.path.join(project_dir, "Dockerfile"))
            self.logger.log(f"Restoring Dockerfile from to directory: {self.saved_dockerfile_content}")
            service = DockerService()
            service.write_content_to_dockerfile(self.saved_dockerfile_content, (os.path.join(project_dir, "Dockerfile")))
            self.logger.log("Succesfully written to file")



    def run_test_container(self, image_tag, project_dir):
        """Runs testing suite in a sibling container"""

        os.chdir(pipeline_dir)

        service = DockerService()

        exit_code = service.run_docker_image(image_tag)

        self.cleanup_after_tests(image_tag, project_dir)

        return exit_code


    def cleanup_after_tests(self, image_tag, project_dir):
        """Cleans up test container and image"""

        os.chdir(pipeline_dir)

        try:

            service = DockerService()

            service.remove_docker_image(image_tag)
        
            self.restore_dockerfile(project_dir)

        except docker.errors.ImageNotFound:
            print(f"Docker image not found: {image_tag}")
            return False
        except Exception as e:
            print(f"An error occurred while removing Docker image: {e}")
            return False
        except Exception as e:
            print(f"An error occurred while restoring Docker image: {e}")
            return False


class UtilService:

    def __init__(self):
        return

    def get_project_type(self, repo_directory):
        """Detects the type of the project."""

        print(f"Detecting project type for {repo_directory}")

        if self.is_maven_project(repo_directory) is True:
            return "MAVEN"
        elif self.is_dotnet_project(repo_directory) is True:
            return "DOTNET"
        elif self.is_python_project(repo_directory) is True:
            return "PYTHON"
        elif self.is_go_project(repo_directory) is True:
            return "GO"
        else:
            return "UNSUPPORTED"


    def is_maven_project(self, repo_directory):
        """Check if project is a Maven project (checks for pom.xml file)."""
        pom_xml_path = os.path.join(repo_directory, "pom.xml")
        return os.path.exists(pom_xml_path)


    def is_dotnet_project(self, repo_directory):
        """Check if project is a .NET project (checks for .csproj file)."""
        for filename in os.listdir(repo_directory):
            if filename.endswith(".csproj") or filename.endswith(".cs"):
                return True
        return False


    def is_python_project(self, repo_directory):
        """Check if project is a Python project (checks for requirements.txt file)"""
        requirements_txt_path = os.path.join(repo_directory, "requirements.txt")
        setup_py_path = os.path.join(repo_directory, "setup.py")
        return os.path.exists(requirements_txt_path) or os.path.exists(setup_py_path)


    def is_go_project(self, repo_directory):
        """Check if project is a Go project (checks for go.mod file)"""
        go_mod_path = os.path.join(repo_directory, "go.mod")
        return os.path.exists(go_mod_path)


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


class GitService:
    """Service class for Git operations."""

    def __init__(self, repo_url, repo_directory, repo_name):
        self.project_type = ""
        self.repo_directory = repo_directory
        self.repo_name = repo_name
        self.repo_url = repo_url


    def resolve_code(self):
        """Pull code from GitHub."""

        os.chdir(pipeline_dir)

        if self.is_repo_cloned():
            self.pull_code()
        else:
            self.clone_repository()

        os.chdir(pipeline_dir)


    def is_repo_cloned(self):
        """Check if provided directory exists and/or create it"""

        logger.log("Checking if repository is cloned", "info")

        if not os.path.exists(self.repo_directory):
            logger.log("Project directory does not exist", "info")
            os.makedirs(self.repo_directory)
        if os.path.exists(self.repo_directory):
            logger.log("Deployment directory exists", "info")
            if self.is_git_repo():
                logger.log(f"Repository is cloned", "info")
                return True
            else:
                logger.log(f"Repository is not cloned but {self.repo_directory} exists", "info")
                os.rmdir(self.repo_directory)
                return False
        else:
            logger.log("Repository is not cloned", "info")
            return False


    def is_git_repo(self):
        """Checks if given directory contains a git repository."""
        try:
            _ = git.Repo(self.repo_directory).git_dir
            return True
        except git.exc.InvalidGitRepositoryError:
            return False

    def clone_repository(self):
        """Clone repository from GitHub"""

        logger.log("Cloning code from the repository", "info")

        os.chdir(deployments_dir)
        subprocess.check_call(["git", "clone", self.repo_url])


    def pull_code(self):
        """Pull code from GitHub."""

        logger.log("Pulling code from the repository", "info")

        os.chdir(self.repo_directory)
        subprocess.check_call(["git", "pull", self.repo_url])


class DockerService:
    """Class for handling Docker related operations."""

    def __init__(self) -> None:
        pass
    

    def read_dockerfile_content(self, path):
        """Reads Dockerfile content and returns it as a string."""
        with open(path, 'r', encoding="UTF-8") as file:
            dockerfile_content = file.read()
            return dockerfile_content


    def write_content_to_dockerfile(self, content, path):
        """Writes content to Dockerfile."""
        with open(path, 'w', encoding="UTF-8") as file:
            file.write(content)

    def run_docker_build(self, image_tag):
        """Runs docker image build process."""
        docker_build_cmd = ["docker", "build", "-t", image_tag, "."]
        logger.log(f"Running Docker build command: {docker_build_cmd}")

        try:
            subprocess.check_call(docker_build_cmd)
            return True
        except subprocess.CalledProcessError as e:
            logger.log(f"Error building Docker image: {e}")
            return False
        
    def run_docker_image(self, image_tag):
        """Runs specified docker image and returns container exit status code."""

        if not image_tag:
            logger.log("No image tag provided.")
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

        except docker.errors.ContainerError as e:
            logger.log(f"Error running tests in Docker container: {e}")
        except docker.errors.ImageNotFound as e:
            logger.log(f"Docker image not found: {e}")
        except Exception as e:
            logger.log(f"An unexpected error occurred: {e}")

        return exit_code
    

    def remove_docker_image(self, image_tag):
        """Removes docker image from the image list."""

        client = docker.from_env()

        try:
            image = client.images.get(image_tag)
            client.images.remove(image.id)

            logger.log(f"Successfully removed Docker image: {image_tag}")

        except docker.errors.ImageNotFound:
            logger.log(f"Docker image not found: {image_tag}", "error")
            return False
        except Exception as e:
            logger.log(f"An error occurred while removing Docker image: {e}", "error")
            return False