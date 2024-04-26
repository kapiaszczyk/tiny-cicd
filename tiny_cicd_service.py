"""Service part for the tiny CI/CD system"""

def pull_code():
    """Pull code from GitHub."""
    return "PULLING CODE"


def test_code():
    """Test code."""
    return "TESTING CODE"


def build_image():
    """Build Docker image."""
    return "BUILDING IMAGE"


def deploy_image():
    """Deploy Docker image."""
    return "DEPLOYING IMAGE"


def pull_image():
    """Pull Docker image."""
    return "PULLING IMAGE"


def run_container():
    """Run Docker container."""
    return "RUNNING CONTAINER"


def stop_container():
    """Stop Docker container."""
    return "STOPPING CONTAINER"


def remove_container():
    """Remove Docker container."""
    return "REMOVING CONTAINER"


def remove_image():
    """Remove Docker image."""
    return "REMOVING IMAGE"


def cleanup():
    """Cleanup after deploy."""
    return "CLEANING UP"


def rollback():
    """Rollback to the previous version."""
    return "ROLLBACK"
