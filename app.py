import requests
from fastapi import FastAPI
from pydantic import BaseModel
from langchain import HuggingFaceHub, PromptTemplate, LLMChain
import chainlit as cl

class QueryModel(BaseModel):
    question: str

api = FastAPI()

hf_api_token = "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"

model_id = "gpt2"
llm = HuggingFaceHub(repo_id=model_id, huggingfacehub_api_token=hf_api_token, model_kwargs={"temperature": 0.5, "max_length": 100})

prompt_template = """
You are a chatbot that provides information about the Paris Olympics.
Question: {question}
Answer:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["question"])
chain = LLMChain(llm=llm, prompt=prompt)

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

@cl.on_message
def main(question: str):
    if "événements" in question.lower():
        events = get_olympic_events()
        return cl.Message(content=f"Voici les événements à venir des JO 2024 à Paris :\n\n{events}").send()
    else:
        response = chain.run(question=question)
        return cl.Message(content=response).send()

@api.post("/ask")
def ask_chatbot(query: QueryModel):
    if "événements" in query.question.lower():
        events = get_olympic_events()
        return {"response": f"Voici les événements à venir des JO 2024 à Paris :\n\n{events}"}
    else:
        response = chain.run(question=query.question)
        return {"response": response}

def start_fastapi():
    import uvicorn
    uvicorn.run(api, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    import threading
    threading.Thread(target=start_fastapi).start()
    cl.run("app.py", watch=True)
