# FleetControl
![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Hxagow/FleetControl?sort=semver&logo=github)

## Installation

### Prérequis

1. Installer Python (3.8 ou supérieur)
2. Installer Node.js et npm
3. Installer PostgreSQL

### Configuration de la base de données

1. Créer une base de données PostgreSQL
2. Copier le fichier `.env.example` en `.env` :
```bash
cp .env.example .env
```
3. Modifier le fichier `.env` avec vos paramètres :
   - Générer une `SECRET_KEY` sécurisée
   - Configurer les informations de connexion à la base de données (`DB_NAME`, `DB_USER`, `DB_PASSWORD`)
   - (Optionnel) Configurer les paramètres email si nécessaire

### Installation de l'environnement virtuel

Windows :
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux :
```bash
python -m venv venv
source venv/bin/activate
```

### Installation des dépendances

```bash
pip install -r requirements.txt
cd src/frontend
npm install
```

### Initialisation de la base de données

```bash
cd src
python manage.py migrate
python manage.py createsuperuser
```

## Développement

Django :
```bash
cd src
python manage.py runserver
```

Tailwind :
```bash
cd src/frontend
npm run dev
```

## Problèmes connus

### Windows
- Si l'installation de `psycopg2-binary` échoue, installez `psycopg2` à la place :
```bash
pip install psycopg2
```

### PostgreSQL
- Assurez-vous que PostgreSQL est en cours d'exécution avant de lancer l'application
- Vérifiez que l'utilisateur PostgreSQL a les droits nécessaires pour créer des bases de données