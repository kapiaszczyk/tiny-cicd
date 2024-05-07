"""Service part for the tiny CI/CD system"""

import os
import git
import subprocess
import docker
import shutil
import json

from tiny_cicd_logger import Logger

deployments_dir = "deployments"
dockerhub_repo_name = "kapiaszczyk"
pipeline_dir = os.getcwd()
deployment_params = {"port: 8080"}

class TinyCICDService:
    """Tiny CI/CD service class."""

    logger = Logger("TinyCICDService")

    def __init__(self):
        self.status = "IDLE"
        self.repo_name = ""
        self.repo_directory = ""
        self.repo_url = ""
        self.project_type = ""
        self.pipeline_dir = pipeline_dir
        self.deployment_dir = deployments_dir
        self.last_tag_number = None
        self.deployed_container_id = None
        self.docker_service = DockerService()

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

    def get_last_deployment_details(self):
        """Get the last deployment details."""

        data = {
            "last_tag_number": self.last_tag_number,
            "deployed_container_id": self.deployed_container_id
        }

        return json.dumps(data)


    def get_status(self):
        """Get CI/CD pipeline status."""
        return self.status

    def get_pipeline_details(self):
        return self.to_json()

    def trigger_pipeline(self, url, repo_name):
        """Trigger the CI/CD pipeline."""

        self.status = "TRIGGERED"

        self.repo_name = repo_name
        self.repo_url = url
        self.repo_directory = os.path.join(self.deployment_dir, repo_name)

        self.logger.log(f"Triggering pipeline for {repo_name}")

        self.status = "PULLING CODE"

        self.pull_code()

        self.status = "RUNNING TESTS"

        self.test_code()

        self.status = "BUILDING IMAGE"

        self.build_image()

        self.status = "PUSHING IMAGE"

        self.push_image()

        self.status = "IDLE"

    def trigger_deployment_pipeline(self, image_tag):
        """Triggers the deployment pipeline"""

        self.status = "DEPLOYING"

        image_name, tag = image_tag.split(':')

        old_container_id = self.deployed_container_id

        if old_container_id is None:
            self.docker_service.get_youngest_container_id(image_name)

        self.status = "PULLING IMAGE"

        self.pull_image(image_tag)

        self.status = "STOPPING CURRENTLY DEPLOYED CONTAINER"

        self.stop_deployed_container()

        self.status = "DEPLOYING IMAGE"

        self.deploy_image(image_tag, None)

        self.status = "CLEANING UP CONTAINERS"

        self.remove_paused_container(old_container_id)

        image_name, tag = image_tag.split(':')

        self.prune_images(3, (image_name))

        self.status = "IDLE"

    def trigger_shutdown(self):
        """Shuts down all containers"""

        self.status = "SHUTTING DOWN"

        self.docker_service.stop_all_containers()


    def pull_code(self):
        """Pull code from GitHub."""

        git_service = GitService(self.repo_url, self.repo_directory, self.repo_name)
        git_service.resolve_code()

        self.project_type = UtilService().get_project_type(self.repo_directory)

    def test_code(self):
        """Test code."""

        self.status = "RUNNING TESTS"
        self.logger.log("Running tests", "info")

        test_runner = TestRunnerService()

        test_runner.run_tests(self.repo_name, self.project_type, self.pipeline_dir, self.repo_directory)

        return None

    def build_image(self):
        """Build Docker image."""

        os.chdir(self.repo_directory)
        git_service = GitService(self.repo_url, self.repo_directory, self.repo_name)
        sha = git_service.get_commit_sha()
        os.chdir(self.pipeline_dir)

        image_tag = f"{dockerhub_repo_name}/{self.repo_name}:{sha}"

        self.docker_service.run_docker_build(image_tag, self.repo_directory)

        self.last_tag_number = image_tag

        self.logger.log(f"Latest image tag is: {self.last_tag_number}")

    def push_image(self):
        """Push image to DockerHub."""

        self.docker_service.push_image(self.last_tag_number)

    def pull_image(self, image_tag):
        """Pull image from Docker Hub."""

        self.docker_service.pull_image(image_tag)

    def deploy_image(self, image_tag, deployment_params):
        """Deploys the specified image"""

        service = DockerService()

        deployed_container_id = service.deploy_image(image_tag, deployment_params)

        self.logger.log(f"Image to be deployed: {image_tag}")

        if (id is None):
            self.rollback_to_previous_container()
        else:
            self.deployed_container_id = deployed_container_id

        self.logger.log(f"Deployed container id: {deployed_container_id}")

    def stop_deployed_container(self):
        """Stops the currently deployed container"""

        service = DockerService()

        container_to_be_stopped = self.deployed_container_id

        if container_to_be_stopped is None:
            self.logger.log("There is no deployed container or none to be stopped")
        else:
            self.logger.log(f"Container to be stopped: {container_to_be_stopped}")

            service.stop_running_container(container_to_be_stopped)

    def rollback_to_previous_container(self):
        """Restart the paused container"""

        service = DockerService()

        container_to_be_restarted = self.deployed_container_id

        if container_to_be_restarted is None:
            self.logger.log("There is no previous container to rollback to")
        else:
            self.logger.log(f"Container to be restarted: {container_to_be_restarted}")

            id = service.run_container(container_to_be_restarted)

            self.deployed_container_id = id

    def remove_paused_container(self, old_container_id):
        """Removes paused containers"""

        service = DockerService()

        if old_container_id is None:
            self.logger.log("There is no container to be removed")
        else:

            self.logger.log(f"Container to be removed: {old_container_id}")

            service.remove_container(old_container_id)

    def prune_images(self, old_images_to_keep, repo_name):
        """Removes unused images"""

        service = DockerService()

        service.prune_unused_images(old_images_to_keep, repo_name)

    def stop_all_containers(self):

        service = DockerService()

        service.stop_all_containers()

