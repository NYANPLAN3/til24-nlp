# til24-nlp

Template for FastAPI-based API server. Features:

- Supports both CPU/GPU-accelerated setups automatically.
- Poetry for package management.
- Ruff for formatting & linting.
- VSCode debugging tasks.
- Other QoL packages.

Oh yeah, this template should work with the fancy "Dev Containers: Clone Repository
in Container Volume..." feature.

## Useful Commands

```sh
# The venv auto-activates, so these work.
poe prod # Launch "production" server.
poe dev # Launch debugging server, use VSCode's debug task instead by pressing F5.

# Building docker image for deployment.
docker build -f Dockerfile . -t nyanplan3-nlp:latest -t nyanplan3-nlp:0.1.0

# Running FastAPI app (with GPU).
docker run --rm --gpus all -p 5002:5002 nyanplan3-nlp
```
