#!/bin/bash
set -e

export EXL2_VERSION=0.1.1
export FLASH_ATTN_VERSION=2.5.9
export PYTORCH_BUILD_VERSION=2.3.0
export PYTORCH_BUILD_NUMBER=0
# Cannot be auto-detected during docker build.
export TORCH_CUDA_ARCH_LIST="7.5 8.6 8.9"
export CUDA_HOME=/usr/local/cuda

# Limit ninja jobs to avoid OOM.
export MAX_JOBS=8

# Need curl to download stuff.
apt-get update
apt-get install -y --no-install-recommends curl

# Install & setup conda.
mkdir -p /tmp/miniconda3
curl -sLo /tmp/miniconda3/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-py310_24.3.0-0-Linux-x86_64.sh
bash /tmp/miniconda3/miniconda.sh -b -u -p /tmp/miniconda3
rm -rf /tmp/miniconda3/miniconda.sh
eval "$(/tmp/miniconda3/bin/conda shell.bash hook)"

# Setup build environment.
conda config --set channel_priority flexible
conda activate
magma_pkg=$(nvcc --version | sed -ne 's/.*_\([0-9]\+\)\.\([0-9]\+\).*/pytorch::magma-cuda\1\2/p')
# conda install -y --no-update-deps cmake ninja intel::mkl-static intel::mkl-include $magma_pkg
conda install -y --no-update-deps cmake ninja packaging wheel setuptools $magma_pkg

# Build & install torch (needed to build exl2).
mkdir -p /tmp/pytorch
curl -Ls https://github.com/pytorch/pytorch/releases/download/v${PYTORCH_BUILD_VERSION}/pytorch-v${PYTORCH_BUILD_VERSION}.tar.gz | tar --strip-components=1 -xzC /tmp/pytorch
pip install -r /tmp/pytorch/requirements.txt
cd /tmp/pytorch
export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
# Temporary bug: https://github.com/pytorch/pytorch/issues/105248
rm -f /tmp/miniconda3/lib/libstdc++.so.6
CFLAGS=" -Os " \
  ONNX_ML=0 USE_CUDNN=0 USE_CUSPARSELT=0 \
  USE_FBGEMM=0 USE_KINETO=0 BUILD_TEST=0 \
  USE_MKLDNN=0 USE_ITT=0 USE_NNPACK=0 \
  USE_QNNPACK=0 USE_DISTRIBUTED=0 USE_TENSORPIPE=0 \
  USE_GLOO=0 USE_MPI=0 USE_XNNPACK=0 \
  USE_PYTORCH_QNNPACK=0 USE_MKL=0 USE_OPENMP=0 \
  python setup.py install
cd /

# Build & install exl2.
mkdir -p /tmp/exllamav2
curl -Ls https://github.com/turboderp/exllamav2/archive/refs/tags/v${EXL2_VERSION}.tar.gz | tar --strip-components=1 -xzC /tmp/exllamav2
sed -i '/"ninja",/d' /tmp/exllamav2/setup.py
sed -i '/"torch>=.\+",/d' /tmp/exllamav2/setup.py
cd /tmp/exllamav2
python setup.py install
cd /

# Build & install flash_attn.
mkdir -p /tmp/flash_attn
curl -Ls https://github.com/Dao-AILab/flash-attention/archive/refs/tags/v${FLASH_ATTN_VERSION}.tar.gz | tar --strip-components=1 -xzC /tmp/flash_attn
cd /tmp/flash_attn
python setup.py install
cd /

# Copy all the wheels to /whl and clean up.
mkdir -p /whl
cd /tmp/pytorch
python setup.py bdist_wheel
cp dist/*.whl /whl/
cd /tmp/exllamav2
python setup.py bdist_wheel
cp dist/*.whl /whl/
cd /
cd /tmp/flash_attn
python setup.py bdist_wheel
cp dist/*.whl /whl/
cd /
# rm -rf /tmp/miniconda3 /tmp/pytorch /tmp/exllamav2 /tmp/flash_attn
