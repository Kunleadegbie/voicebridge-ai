FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 AS base-check

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 python3-pip ffmpeg ca-certificates && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

FROM base-check AS production

WORKDIR /workspace

COPY deployment/runpod-asr/build/requirements.txt ./requirements.txt

RUN python3 -m pip install --no-cache-dir \
    torch==2.5.1+cu124 \
    --index-url https://download.pytorch.org/whl/cu124

RUN python3 -m pip install --no-cache-dir -r requirements.txt

COPY deployment/runpod-asr/build/worker.py ./worker.py
COPY deployment/runpod-asr/build/app/services/audio.py ./app/services/audio.py
COPY deployment/runpod-asr/build/app/services/asr_registry.py ./app/services/asr_registry.py

RUN touch app/__init__.py app/services/__init__.py

CMD ["python3", "-u", "worker.py"]



