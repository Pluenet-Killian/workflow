FROM debian:stable-slim

# Éviter les interactions pendant l'installation des paquets
ENV DEBIAN_FRONTEND=noninteractive

# Mise à jour et installation des dépendances
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    cmake \
    git \
    libssl-dev \
    zlib1g-dev \
    python3 \
    python3-pip \
    libcriterion-dev \
    xorg-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Création du répertoire de travail
RUN mkdir -p /workspace /app

# Copie du script entrypoint
COPY entrypoint.py /app/entrypoint.py

# Configuration du point d'entrée
ENTRYPOINT ["python3", "/app/entrypoint.py"]
