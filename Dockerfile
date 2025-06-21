# Base CUDA + Python image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# System packages
RUN apt-get update && apt-get install -y \
    wget curl git ca-certificates build-essential \
    libglib2.0-0 libxext6 libsm6 libxrender1 libssl-dev \
    libsndfile1 libbz2-dev liblzma-dev libffi-dev \
    libgl1 libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh
ENV PATH=$CONDA_DIR/bin:$PATH

# Copy environment and install conda dependencies
COPY conda_env.yml /tmp/conda_env.yml
RUN conda update -n base -c defaults conda && \
    conda env create -f /tmp/conda_env.yml && \
    conda clean -a -y

# Activate env and install pip packages
COPY requirements.txt /app/requirements.txt
RUN /opt/conda/envs/mistral-env/bin/pip install --no-cache-dir -r /app/requirements.txt

# Set environment path
ENV PATH="/opt/conda/envs/mistral-env/bin:$PATH"

# Copy source code (including score.py)
WORKDIR /app
COPY . /app

# Entry point for Azure ML (init + run style)
CMD ["python", "score.py"]