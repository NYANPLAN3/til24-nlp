# syntax=docker/dockerfile:1
# NOTE: Docker's GPU support works for most images despite common misconceptions.
#FROM python:3.11-slim-bookworm
#FROM pytorch/pytorch:2.3.0-cuda12.1-cudnn8-runtime
#FROM nvidia/cuda:11.8.0-base-ubuntu22.04
#FROM gcr.io/deeplearning-platform-release/pytorch-cu121.2-2.py310:latest

ARG CUDA_VERSION=12.1.1

FROM nyanplan3/til24_nlp:build-whls as build
FROM nvidia/cuda:${CUDA_VERSION}-base-ubuntu22.04 as deploy

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && apt-get install -y --no-install-recommends \
  cuda-nvtx-12-1 \
  libcusparse-12-1 \
  libcufft-12-1 \
  libcurand-12-1 \
  libcublas-12-1 \
  libnvjitlink-12-1
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && apt-get install -y --no-install-recommends python3-pip
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -U pip
RUN --mount=type=bind,from=build,source=/whl,target=/whl \
  pip install /whl/*

WORKDIR /app
COPY --link models ./models

# Remember to regenerate requirements.txt!
COPY --link requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -r requirements.txt

COPY --link til24_nlp ./til24_nlp

EXPOSE 5002
CMD ["uvicorn", "--host=0.0.0.0", "--port=5002", "--factory", "til24_nlp:create_app"]
