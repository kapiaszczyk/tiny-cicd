# The plan
Obviously, the pipeline can be diveded into two parts - CI and CD. I decided to use Python to simpify the process of creating the pipeline (but implementation in shell scripts is also possible). The pipeline will be run on a RaspberryPI and the image will be deployed there as well. To reduce the memmory usage on the Raspberry, the pipeline will run directly on the host machine, not in a container. However, it is possible to run the pipeline in a container as well.

I created a sample Flask application which will be used in testing the pipeline which you can find [here](https://github.com/kapiaszczyk/sample-flask-service).

## CI

### Checking for changes in a github repository

To check for changes, a GitHub webhook will be used. The webhook will send a POST request to the RaspberryPI with a payload containing information about the changes in the repository. The payload will be parsed and the pipeline will be run.

An designeted `/webhook` endpoint will be created to handle the POST requests.

### Pulling new code

When the app receives a POST request from the webhook, it will pull the new code from the repository.

### Running tests

When the new code is pulled, the tests will be run.

### Building a Docker image

If the tests pass, the pipeline will build a Docker image from a Dockerfile included in the repository.

### Pushing the image to Docker Hub

If the image is built successfully, it will be pushed to a Docker Hub repository with a new tag (in some way incremented).

## CD

### Checking for changes on a Docker Hub repo for a new image

The pipeline will check for changes in the Docker Hub repository for a new image.

### Stopping the previously running image and removing it

If there is a new image, the previously running image will be stopped and removed.

### Pulling the new image and running it

When the previous image is stopped and removed, the new image will be pulled and run.

## The features

### Notifications and communication

#### Notification on failure on any of the steps

If any of the steps fails, a notification will be sent via email.

#### Notification on success in deploying the image in step 7

If the image is deployed successfully, a notification will be sent via email.

### Logs on each run

Each step will be logged and the logs will be stored in a file. The file is named after the date and time of the run and the run number.

### Behaviour on failure

The pipeline will not proceed with the next steps if any of the checks fails and will rollback to the previous deployment.