# 📑 Financial Policy Document Assistant

A Streamlit chatbot that answers questions about financial policy and compliance documents using **RAG (Retrieval-Augmented Generation)**. Upload a policy PDF, process it once, then ask questions in plain English. Answers come only from the document, with page citations.

**Tech stack:** Python · LangChain · OpenAI (embeddings + chat model) · ChromaDB · PyMuPDF · Streamlit

---

## How It Works

```
PDF ─► Load (PyMuPDF) ─► Chunk ─► Embed (OpenAI) ─► Store (ChromaDB)
                                                         │
Question ─► Retrieve relevant chunks ◄───────────────────┘
               │
               ▼
        Prompt + context ─► LLM (OpenAI) ─► Answer with page citations
```

---

## Prerequisites

- Python 3.11+
- An [OpenAI API key](https://platform.openai.com/api-keys)
- [uv](https://docs.astral.sh/uv/) (optional, for faster installs)

---

## Setup

### 1. Create a virtual environment

```bash
python -m venv venv
```

### 2. Activate the virtual environment

```bash
# macOS / Linux
source venv/bin/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
venv\Scripts\activate.bat
```

You'll see `(venv)` at the start of your terminal prompt when it's active.

### 3. Install dependencies

Make sure the virtual environment is **active** before installing, so packages go into `venv` and not your system Python.

```bash
uv pip install -r requirements.txt

# or, without uv
python -m pip install -r requirements.txt
```

When you add a new package, list it in `requirements.txt` and run the install command again.

### 4. Add your OpenAI API key

Create a `.env` file in the project root (copy `.env.example`):

```
OPENAI_API_KEY=sk-your-key-here
```

`.env` is listed in `.gitignore`, so your key is never pushed to GitHub.

---

## Run the App

```bash
python -m streamlit run app.py
```

Open http://localhost:8501, then:

1. **Upload** a financial policy PDF (a sample is in `data/sample_pdfs/`)
2. Click **Ingest/Process Document**
3. **Ask a question**, for example:
   - What is the main purpose of the Financial Policy and Procedures manual?
   - What are the quotation requirements based on purchase value?
   - Who are the current authorised bank signatories?

To stop the app, press `Ctrl+C` in the terminal.

---

## Deploy to Azure Web App (Azure Portal)

The app is deployed from the Azure Portal, with GitHub as the source. Every push to `main` redeploys automatically.

> **Before you start:** make sure your code is pushed to GitHub (`app.py`, `src/`, `requirements.txt` visible in the repo) and that GitHub Actions is available on your account (no billing lock, or the repo is public).

### 1. Create the Web App

In [portal.azure.com](https://portal.azure.com), go to **Create a resource → Web App** and fill in the **Basics** tab:

| Field | Value |
|---|---|
| Resource Group | Create new, e.g. `rg-financial-policy-bot` |
| Name | A unique name, e.g. `financial-policy-chatbot` (becomes the URL) |
| Publish | Code |
| Runtime stack | Python 3.11 |
| Operating System | **Linux** |
| Region | Central India (or nearest) |
| Pricing plan | **Basic B1** (Free F1 is too slow for ChromaDB) |

Click **Review + create → Create**, wait for *"Your deployment is complete"*, then click **Go to resource**.

### 2. Add environment variables

**Settings → Environment variables → App settings → + Add**

| Name | Value |
|---|---|
| `OPENAI_API_KEY` | your OpenAI API key |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` |

Click **Apply**, then confirm the restart.

### 3. Set the startup command and enable web sockets

**Settings → Configuration → General settings**

- **Startup Command:**
  ```bash
  python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0 --server.headless true
  ```
- **Web sockets:** **On** (Streamlit needs this, otherwise the page stays blank)

Click **Save → Continue**.

### 4. Connect GitHub

**Deployment → Deployment Center**

| Field | Value |
|---|---|
| Source | GitHub (click **Authorize** and sign in) |
| Organization | your GitHub account |
| Repository | this repository |
| Branch | `main` |
| Authentication | User-assigned identity (default) |

Click **Save**. Azure adds a workflow file under `.github/workflows/` in your repo and starts the first deployment.

### 5. Watch the deployment

Open the **Logs** tab in Deployment Center, or the **Actions** tab in your GitHub repo. Wait for the **build** and **deploy** jobs to show green ticks. This takes about 5–10 minutes because `chromadb` is large.

### 6. Open and test the app

Go to **Overview** and click the **Default domain** link (`https://<app-name>.azurewebsites.net`). The first load can take a minute.

Upload the policy PDF, click **Ingest/Process Document**, then ask a question.

> The `db/` folder is not stored in Git, so process the document once after each fresh deployment.

### Azure troubleshooting

Check **Monitoring → Log stream** for errors.

| Symptom | Fix |
|---|---|
| "Application Error" or the container keeps restarting | Check the startup command in step 3 |
| Page loads but stays blank or keeps reconnecting | Turn **Web sockets** On |
| `ModuleNotFoundError` | Set `SCM_DO_BUILD_DURING_DEPLOYMENT=true` and redeploy |
| OpenAI authentication error | Check the `OPENAI_API_KEY` app setting |
| GitHub job "not started … billing issue" | Fix billing in GitHub **Settings → Billing**, or make the repo public |

---

## Project Structure

```
├── app.py                    # Streamlit UI (upload, ingest, Q&A)
├── src/
│   ├── config_loader.py      # Reads config/config.yaml
│   ├── document_loaders.py   # PDF → pages (PyMuPDF)
│   ├── chunking.py           # Pages → chunks
│   ├── embeddings.py         # OpenAI embedding model
│   ├── vectorstore.py        # ChromaDB create / load / retriever
│   ├── llm_integration.py    # OpenAI chat model
│   └── rag_pipeline.py       # indexing_pipeline() and get_answer()
├── prompts/
│   └── prompt_template.py    # System prompt + message builder
├── config/
│   └── config.yaml           # Models, chunk size, retriever settings
├── data/sample_pdfs/         # Uploaded / sample PDFs
├── exploration/
│   └── notebook.ipynb        # Step-by-step RAG notebook
├── requirements.txt
└── .env.example
```

---

## Development Workflow

1. **Explore:** build and test each RAG step in `exploration/notebook.ipynb`
2. **Modularise:** move each step into its own file under `src/`
3. **Configure:** keep model names and settings in `config/config.yaml`
4. **Build the UI:** connect the pipeline to the Streamlit app in `app.py`

---

## Configuration

Edit `config/config.yaml` to change:

| Setting | Default |
|---|---|
| Chat model | `gpt-5.5`, temperature 0 |
| Embedding model | `text-embedding-ada-002` |
| Chunk size / overlap | 1000 / 200 |
| Retriever | similarity search, top 10 chunks |
| Vector store folder | `db/` |

If you change the embedding model, delete the `db/` folder and process the documents again.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `pip.exe` / `streamlit.exe` blocked on Windows | Use `python -m pip ...` and `python -m streamlit run app.py` |
| `DLL load failed ... Application Control policy` | Windows Smart App Control is blocking a compiled package. Turn it off, or run the project in WSL / GitHub Codespaces |
| Duplicate answers after re-processing | Delete the `db/` folder and process the PDF once |
| `OPENAI_API_KEY not found` | Check that `.env` exists in the project root and contains your key |

---

**Author:** Ajeetkumar
