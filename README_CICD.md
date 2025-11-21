# CI/CD Secrets & Setup

Set these GitHub repository secrets before using the workflow:

- DOCKERHUB_USERNAME  - your Docker Hub username
- DOCKERHUB_TOKEN     - Docker Hub access token (not password)
- DEPLOY_HOST         - IP or hostname of your server (for SSH deploy)
- DEPLOY_USER         - SSH user on the server
- DEPLOY_SSH_KEY      - Private SSH key (add as secret, no passphrase recommended for automation)
- DEPLOY_SSH_PORT     - (optional) SSH port, default 22

Notes:
- The workflow builds the Docker image, pushes to Docker Hub, and then SSHes to your server and runs the container.
- If you prefer GitHub Packages (GHCR) or other registries, modify the login/build steps accordingly.
