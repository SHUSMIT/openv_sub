"""
FastAPI server for OpenEnv spec (HTTP endpoints)
Exposes /reset, /step, /state
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Dict, Any, Optional

from environment import EmailTriageEnv
from models import Action, Observation, Reward, State

# Global environment instances (one per task)
environments: Dict[str, EmailTriageEnv] = {}

app = FastAPI(
    title="OpenEnv Email Triage",
    description="Real-world email triage environment for AI agent training",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_or_create_env(task_id: str, seed: Optional[int] = None) -> EmailTriageEnv:
    """Get or create environment for task"""
    key = f"{task_id}_{seed}" if seed else task_id
    if key not in environments:
        environments[key] = EmailTriageEnv(task_id=task_id, seed=seed)
    return environments[key]


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "OpenEnv Email Triage",
        "tasks": [
            "email_priority_classification",
            "urgency_detection",
            "intelligent_routing"
        ]
    }


@app.post("/reset")
async def reset(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None
):
    """Reset environment for new episode"""
    try:
        try:
            env = get_or_create_env(task_id, seed)
        except Exception as e:
            print(f"[ERROR] Failed to get/create environment: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Environment creation failed: {str(e)}")
        
        try:
            obs = env.reset()
        except Exception as e:
            print(f"[ERROR] Failed to reset environment: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Reset failed: {str(e)}")
        
        try:
            return {
                "status": "success",
                "observation": json.loads(obs.model_dump_json()),
            }
        except Exception as e:
            print(f"[ERROR] Failed to serialize observation: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Serialization failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unhandled exception in /reset: {type(e).__name__}: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")


@app.post("/step")
async def step(
    task_id: str = "email_priority_classification",
    action: Dict[str, Any] = Body(...),
    seed: Optional[int] = None
):
    """Execute one environment step"""
    try:
        try:
            env = get_or_create_env(task_id, seed)
        except Exception as e:
            print(f"[ERROR] Failed to get environment in /step: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Environment error: {str(e)}")
        
        try:
            action_obj = Action(**action)
        except Exception as e:
            print(f"[ERROR] Failed to parse action: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Invalid action: {str(e)}")
        
        try:
            result = env.step(action_obj)
            if result is None or len(result) < 3:
                raise ValueError("Invalid environment step result")
            obs, reward, info = result
        except Exception as e:
            print(f"[ERROR] Failed to execute environment step: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Step failed: {str(e)}")

        try:
            return {
                "status": "success",
                "observation": json.loads(obs.model_dump_json()) if obs else None,
                "reward": json.loads(reward.model_dump_json()) if reward else None,
                "info": info if info else {},
            }
        except Exception as e:
            print(f"[ERROR] Failed to serialize step result: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Serialization failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unhandled exception in /step: {type(e).__name__}: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")


@app.get("/state")
async def state(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None
):
    """Get current environment state (read-only snapshot)"""
    try:
        try:
            env = get_or_create_env(task_id, seed)
        except Exception as e:
            print(f"[ERROR] Failed to get environment in /state: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Environment error: {str(e)}")
        
        try:
            state_obj = env.state()
        except Exception as e:
            print(f"[ERROR] Failed to get state: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"State retrieval failed: {str(e)}")
        
        try:
            return {
                "status": "success",
                "state": json.loads(state_obj.model_dump_json()) if state_obj else None,
            }
        except Exception as e:
            print(f"[ERROR] Failed to serialize state: {e}", flush=True)
            raise HTTPException(status_code=400, detail=f"Serialization failed: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] Unhandled exception in /state: {type(e).__name__}: {e}", flush=True)
        raise HTTPException(status_code=500, detail=f"Unhandled error: {str(e)}")


@app.get("/episode-summary")
async def episode_summary(
    task_id: str = "email_priority_classification",
    seed: Optional[int] = None
):
    """Get episode summary for completed episode"""
    try:
        env = get_or_create_env(task_id, seed)
        summary = env.get_episode_summary()
        return {
            "status": "success",
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/tasks")
async def list_tasks():
    """List available tasks"""
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
        ]
    }


@app.get("/")
async def root():
    """Root endpoint"""
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
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
