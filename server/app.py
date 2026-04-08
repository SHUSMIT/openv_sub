"""
HuggingFace Spaces ASGI entrypoint.
This module exposes the FastAPI app for HF Spaces to load.
HF Spaces expects to find an 'app' attribute at the root level.

The README.md header sets: app_file: app.py, app_port: 7860
This file imports from server.app and runs uvicorn on port 7860.
"""

from server.app import app  # noqa: F401 — re-exported for uvicorn

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
