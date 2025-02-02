# Image de base Python
FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers requirements
COPY requirements.txt .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code source
COPY src/ .

# Variables d'environnement par défaut
ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=fleet_control.settings \
    DB_NAME=postgres \
    DB_USER=postgres \
    DB_PASSWORD=postgres \
    DB_HOST=localhost \
    DB_PORT=5432 \
    STRIPE_SECRET_KEY=sk_test_dummy \
    STRIPE_PUBLISHABLE_KEY=pk_test_dummy \
    STRIPE_WEBHOOK_SECRET=whsec_dummy

# Port à exposer
EXPOSE 8000

# Commande de démarrage
CMD ["gunicorn", "fleet_control.wsgi:application", "--bind", "0.0.0.0:8000"]