class TestRunnerService:
    """Service class for running tests in a Docker container."""

    logger = Logger("TestRunnerService")

    def __init__(self):
        self.saved_dockerfile_content = ""
        return

    def run_tests(self, repo_name, project_type, src_dir, project_dir):
        """Runs test suite for the managed project."""

        image_tag = self.build_test_image(repo_name, project_type, src_dir, project_dir)

        return self.run_test_container(image_tag, project_dir)

    def build_test_image(self, repo_name, project_type, src_dir, project_dir):
        """Builds test image for the managed project."""
        image_tag = f"tiny-cicd-testrunner-{repo_name}".lower()
        dockerfile = "Dockerfile"

        self.logger.log(f"Building Docker image with tag: {image_tag}")

        if self.remove_existing_dockerfile(project_dir, dockerfile):
            self.copy_dockerfile(src_dir, project_type, dockerfile, project_dir)

        service = DockerService()

        if service.run_docker_build(image_tag, project_dir):
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

    def copy_dockerfile(self, src_dir, project_type, dockerfile, project_dir):
        """Copies the test Dockerfile template into the repository folder."""
        dockerfile_source_path = os.path.join(src_dir, "test-runner", project_type.lower(), dockerfile)
        dockerfile_destination_path = project_dir

        shutil.copy(dockerfile_source_path, dockerfile_destination_path)
        self.logger.log(
            f"{dockerfile} copied successfully from '{dockerfile_source_path}' to '{dockerfile_destination_path}'.")

    def restore_dockerfile(self, project_dir):
        """Restores removed Dockerfile"""

        if os.path.exists(os.path.join(project_dir, "Dockerfile")):
            self.logger.log(f"Removing test Dockerfile from project directory: {project_dir}")
            os.remove(os.path.join(project_dir, "Dockerfile"))
            self.logger.log(f"Restoring Dockerfile to directory: {project_dir}")
            service = DockerService()
            service.write_content_to_dockerfile(self.saved_dockerfile_content,
                                                (os.path.join(project_dir, "Dockerfile")))
            self.logger.log("Successfully written to file")

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
            self.logger.log(f"Docker image not found: {image_tag}", "error")
            return False
        except Exception as e:
            self.logger.log(f"An error occurred while removing Docker image: {e}", "error")
            return False


class UtilService:
    logger = Logger("UtilService")

    def __init__(self):
        return

    def get_project_type(self, repo_directory):
        """Detects the type of the project."""

        self.logger.log(f"Detecting project type for {repo_directory}")

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

    @staticmethod
    def is_maven_project(repo_directory):
        """Check if project is a Maven project (checks for pom.xml file)."""
        pom_xml_path = os.path.join(repo_directory, "pom.xml")
        return os.path.exists(pom_xml_path)

    @staticmethod
    def is_dotnet_project(repo_directory):
        """Check if project is a .NET project (checks for .csproj file)."""
        for filename in os.listdir(repo_directory):
            if filename.endswith(".csproj") or filename.endswith(".cs"):
                return True
        return False

    @staticmethod
    def is_python_project(repo_directory):
        """Check if project is a Python project (checks for requirements.txt file)"""
        requirements_txt_path = os.path.join(repo_directory, "requirements.txt")
        setup_py_path = os.path.join(repo_directory, "setup.py")
        return os.path.exists(requirements_txt_path) or os.path.exists(setup_py_path)

    @staticmethod
    def is_go_project(repo_directory):
        """Check if project is a Go project (checks for "go.mod" file)"""
        go_mod_path = os.path.join(repo_directory, "go.mod")
        return os.path.exists(go_mod_path)

    def resolve_repository_name(self, url):
        """Get repository name from the git repository url."""
        self.logger.log("Resolving repository name", "info")
        if url.endswith(".git"):
            name = url[:-4].split("/")[-1]
            self.logger.log(f"Name resolved to {name}", "info")
            return name
        else:
            name = url.split("/")[-1]
            self.logger.log(f"Name resolved to {name}", "info")
            return name

    @staticmethod
    def parse_docker_image_tag(image_tag):
        """Parse Docker image tag <repository>/<image_name>:<tag> into repository, image name, and tag."""
        if ':' in image_tag:
            repository_image, tag = image_tag.split(':')
        else:
            repository_image = image_tag
            tag = None

        repository, image_name = repository_image.split('/', 1)

        return repository, image_name, tag


