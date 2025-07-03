# Use the latest curated PyTorch + CUDA + Python 3.9 AzureML image
FROM mcr.microsoft.com/azureml/openmpi4.1.0-cuda11.8-cudnn8-ubuntu22.04

RUN apt-get update && apt-get install -y python3 python3-pip git

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

# Make start.sh executable
RUN chmod +x start.sh

ENV PYTHONPATH=.

EXPOSE 5001

# Entrypoint: Train if flag is set, otherwise start FastAPI
CMD ["bash", "start.sh"]