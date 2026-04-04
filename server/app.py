"""
FastAPI server for OpenEnv Email Triage Environment
Exposes /reset, /step, /state endpoints per OpenEnv spec
"""

import json
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from ..models import Action, Observation, Reward, State
    from ..environment import EmailTriageEnv
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from models import Action, Observation, Reward, State
    from environment import EmailTriageEnv

# Global environment instances (one per task)
environments: Dict[str, EmailTriageEnv] = {}

app = FastAPI(
    title="OpenEnv Email Triage",
    description="Real-world email triage environment for AI agent training",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_or_create_env(task_id: str, seed: Optional[int] = None) -> EmailTriageEnv:
    key = f"{task_id}_{seed}" if seed else task_id
    if key not in environments:
        environments[key] = EmailTriageEnv(task_id=task_id, seed=seed)
    return environments[key]


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "OpenEnv Email Triage",
        "tasks": [
            "email_priority_classification",
            "urgency_detection",
            "intelligent_routing",
        ],
    }


@app.post("/reset")
async def reset(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None,
):
    try:
        env = get_or_create_env(task_id, seed)
        obs = env.reset()
        return {"status": "success", "observation": json.loads(obs.model_dump_json())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/step")
async def step(
    task_id: str = "email_priority_classification",
    action: Dict[str, Any] = Body(...),
    seed: Optional[int] = None,
):
    try:
        env = get_or_create_env(task_id, seed)
        action_obj = Action(**action)
        obs, reward, info = env.step(action_obj)
        return {
            "status": "success",
            "observation": json.loads(obs.model_dump_json()),
            "reward": json.loads(reward.model_dump_json()),
            "info": info,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/state")
async def state(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None,
):
    try:
        env = get_or_create_env(task_id, seed)
        state_obj = env.state()
        return {"status": "success", "state": json.loads(state_obj.model_dump_json())}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/episode-summary")
async def episode_summary(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None,
):
    try:
        env = get_or_create_env(task_id, seed)
        summary = env.get_episode_summary()
        return {"status": "success", "summary": summary}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
async def list_tasks():
    return {
        "status": "success",
        "tasks": [
            {
                "id": "email_priority_classification",
                "name": "Email Priority Classification",
                "difficulty": "easy",
                "description": "Classify incoming emails by priority level (0-3 scale)",
            },
            {
                "id": "urgency_detection",
                "name": "Urgency & Escalation Detection",
                "difficulty": "medium",
                "description": "Detect urgency signals and recommend escalation",
            },
            {
                "id": "intelligent_routing",
                "name": "Intelligent Email Routing & Response",
                "difficulty": "hard",
                "description": "Route emails to correct team and compose responses",
            },
        ],
    }


@app.get("/")
async def root():
    return {
        "service": "OpenEnv Email Triage Environment",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "reset": "/reset",
            "step": "/step",
            "state": "/state",
            "episode_summary": "/episode-summary",
            "tasks": "/tasks",
        },
    }


def main():
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
