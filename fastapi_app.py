from fastapi import FastAPI
from pydantic import BaseModel

class QueryModel(BaseModel):
    question: str

api = FastAPI()

@api.post("/ask")
def ask_chatbot(query: QueryModel):
    return {"response": f"Voici votre question : {query.question}"}