class GitService:
    """Service class for Git operations."""

    logger = Logger("GitService")

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

        self.logger.log("Checking if repository is cloned", "info")

        if not os.path.exists(self.repo_directory):
            self.logger.log("Project directory does not exist", "info")
            os.makedirs(self.repo_directory)
        if os.path.exists(self.repo_directory):
            self.logger.log("Deployment directory exists", "info")
            if self.is_git_repo():
                self.logger.log(f"Repository is cloned", "info")
                return True
            else:
                self.logger.log(f"Repository is not cloned but {self.repo_directory} exists", "info")
                os.rmdir(self.repo_directory)
                return False
        else:
            self.logger.log("Repository is not cloned", "info")
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

        self.logger.log("Cloning code from the repository", "info")

        os.chdir(deployments_dir)
        subprocess.check_call(["git", "clone", self.repo_url])

    def pull_code(self):
        """Pull code from GitHub."""

        self.logger.log("Pulling code from the repository", "info")

        os.chdir(self.repo_directory)
        subprocess.check_call(["git", "pull", self.repo_url])

    def get_commit_sha(self):
        """Returns last commit SHA."""

        self.logger.log("Retrieving last commit SHA")

        command = "git rev-parse --short HEAD"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise RuntimeError(f"Git command failed with error:\n{result.stderr}")

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Git command: {e}")


