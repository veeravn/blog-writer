# Base CUDA + Python image
FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install tini and system packages
RUN apt-get update && apt-get install -y \
    wget curl git ca-certificates build-essential \
    libglib2.0-0 libxext6 libsm6 libxrender1 libssl-dev \
    libsndfile1 libbz2-dev liblzma-dev libffi-dev \
    libgl1 libgl1-mesa-glx tini \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
    bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh

ENV PATH=/opt/conda/bin:$PATH

# Copy conda env and install
COPY conda_env.yml /tmp/conda_env.yml
RUN conda update -n base -c defaults conda && \
    conda env create -f /tmp/conda_env.yml && \
    conda clean -a -y

# Activate environment by default
ENV PATH="/opt/conda/envs/mistral-env/bin:$PATH"

# Install pip dependencies into env
COPY requirements.txt /app/requirements.txt
RUN /opt/conda/envs/mistral-env/bin/pip install -r /app/requirements.txt

# Set env path
ENV PATH="/opt/conda/envs/mistral-env/bin:$PATH"

# Set workdir and copy app code
WORKDIR /app
COPY . /app

# Expose port
EXPOSE 5001
ENV PORT=5001

# Set tini as init process and start uvicorn
# ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5001"]
