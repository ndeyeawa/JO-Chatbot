from flask import Flask, request, jsonify
import requests
import logging
from flasgger import Swagger, swag_from
from pydantic import BaseModel, ValidationError

app = Flask(__name__)
swagger = Swagger(app)

# Configuration du logger
logging.basicConfig(level=logging.INFO)

# Votre token API de Hugging Face
API_TOKEN = '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'
# URL de l'API Hugging Face pour le modèle de question-réponse
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/deepset/roberta-base-squad2"

headers = {"Authorization": f"Bearer {API_TOKEN}"}

class QueryModel(BaseModel):
    question: str

@app.route('/ask', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'La réponse du modèle Hugging Face',
            'examples': {
                'application/json': {
                    'answer': 'Les Jeux Olympiques auront lieu en 2024.',
                    'score': 0.98
                }
            }
        },
        400: {
            'description': 'Requête incorrecte (exemple : question non fournie)',
            'examples': {
                'application/json': {
                    'error': 'Veuillez fournir une question.'
                }
            }
        },
        500: {
            'description': 'Erreur interne du serveur ou problème avec l\'API de Hugging Face',
            'examples': {
                'application/json': {
                    'error': 'Failed to fetch response from the Hugging Face model'
                }
            }
        }
    }
})
def ask():
    try:
        # Valider les données entrantes
        content = request.json
        query = QueryModel(**content)
    except ValidationError as e:
        app.logger.error("Invalid request: %s", e)
        return jsonify({'error': 'Invalid request', 'details': str(e)}), 400

    # Préparer les données pour le modèle de question-réponse avec un contexte sur les JO de 2024
    data = {
        "inputs": {
            "question": query.question,
            "context": "Les Jeux Olympiques d'été 2024 se tiendront à Paris, France. Cet événement comprendra de nombreux sports, y compris l'athlétisme, la natation, et le cyclisme."
        }
    }

    # Appeler l'API de Hugging Face
    try:
        model_response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=data)
        model_response.raise_for_status()  # Cela va lever une exception si le statut n'est pas 200
        return jsonify(model_response.json())
    except requests.RequestException as e:
        error_message = str(e)
        app.logger.error(f"Failed to fetch response from the Hugging Face model: {error_message}")
        status_code = getattr(e.response, 'status_code', 500)
        return jsonify({'error': 'Failed to fetch response from the Hugging Face model', 'details': error_message}), status_code

if __name__ == '__main__':
    app.run(debug=True)
