import requests
from fastapi import FastAPI
from pydantic import BaseModel
from langchain import HuggingFaceHub, PromptTemplate, LLMChain
import chainlit as cl

# Définir le modèle des requêtes pour FastAPI
class QueryModel(BaseModel):
    question: str

# Créer une instance FastAPI
api = FastAPI()

# Remplacez par votre propre token d'accès Hugging Face
hf_api_token = "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"

# Utiliser le modèle GPT-2 depuis Hugging Face Hub
model_id = "gpt2"
llm = HuggingFaceHub(repo_id=model_id, huggingfacehub_api_token=hf_api_token, model_kwargs={"temperature": 0.5, "max_length": 100})

# Créer un template de prompt pour répondre aux questions sur les JO
prompt_template = """
You are a chatbot that provides information about the Paris Olympics.
Question: {question}
Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["question"])

# Créer la chaîne Langchain
chain = LLMChain(llm=llm, prompt=prompt)

# Fonction pour récupérer les événements culturels des JO 2024
def get_olympic_events(limit=20):
    url = "https://data.paris2024.org/api/explore/v2.1/catalog/datasets/paris-2024-evenements-olympiade-culturelle/records"
    params = {"limit": limit}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        events = data["records"]
        formatted_events = []
        for event in events:
            title = event["record"]["fields"].get("titre", "Titre inconnu")
            date = event["record"]["fields"].get("date", "Date inconnue")
            location = event["record"]["fields"].get("lieu", "Lieu inconnu")
            formatted_events.append(f"Titre : {title}, Date : {date}, Lieu : {location}")
        return "\n".join(formatted_events)
    else:
        return "Erreur lors de la récupération des événements."

# Fonction pour traiter les messages entrants via Chainlit
@cl.on_message
def main(question: str):
    # Si la question contient "événements", obtenir la liste des événements
    if "événements" in question.lower():
        events = get_olympic_events()
        return cl.Message(content=f"Voici les événements à venir des JO 2024 à Paris :\n\n{events}").send()
    else:
        response = chain.run(question=question)
        return cl.Message(content=response).send()

# Endpoint API pour poser des questions au chatbot
@api.post("/ask")
def ask_chatbot(query: QueryModel):
    if "événements" in query.question.lower():
        events = get_olympic_events()
        return {"response": f"Voici les événements à venir des JO 2024 à Paris :\n\n{events}"}
    else:
        response = chain.run(question=query.question)
        return {"response": response}

# Fonction pour lancer le serveur FastAPI
def start_fastapi():
    import uvicorn
    uvicorn.run(api, host="0.0.0.0", port=8000)

# Lancer FastAPI et Chainlit en parallèle
if __name__ == "__main__":
    import threading
    threading.Thread(target=start_fastapi).start()
    cl.run("app1.py", watch=True)
