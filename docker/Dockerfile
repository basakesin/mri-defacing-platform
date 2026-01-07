# syntax=docker/dockerfile:1

# FSL içeren bir base image örneği (uygun tag seçin)
FROM neurodebian:bookworm-non-free

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Python + pip + temel paketler
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Eğer FSL bu base'de yoksa burada kurmanız gerekir (bu kısım dağıtıma göre değişir).
# Bazı base imajlarda FSL hazır gelir. Gelmiyorsa:
# RUN apt-get update && apt-get install -y fsl-core && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "2", "--threads", "4", "--timeout", "300"]
