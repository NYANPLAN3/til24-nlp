# syntax=docker/dockerfile:1

ARG CUDA_VERSION=12.1.1

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
  libnvjitlink-12-1 \
  curl
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  apt-get update && apt-get install -y --no-install-recommends python3-pip
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -U pip
RUN --mount=type=bind,source=./whl,target=/whl \
  pip install --no-cache-dir /whl/*

WORKDIR /app

# Remember to regenerate requirements.txt!
COPY --link requirements.txt .env ./
RUN --mount=type=cache,target=/root/.cache/pip,sharing=locked \
  pip install -r requirements.txt

COPY --link models ./models
COPY --link til24_nlp ./til24_nlp

EXPOSE 5002
ENV TORCH_CUDNN_V8_API_ENABLED=1 PYTORCH_CUDA_ALLOC_CONF=backend:cudaMallocAsync CUDA_VISIBLE_DEVICES=0
# uvicorn --host=0.0.0.0 --port=5002 --factory til24_nlp:create_app
CMD ["uvicorn", "--log-level=warning", "--host=0.0.0.0", "--port=5002", "--factory", "til24_nlp:create_app"]
