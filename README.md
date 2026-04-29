# AnimateDiff Text-to-Video Web App

## Local Execution Instructions

### 1. Start the Backend (FastAPI)
Navigate to the project root and run:
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend (Streamlit)
In a new terminal, run:
```bash
streamlit run frontend/app.py
```

## Hugging Face Spaces Deployment

To deploy this application to Hugging Face Spaces:

1. **Create a new Space**: Choose the **Streamlit** SDK or **Docker**.
2. **System Dependencies**: If using the Streamlit SDK, create a `packages.txt` file in the root with:
   ```text
   ffmpeg
   aria2
   git-lfs
   ```
3. **Model Weights**: Ensure your deployment script or Dockerfile handles downloading the required weights into the `models/` directory.
4. **GPU Requirement**: Since AnimateDiff requires CUDA, ensure the Space is running on a GPU instance (e.g., T4 small or larger).