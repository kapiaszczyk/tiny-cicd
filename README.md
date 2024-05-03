# Tiny CI/CD
Simple prototype CI/CD pipeline written in Python.

![pipes](https://github.com/kapiaszczyk/tiny-cicd/assets/41442206/9da982c0-664a-4c58-a6f5-ad59daa0e19e)

## About

A simple CI/CD pipeline designed to automate the testing, building, and deployment of a Dockerized application. The pipeline is triggered by changes in a GitHub repository and integrates with Docker Hub for image management.

## The goal

Run a simple CI/CD pipeline that includes running tests, building a Docker image, pushing it to Docker Hub, pulling and running it.

## The steps

1. Monitor GitHub Repository
    -  The pipeline is notified of changes via a GitHub webhook.
2. Pull Code and Run Tests
    -  Upon detecting changes, the pipeline pulls the latest code and executes defined tests.
3. Build Docker Image
    -  If the tests pass successfully, the pipeline builds a Docker image using the provided Dockerfile from the repository.
4. Push Image to Docker Hub
    -  After a successful build, the image is tagged and pushed to Docker Hub, with a version based on the commit SHA.
5. Monitor Docker Hub for New Image
    -  The pipeline is notified of changes via a Dockr Hub webhook.
6. Replace Running Container
    -  When a new image is detected, the existing running container is stopped and removed.
7. Pull and Run New Image
    -  Finally, the updated image is pulled from Docker Hub and launched as a running container.

## Features (to be implemented)
- [ ] Notifications
    -  Notifications on critical failures and successfull deployment
- [ ] Support for Maven projects, .NET, Go and Python projects
- [ ] Automatic rollback on image deployment failure
- [ ] Parameterised builds and configuration via environmental variables
- [ ] Performance Monitoring
- [ ] Different rollout strategies
- [ ] Gracefull degradation of deployed containers
- [ ] Ability to manage more than one project/container
