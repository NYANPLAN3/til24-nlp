# syntax=docker/dockerfile:1
# NOTE: Docker's GPU support works for most images despite common misconceptions.
#FROM python:3.11-slim-bookworm
# Example of prebuilt pytorch image to save download time.
#FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime
#FROM nvidia/cuda:11.8.0-base-ubuntu22.04
FROM gcr.io/deeplearning-platform-release/pytorch-cu121.2-2.py310:latest

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

ARG EXL2_VERSION=v0.0.21
# Cannot be auto-detected during docker build.
ARG TORCH_CUDA_ARCH_LIST="7.5 8.9"

WORKDIR /app

# Cache packages to speed up builds, see: https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md#run---mounttypecache
# Example:
#RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
#  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
#RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
#  --mount=type=cache,target=/var/lib/apt,sharing=locked \
#  apt-get update && apt-get install -y --no-install-recommends python3-pip

# Split multiple RUN commands to avoid caching issues.
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -U pip
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  mkdir exllamav2 \
  && wget -qO- https://github.com/turboderp/exllamav2/archive/refs/tags/${EXL2_VERSION}.tar.gz | tar --strip-components=1 -xzC exllamav2 \
  && pip install ninja \
  && pip install --no-use-pep517 ./exllamav2 \
  && rm -rf exllamav2
#RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
#  pip install torch==2.3.0+cu118 --extra-index-url https://download.pytorch.org/whl/cu118

# COPY should be from least changed to most frequently changed.
COPY --link models ./models

# Remember to regenerate requirements.txt!
COPY --link requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -r requirements.txt

COPY --link til24_nlp ./til24_nlp

EXPOSE 5002
CMD ["uvicorn", "--host=0.0.0.0", "--port=5002", "--factory", "til24_nlp:create_app"]