class DockerService:
    """Class for handling Docker related operations."""

    logger = Logger("DockerService")

    def __init__(self):
        self.client = docker.from_env()

    @staticmethod
    def read_dockerfile_content(path):
        """Reads Dockerfile content and returns it as a string."""
        with open(path, 'r', encoding="UTF-8") as file:
            dockerfile_content = file.read()
            return dockerfile_content

    @staticmethod
    def write_content_to_dockerfile(content, path):
        """Writes content to Dockerfile."""
        with open(path, 'w', encoding="UTF-8") as file:
            file.write(content)

    def run_docker_build(self, image_tag, build_directory):
        """Runs docker image build process."""

        previous_directory = os.getcwd()

        os.chdir(build_directory)

        docker_build_cmd = ["docker", "build", "-t", image_tag, "."]
        self.logger.log(f"Running Docker build command: {docker_build_cmd}")

        try:
            subprocess.check_call(docker_build_cmd)
            os.chdir(previous_directory)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.log(f"Error building Docker image: {e}")
            os.chdir(previous_directory)
            return False

    def run_docker_image(self, image_tag):
        """Runs specified docker image and returns container exit status code."""

        if not image_tag:
            self.logger.log("No image tag provided.")
            return

        try:
            container = self.client.containers.run(
                image=image_tag,
                detach=True,
            )

            result = container.wait()
            container.remove()

            exit_code = result["StatusCode"]

            return exit_code

        except docker.errors.ContainerError as e:
            self.logger.log(f"Error running tests in Docker container: {e}")
        except docker.errors.ImageNotFound as e:
            self.logger.log(f"Docker image not found: {e}")
        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}")

        return exit_code

    def remove_docker_image(self, image_tag):
        """Removes docker image from the image list."""

        try:
            image = self.client.images.get(image_tag)
            self.client.images.remove(image.id)

            self.logger.log(f"Successfully removed Docker image: {image_tag}")

        except docker.errors.ImageNotFound:
            self.logger.log(f"Docker image not found: {image_tag}", "error")
            return False
        except Exception as e:
            self.logger.log(f"An error occurred while removing Docker image: {e}", "error")
            return False

    def push_image(self, image_tag):
        """Pushes image to Docker Hub."""

        util_service = UtilService()

        repository, image_name, image_tag = util_service.parse_docker_image_tag(image_tag)

        image_name = f"{repository}/{image_name}:{image_tag}"

        try:
            for line in self.client.images.push(image_name, stream=True, decode=True):
                if 'status' in line:
                    self.logger.log(f"Pushing: {line['status']}", "info")

            self.logger.log(f"Successfully pushed image to Docker Hub: {image_name}", "info")

        except docker.errors.APIError as e:
            self.logger.log(f"Failed to push image to Docker Hub with reason: {e}", "error")

    def pull_image(self, image_tag):
        """Pulls image with specified tag from the Docker Hub"""

        try:
            self.client.images.pull(image_tag)
        except Exception as e:
            self.logger.log(f"Failed to pull image {image_tag} with reason: {e}", "error")

    def deploy_image(self, image_tag, port_mapping):
        """Runs the image with specified tag."""

        # Overriding port_mapping for initial feature implementation
        port_mapping = "5000:5000"

        if not image_tag:
            self.logger.log("No image tag provided", "error")
            return None

        try:
            ports = None
            if port_mapping:
                ports = {f"{port_mapping.split(':')[0]}/tcp": int(port_mapping.split(':')[1])}
            container = self.client.containers.run(image_tag, ports=ports, detach=True)

            self.logger.log(f"Container deployed successfully: {container.id}", "info")
            return container.id

        except docker.errors.ContainerError as e:
            self.logger.log(f"Error deploying container: {e}", "error")
            return None

        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return None

    def stop_running_container(self, id):
        """Stops a container by id"""

        try:
            container = self.client.containers.get(id)
            container.stop()
            self.logger.log(f"Container {id} stopped successfully", "info")
            return True
        except docker.errors.NotFound as e:
            self.logger.log(f"Container {id} not found: {e}", "error")
            return False
        except docker.errors.APIError as e:
            self.logger.log(f"Error pausing container {id}: {e}", "error")
            return False
        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return False

    def run_container(self, id):
        """Runs a container passed by id"""

        try:
            container = self.client.containers.get(id)
            container.unpause()
            self.logger.log(f"Container {id} unpaused successfully", "info")
            return True
        except docker.errors.NotFound as e:
            self.logger.log(f"Container {id} not found: {e}", "error")
            return False
        except docker.errors.APIError as e:
            self.logger.log(f"Error unpausing container {id}: {e}", "error")
            return False
        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return False

    def remove_container(self, id):
        """Removes specified container"""

        try:
            container = self.client.containers.get(id)
            container.remove()
            self.logger.log(f"Container {id} removed successfully", "info")
            return True
        except docker.errors.NotFound as e:
            self.logger.log(f"Container {id} not found: {e}", "error")
            return False
        except docker.errors.APIError as e:
            self.logger.log(f"Error removing container {id}: {e}", "error")
            return False
        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return False

    def prune_unused_images(self, amount, repo_name):
        """Prunes specified amount of unused images from the specified repository."""

        try:
            images = self.client.images.list(name=repo_name)

            if not images:
                self.logger.log(f"No images found for repository: {repo_name}", "info")
                return

            # Sort images by creation date (oldest to newest)
            images.sort(key=lambda img: img.attrs['Created'])

            # Determine the number of images to retain
            images_to_keep = images[-amount:]

            # Identify images to prune (those not in the list to keep)
            images_to_prune = [img for img in images if img not in images_to_keep]

            if not images_to_prune:
                self.logger.log(f"No images to prune for repository: {repo_name}", "info")
                return

            for img in images_to_prune:
                self.client.images.remove(img.id, force=True)
                self.logger.log(f"Pruned image: {img.tags[0]}", "info")

            self.logger.log(f"Successfully pruned unused images for repository: {repo_name}", "info")

        except docker.errors.APIError as e:
            self.logger.log(f"Failed to prune images: {e}", "error")

        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")

    def get_youngest_container_id(self, image_name):
        """Retrieve the ID of the youngest running container from an image with the specified name."""

        if image_name is None:
            self.logger.log("No image name provided", "error")
            return None

        try:
            containers = self.client.containers.list()

            filtered_containers = [container for container in containers if image_name in container.image.tags]

            if not filtered_containers:
                self.logger.log(f"No running containers found for image: {image_name}", "info")
                return None

            # Sort containers by creation time (newest to oldest)
            # And retrieve the ID of the youngest (most recently created) container
            filtered_containers.sort(key=lambda container: container.attrs['Created'], reverse=True)

            youngest_container_id = filtered_containers[0].id

            self.logger.log(f"Youngest container ID for image {image_name}: {youngest_container_id}", "info")
            return youngest_container_id

        except docker.errors.APIError as e:
            self.logger.log(f"Failed to retrieve youngest container ID: {e}", "error")
            return None

        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return None

    def stop_all_containers(self):
        """Shutdown all containers"""

        self.logger.log(f"Stopping all containers")

        try:
            containers = self.client.containers.list()

            for container in containers:
                container.stop()

        except docker.errors.APIError as e:
            self.logger.log(f"Failed to stop containers with reason: {e}", "error")
            return None

        except Exception as e:
            self.logger.log(f"An unexpected error occurred: {e}", "error")
            return None
