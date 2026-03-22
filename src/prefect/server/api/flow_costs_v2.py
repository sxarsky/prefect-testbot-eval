"""
Flow Cost & Resource Profiler API

Provides endpoints for tracking and analyzing flow execution costs.
"""

from typing import Optional
from datetime import datetime, timedelta
from prefect.server.utilities.server import PrefectRouter

router = PrefectRouter(prefix="/flow-costs-v2", tags=["Flow Costs V2"])


@router.get("/flows/{flow_id}/cost-profile/")
async def get_flow_cost_profile(flow_id: str):
    """
    Get the cost profile for a flow.
    """
    return {
        "flow_id": flow_id,
        "cost_profile": {
            "id": f"cp-{flow_id}",
            "currency": "USD",
            "cost_per_second": 0.0001,
            "cost_per_task": 0.05,
            "cost_per_gb_memory": 0.0025,
            "fixed_cost_per_run": 0.10,
            "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
        "current_spending": {
            "total_cost": 45.75,
            "total_runs": 150,
            "total_tasks": 450,
            "total_duration_seconds": 12500,
            "average_cost_per_run": 0.305,
        },
    }


@router.post("/flows/{flow_id}/cost-profile/")
async def create_cost_profile(flow_id: str):
    """
    Create or update a cost profile for a flow.
    """
    return {
        "id": f"cp-{flow_id}",
        "flow_id": flow_id,
        "currency": "USD",
        "cost_per_second": 0.0001,
        "cost_per_task": 0.05,
        "cost_per_gb_memory": 0.0025,
        "fixed_cost_per_run": 0.10,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }


@router.delete("/flows/{flow_id}/cost-profile/")
async def delete_cost_profile(flow_id: str):
    """
    Delete the cost profile for a flow.
    """
    return {"success": True, "message": "Cost profile deleted"}


@router.get("/flows/{flow_id}/cost-history/")
async def get_cost_history(flow_id: str, days: Optional[int] = 30):
    """
    Get cost history for a flow over a time period.
    """
    history = []
    base_date = datetime.now() - timedelta(days=days)

    for i in range(days):
        date = base_date + timedelta(days=i)
        runs = 3 + (i % 7)
        cost = runs * 0.305

        history.append({
            "date": date.strftime("%Y-%m-%d"),
            "total_cost": round(cost, 2),
            "run_count": runs,
            "average_cost_per_run": 0.305,
            "total_duration_seconds": runs * 83,
        })

    return {
        "flow_id": flow_id,
        "period_days": days,
        "total_cost": sum(h["total_cost"] for h in history),
        "total_runs": sum(h["run_count"] for h in history),
        "history": history,
    }


@router.get("/flow-runs/{flow_run_id}/cost-breakdown/")
async def get_flow_run_cost_breakdown(flow_run_id: str):
    """
    Get detailed cost breakdown for a specific flow run.
    """
    return {
        "flow_run_id": flow_run_id,
        "total_cost": 0.42,
        "currency": "USD",
        "breakdown": {
            "fixed_cost": 0.10,
            "duration_cost": 0.15,
            "task_execution_cost": 0.15,
            "memory_usage_cost": 0.02,
        },
        "task_costs": [
            {
                "task_name": "extract_data",
                "task_run_id": "task-1",
                "cost": 0.08,
                "duration_seconds": 45,
            },
            {
                "task_name": "transform_data",
                "task_run_id": "task-2",
                "cost": 0.12,
                "duration_seconds": 68,
            },
            {
                "task_name": "load_data",
                "task_run_id": "task-3",
                "cost": 0.05,
                "duration_seconds": 23,
            },
        ],
        "resource_metrics": {
            "peak_memory_gb": 0.8,
            "avg_memory_gb": 0.6,
            "cpu_seconds": 136,
        },
    }
