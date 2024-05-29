# til24-nlp

Template for FastAPI-based API server. Features:

- Supports both CPU/GPU-accelerated setups automatically.
- Poetry for package management.
- Ruff for formatting & linting.
- VSCode debugging tasks.
- Other QoL packages.

Oh yeah, this template should work with the fancy "Dev Containers: Clone Repository
in Container Volume..." feature.

Note: competition uses port 5002 for NLP server.
Note: Eval is both case & punctuation sensitive.
Note: Compute Capability of T4 is 7.5, RTX 4070 Ti is 8.9.

## Useful Commands

The venv auto-activates, so these work.

```sh
# Launch debugging server, use VSCode's debug task instead by pressing F5.
poe dev
# Run test stolen from the official competition template repo.
poe test
# Building docker image for deployment, will also be tagged as latest.
poe build {insert_version_like_0.1.0}
# Run the latest image locally.
poe prod
# Publish the latest image to GCP artifact registry.
poe publish
```

Finally, to submit the image (must be done on GCP unfortunately).

```sh
gcloud ai models upload --region asia-southeast1 --display-name 'nyanplan3-nlp' --container-image-uri asia-southeast1-docker.pkg.dev/dsta-angelhack/repository-nyanplan3/nyanplan3-nlp:finals --container-health-route /health --container-predict-route /extract --container-ports 5002 --version-aliases default
```

## PyTorch Slim

1. Build `Dockerfile.whl-build`
2. Use `docker cp` to copy the wheel files located at `/whl` inside the image to `./whl` in the repo
3. Build `Dockerfile.precompiled`
