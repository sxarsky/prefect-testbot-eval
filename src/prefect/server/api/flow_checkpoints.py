"""
Flow run checkpoints endpoints.
"""
from prefect.server.utilities.server import PrefectRouter

router = PrefectRouter(prefix="/flow-checkpoints", tags=["Flow Checkpoints"])


@router.get("/runs/{run_id}")
async def list_checkpoints(run_id: str):
    """Get all checkpoints for a run."""
    return {
        "run_id": run_id,
        "checkpoints": [
            {"id": "1", "task_name": "task-1", "timestamp": "2026-03-20T10:00:00Z"},
            {"id": "2", "task_name": "task-2", "timestamp": "2026-03-20T10:05:00Z"}
        ]
    }


@router.post("/runs/{run_id}")
async def create_checkpoint(run_id: str, task_name: str, state_data: dict):
    """Create a checkpoint."""
    return {
        "checkpoint_id": "new-checkpoint",
        "run_id": run_id,
        "task_name": task_name,
        "saved": True
    }


@router.post("/runs/{run_id}/restore")
async def restore_from_checkpoint(run_id: str, checkpoint_id: str):
    """Restore from a checkpoint."""
    return {
        "run_id": run_id,
        "checkpoint_id": checkpoint_id,
        "restored": True,
        "resume_task": "task-3"
    }
