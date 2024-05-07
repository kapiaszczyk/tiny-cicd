"""Simple Flask CI/CD pipeline."""

from flask import Flask, request, redirect
from simple_websocket import Server, ConnectionClosed
from tiny_cicd_service import TinyCICDService
from tiny_cicd_logger import Logger
import time

app = Flask(__name__)
service = TinyCICDService()
logger = Logger("tiny-cicd")


@app.route("/status", websocket=True)
def status():
    """Get CI/CD service status."""
    ws = Server(request.environ)

    try:
        while True:
            ws.send(service.get_status())
            time.sleep(5)
    except ConnectionClosed:
        pass


@app.route("/details")
def details():
    """Get CI/CD service details."""
    return service.get_pipeline_details(), 200, {"Content-Type": "application/json"}


@app.route("/pipeline-status")
def pipeline_status():
    """Get CI/CD pipeline status."""
    return service.get_status(), 200, {"Content-Type": "application/json"}


@app.route("/status/last-deploy")
def last_deploy():
    """Get last deploy status."""
    return service.get_last_deployment_details(), 200, {"Content-Type": "application/json"}


@app.route("/webhook-github", methods=["POST"])
def github_webhook():
    """Receive GitHub push event."""

    payload = request.get_json()

    url = payload["payload"]["repository"]["url"]
    repo_name = payload["payload"]["repository"]["name"]
    last_commit = payload["payload"]["after"]
    previous_commit = payload["payload"]["before"]

    service.trigger_pipeline(url, repo_name)

    return "OK", 200, {"Content-Type": "application/json"}


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

    return "OK", 200, {"Content-Type": "application/json"}


@app.route("/shutdown", methods=["POST"])
def shutdown():
    """Receive shutdown request"""

    service.trigger_shutdown()

    return "OK", 200, {"Content-Type": "application/json"}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050, debug=True)
