---
title: CivicGuard Toxic Comment Simulator
emoji: 🛡️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: "1.58.0"
python_version: "3.10.0"
app_file: app.py
pinned: false
---

# 🛡️ CivicGuard: Toxic Comment Simulator

An AI-powered content moderation engine and civility analysis dashboard designed to flag toxic inputs and safeguard community discussions. Powered by **DistilBERT** for real-time sequence classification and **Streamlit** for visual analysis.

---

## 🚀 One-Click Cloud Deployment

We have optimized this codebase with a unified `app.py` entrypoint in the root, enabling **instant cloud deployment** using the most popular free platforms!

### Option A: Deploy to Hugging Face Spaces (100% Free - Recommended)
Hugging Face Spaces provides up to 16GB of RAM, making it perfect for running this deep learning model smoothly.
1. Sign in to [Hugging Face](https://huggingface.co/).
2. Create a new Space: Click **New Space** -> Name it -> Select **Streamlit** as the SDK -> Choose the **Free CPU Basic (16GB RAM)** tier.
3. Choose **Import from GitHub** and paste your repository link:
   `https://github.com/shahnog16/toxic_comment_simulator.git`
4. Hugging Face will automatically download the repository, set up the environment, and launch your dashboard!

### Option B: Deploy to Streamlit Community Cloud (Free)
1. Go to [Streamlit Share](https://share.streamlit.io/).
2. Click **New App** -> Choose your GitHub repository (`toxic_comment_simulator`).
3. Set the Main File Path to: `app.py`.
4. Click **Deploy!**

---

## ⚡ How to Push this Code to your GitHub Repository

Since the git origin has been successfully configured in this folder to point to `https://github.com/shahnog16/toxic_comment_simulator.git`, you can push all files directly using your **VSCode Source Control panel**:

1. Click on the **Source Control icon** in the left sidebar of VSCode (or press `Ctrl+Shift+G`).
2. You will see the list of new and modified files. Type a commit message (e.g. `Initial commit: unified deployment-ready model and dashboard`) in the text field at the top.
3. Click the arrow next to the **Commit** button and select **Commit & Push** (or click **Commit** and then click the **Sync Changes** button).
4. VSCode will securely upload all files to your repository!

---

## 💻 Local Execution Instructions

If you want to run this application locally on your machine, you can run either the single-process version or the split API-and-dashboard version:

### 1. Simple Single-Process Execution (Recommended)
This runs the dashboard and the AI model together in a single window, exactly like the cloud deployment:
```powershell
# 1. Navigate to the project folder
cd "C:\Users\Windows\Desktop\ai proj\CivicGuard"

# 2. Activate the virtual environment
.venv\Scripts\Activate.ps1

# 3. Run the application
streamlit run app.py
```

### 2. Multi-Service API & Dashboard Execution
If you want to run the FastAPI backend server separately from the Streamlit frontend:
* **Terminal 1 (Start FastAPI Backend):**
  ```powershell
  cd "C:\Users\Windows\Desktop\ai proj\CivicGuard\api"
  ..\.venv\Scripts\python -m uvicorn main:app --host 127.0.0.1 --port 8000
  ```
* **Terminal 2 (Start Streamlit Frontend):**
  ```powershell
  cd "C:\Users\Windows\Desktop\ai proj\CivicGuard"
  .venv\Scripts\streamlit run dashboard/dashboard_app.py
  ```

---

## 🛠️ Project Structure

```bash
CivicGuard/
├── app.py                      # Unified Deployment Entrypoint (Streamlit + Model Inference)
├── api/
│   └── main.py                 # FastAPI Backend API Server (was api/app.py)
├── dashboard/
│   └── dashboard_app.py        # Streamlit Frontend Dashboard (API requester, was dashboard/app.py)
├── data/
│   └── civicguard_distilbert/  # Pre-trained DistilBERT PyTorch Model & Tokenizer files
├── database/
│   ├── db.py                   # SQLite Connection & Schema management
│   └── civicguard.db           # SQLite database holding audit logs
├── DEPLOYMENT.md               # Detailed technical deployment guide
├── requirements.txt            # System dependencies
└── README.md                   # This overview guide
```
