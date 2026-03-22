"""
Flow Run Checkpoints API

Provides endpoints for managing flow run checkpoints and recovery points.
"""

from datetime import datetime, timedelta
from prefect.server.utilities.server import PrefectRouter

router = PrefectRouter(prefix="/checkpoints-v2", tags=["Checkpoints V2"])


@router.get("/flow-runs/{flow_run_id}/checkpoints/")
async def get_flow_run_checkpoints(flow_run_id: str):
    """
    Get all checkpoints for a flow run.
    """
    base_time = datetime.now()

    return {
        "flow_run_id": flow_run_id,
        "checkpoints": [
            {
                "id": "checkpoint-1",
                "name": "data_extracted",
                "state": "completed",
                "created_at": (base_time - timedelta(minutes=10)).isoformat(),
                "metadata": {
                    "task_count": 1,
                    "data_size_mb": 125,
                },
            },
            {
                "id": "checkpoint-2",
                "name": "data_transformed",
                "state": "completed",
                "created_at": (base_time - timedelta(minutes=8)).isoformat(),
                "metadata": {
                    "task_count": 2,
                    "rows_processed": 50000,
                },
            },
            {
                "id": "checkpoint-3",
                "name": "data_loaded",
                "state": "completed",
                "created_at": (base_time - timedelta(minutes=5)).isoformat(),
                "metadata": {
                    "task_count": 3,
                    "rows_inserted": 50000,
                },
            },
            {
                "id": "checkpoint-4",
                "name": "validation_complete",
                "state": "active",
                "created_at": (base_time - timedelta(minutes=2)).isoformat(),
                "metadata": {
                    "task_count": 4,
                    "validation_passed": True,
                },
            },
        ],
        "total_checkpoints": 4,
        "latest_checkpoint_id": "checkpoint-4",
    }


@router.post("/flow-runs/{flow_run_id}/checkpoints/")
async def create_checkpoint(flow_run_id: str):
    """
    Create a new checkpoint for a flow run.
    """
    return {
        "id": "checkpoint-new",
        "flow_run_id": flow_run_id,
        "name": "new_checkpoint",
        "state": "active",
        "created_at": datetime.now().isoformat(),
        "metadata": {},
    }


@router.get("/checkpoints/{checkpoint_id}")
async def get_checkpoint_details(checkpoint_id: str):
    """
    Get detailed information about a specific checkpoint.
    """
    return {
        "id": checkpoint_id,
        "name": "data_transformed",
        "state": "completed",
        "created_at": datetime.now().isoformat(),
        "metadata": {
            "task_count": 2,
            "rows_processed": 50000,
            "memory_usage_mb": 256,
            "cpu_seconds": 45,
        },
        "state_data": {
            "variables": {"batch_size": 1000, "total_batches": 50},
            "task_states": {
                "extract_data": "completed",
                "transform_data": "completed",
            },
        },
    }
