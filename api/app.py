from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
import sys


sys.path.append('..')
from database.db import create_table, log_result

app = FastAPI()
create_table()

MODEL_PATH = "../data/civicguard_distilbert"

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)

model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_PATH
)

model.eval()

label_mapping = {
    "LABEL_0": "toxic",
    "LABEL_1": "severe_toxic",
    "LABEL_2": "obscene",
    "LABEL_3": "threat",
    "LABEL_4": "insult",
    "LABEL_5": "identity_hate"
}


class TextInput(BaseModel):
    text: str


def predict_text(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    inputs.pop("token_type_ids", None)

    with torch.no_grad():
        outputs = model(**inputs)

    probabilities = torch.sigmoid(outputs.logits)[0]

    scores = {}

    for i, score in enumerate(probabilities):
        scores[label_mapping[f"LABEL_{i}"]] = round(
            float(score),
            4
        )

    return scores


@app.post("/moderate")
def moderate_text(input: TextInput):

    print("MODEL IS RUNNING")
    scores = predict_text(input.text)

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
