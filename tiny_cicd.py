"""Simple Flask CI/CD pipeline."""

from flask import Flask, request, redirect
from tiny_cicd_service import TinyCICDService
from tiny_cicd_logger import Logger

app = Flask(__name__)
service = TinyCICDService()
logger = Logger("tiny-cicd")


@app.route("/status")
def status():
    """Get CI/CD service status."""
    return "OK"


@app.route("/pipeline-status")
def pipeline_status():
    """Get CI/CD pipeline status."""
    pipeline_status_value = service.get_status()
    logger.log(f"Pipeline status: {pipeline_status_value}", "info")
    return pipeline_status_value


@app.route("/status/last-deploy")
def last_deploy():
    """Get last deploy status."""
    return "PLACEHOLDER"


@app.route("/webhook-github", methods=["POST"])
def github_webhook():
    """Receive GitHub push event."""

    payload = request.get_json()

    url = payload["payload"]["repository"]["url"]
    repo_name = payload["payload"]["repository"]["name"]
    last_commit = payload["payload"]["after"]
    previous_commit = payload["payload"]["before"]

    logger.log(f"Received push event for {repo_name} with commit {last_commit}", "info")
    logger.log(f"Previous commit was {previous_commit}", "info")

    service.trigger_pipeline(url)

    return "OK"


@app.route("/webhook-dockerhub", methods=["POST"])
def dockerhub_webhook():
    """Receive DockerHub push event."""
    return "PLACEHOLDER"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
