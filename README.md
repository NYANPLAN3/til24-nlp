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

## Useful Commands

The venv auto-activates, so these work.

```sh
# Launch debugging server, use VSCode's debug task instead by pressing F5.
poe dev
# Run test stolen from the official competition template repo.
poe test
# Building docker image for deployment.
poe build {insert_version_like_0.1.0}
# Run the docker image locally.
poe prod
```
