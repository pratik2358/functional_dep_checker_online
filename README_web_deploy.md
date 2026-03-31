# Functional Dependency Explorer

This repository contains a Streamlit web app for teaching and experimenting with functional dependencies.
It exposes the repository's main notebook functionality through an online interface.

## Features

- Compute attribute closures
- Compute all closures
- Find candidate keys
- Find prime attributes
- Compute a minimal cover
- Project dependencies onto a sub-relation
- Discover functional dependencies from a relation
- Generate random FD instances

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Put it on GitHub and run it online

GitHub Pages cannot host this app because it needs Python execution on the server.
The simplest GitHub-based deployment is **Streamlit Community Cloud**.

### 1. Push this repository to GitHub

Create a new GitHub repository and push these files:

```bash
git init
git add .
git commit -m "Add Streamlit web interface"
git branch -M main
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy from GitHub

1. Go to Streamlit Community Cloud.
2. Sign in with GitHub.
3. Click **Create app**.
4. Select your repository.
5. Set:
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. Click **Deploy**.

After deployment, you will get a public URL that students can open directly.

## Recommended repository layout

- `app.py` — main web interface
- `web_helpers.py` — parsing and formatting helpers for the web app
- `utils.py` — original FD logic used by the notebooks and app
- `.streamlit/config.toml` — Streamlit configuration
- `requirements.txt` — dependencies for local and cloud deployment
- `runtime.txt` — Python runtime for deployment compatibility

## Notes

- The app uses the same Python logic as the notebooks.
- If you later want a custom domain, Streamlit Cloud supports that through its settings.
- If you want a fully self-hosted deployment later, this can also be deployed on Hugging Face Spaces, Render, or a small VPS.
