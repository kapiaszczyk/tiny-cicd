"""Simple Flask CI/CD pipeline."""

from flask import Flask

app = Flask(__name__)


@app.route("/status")
def status():
    """Get CI/CD pipeline status."""
    return "OK"


@app.route("/status/last-deploy")
def last_deploy():
    """Get last deploy status."""
    return "PLACEHOLDER"


@app.route("/webhook", methods=["POST"])
def github_webhook():
    """Receive GitHub push event."""
    # Do not return anything to GitHub


if __name__ == '__main__':
    app.run(port=5000)
