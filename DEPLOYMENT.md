# CivicGuard Deployment Guide

This guide provides instructions on how to rerun the **FastAPI Backend** and **Streamlit Frontend** locally, as well as set them up from scratch.

---

## ⚡ Quick Rerun/Restart Instructions (Local Machine)

If you have already set up the environment and installed the dependencies, follow these steps to quickly rerun the code on your local machine:

### 1. Start the FastAPI Backend
Open a terminal in the `CivicGuard` directory and run:
```powershell
cd api
..\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
*(Keep this terminal open to keep the backend server running).*

### 2. Start the Streamlit Frontend Dashboard
Open a **second terminal window** in the `CivicGuard` directory and run:
```powershell
.venv\Scripts\streamlit run dashboard/app.py
```
This will automatically launch the web dashboard in your browser.

---

## System Architecture Overview

CivicGuard is composed of three main components:
1. **Backend Engine (`api/app.py`)**: A FastAPI application that loads a local DistilBERT sequence classification model to moderate and score inputs for toxicity, threats, obscenity, insults, and identity hate.
2. **Database Module (`database/db.py`)**: An SQLite-based storage engine that keeps logs of all comments, scores, and decisions.
3. **Frontend Dashboard (`dashboard/app.py`)**: A Streamlit dashboard that presents aggregate metrics, recent logs, and a text analysis interface connecting to the FastAPI backend.

---

## 1. Local Development / Quickstart Setup

Follow these steps to set up and run the entire stack locally.

### Step 1: Clone or Navigate to the Directory
Open a terminal (such as PowerShell or Bash) and navigate to the project directory:
```powershell
cd "C:\Users\Windows\Desktop\ai proj\CivicGuard"
```

### Step 2: Set up a Virtual Environment
Create and activate an isolated virtual environment to manage dependencies:
```powershell
# Create the environment
python -m venv .venv

# Activate it (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate it (Windows Command Prompt)
.venv\Scripts\activate.bat

# Activate it (Linux/macOS)
source .venv/bin/activate
```

### Step 3: Install Dependencies
Install all required libraries (using a CPU-only PyTorch index to keep the installation lightweight and fast):
```powershell
pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

---

## 2. Running & Deploying the Backend (FastAPI)

The backend handles model inference and database logging. It must run on port `8000`.

### Running Locally
To launch the FastAPI server locally, navigate to the `api` directory and run:
```powershell
cd api
..\.venv\Scripts\python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
*Note: If you run it from the `api` directory, relative paths to the model directory (`../data/civicguard_distilbert`) will resolve correctly.*

### Verifying the Backend API
You can verify the backend is running by testing it with `PowerShell` or `curl`:

**Test moderation request:**
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/moderate" -Method Post -ContentType "application/json" -Body '{"text": "This is a clean and civil test comment."}'
```

**View API documentation:**
Navigate to [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your web browser.

---

## 3. Running & Deploying the Frontend (Streamlit)

The frontend connects to the backend and the SQLite database.

### Running Locally
From the `CivicGuard` main directory, run:
```powershell
.venv\Scripts\streamlit run dashboard/app.py
```
This will automatically launch the web dashboard in your browser (usually at `http://localhost:8501`).

---

## 4. Production Deployment Considerations

When moving this application to production, consider the following strategies:

### A. Deploying via Docker (Recommended)
You can containerize both applications. Create two separate `Dockerfile` configs or use `docker-compose`:

**Sample `docker-compose.yml` Structure:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: api/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - db-data:/app/database

  frontend:
    build:
      context: .
      dockerfile: dashboard/Dockerfile
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000
    volumes:
      - db-data:/app/database

volumes:
  db-data:
```

### B. Deploying Backend to Cloud Platforms (AWS, GCP, Azure, Render)
- **FastAPI Backend**: Can be deployed to AWS ECS, Google Cloud Run, or Render as a web service. 
- Ensure that the model directory (`data/civicguard_distilbert`) is packaged into the Docker container or loaded from an external storage bucket (like AWS S3 or Google Cloud Storage) during startup to avoid large image sizes.

### C. Deploying Frontend to Streamlit Community Cloud
- You can deploy the frontend directly to the [Streamlit Community Cloud](https://streamlit.io/cloud) by linking it with your GitHub repository.
- Ensure the backend service URL is exposed and configure the connection string inside your Streamlit secrets manager.
