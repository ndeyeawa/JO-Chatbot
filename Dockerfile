# Utiliser une image Python comme base
FROM python:3.9

# Créer un répertoire pour l'application
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel Flask écoute
EXPOSE 5000

# Démarrer l'application
CMD ["python", "flaskApp.py"]
