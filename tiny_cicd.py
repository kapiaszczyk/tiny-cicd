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


@app.route("/details")
def details():
    """Get CI/CD service details."""
    details = service.get_pipeline_details()
    logger.log("details")
    return details, 200, {"Content-Type": "application/json"}


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

    service.trigger_pipeline(url, repo_name)

    return "OK"


@app.route("/webhook-dockerhub", methods=["POST"])
def dockerhub_webhook():
    """Receive DockerHub push event."""

    payload = request.get_json()

    pushed_at = payload["push_data"]["pushed_at"]
    pusher = payload["push_data"]["pusher"]
    tag = payload["push_data"]["tag"]

    date_created = payload["repository"]["date_created"]
    dockerfile = payload["repository"]["dockerfile"]
    name = payload["repository"]["name"]
    repo_name = payload["repository"]["repo_name"]
    repo_url = payload["repository"]["repo_url"]

    service.trigger_deployment_pipeline((repo_name + ":" + tag))

    return "OK"


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Receive shutdown request"""

    result = service.trigger_shutdown()

    return "OK"


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
