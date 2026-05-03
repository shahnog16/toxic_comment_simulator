from fastapi import FastAPI
from pydantic import BaseModel
import sys
sys.path.append('..')
from database.db import create_table, log_result

app = FastAPI()
create_table()

class TextInput(BaseModel):
    text: str

@app.post("/moderate")
def moderate_text(input: TextInput):

    scores = {
        "toxic": 0.95,
        "severe_toxic": 0.10,
        "obscene": 0.80,
        "threat": 0.05,
        "insult": 0.88,
        "identity_hate": 0.02
    }

    if scores["toxic"] > 0.5:
        decision = "BLOCKED"
    else:
        decision = "APPROVED"

    log_result(input.text, scores, decision)

    return {
        "text": input.text,
        "scores": scores,
        "decision": decision
    }