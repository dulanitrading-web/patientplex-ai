"""PatientPlex AI — Agents API Router.

Provides endpoints to list, trigger, and monitor all 14 AI agents.
Mount this in main.py: app.include_router(agents_router, prefix=settings.API_V1_PREFIX)
"""
import asyncio
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.agents import AGENT_REGISTRY, get_agent, get_all_agents

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agents", tags=["agents"])

# In-memory run history (replace with DB when PostgreSQL is connected)
_run_history: list[dict] = []


@router.get("/")
async def list_agents():
    """List all registered AI agents with their info and status."""
    agents_info = get_all_agents()
    return {
        "total": len(agents_info),
        "agents": agents_info,
        "note": "All agents default to demo_mode=True until real API credentials are configured.",
    }


@router.get("/{agent_name}")
async def get_agent_info(agent_name: str):
    """Get detailed info about a specific agent."""
    try:
        agent = get_agent(agent_name)
        return agent.get_info()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{agent_name}/run")
async def run_agent(agent_name: str):
    """Manually trigger an agent run. Returns the result immediately."""
    try:
        agent = get_agent(agent_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        result = await agent.execute(triggered_by="api")
        _run_history.append({
            "agent": agent_name,
            "triggered_by": "api",
            "status": "completed",
            "run_at": datetime.utcnow().isoformat(),
            "result_summary": str(result.get("result", {}).get("mode", "unknown")),
        })
        return result
    except Exception as e:
        _run_history.append({
            "agent": agent_name,
            "triggered_by": "api",
            "status": "failed",
            "run_at": datetime.utcnow().isoformat(),
            "error": str(e),
        })
        raise HTTPException(status_code=500, detail=f"Agent run failed: {e}")


@router.get("/{agent_name}/history")
async def get_agent_history(agent_name: str, limit: int = Query(default=10, le=100)):
    """Get recent run history for an agent."""
    history = [r for r in _run_history if r["agent"] == agent_name]
    return {"agent": agent_name, "runs": history[-limit:], "total": len(history)}


@router.get("/dashboard/overview")
async def agents_dashboard():
    """Dashboard overview: all agents, their schedules, and last run status."""
    agents_info = get_all_agents()
    last_runs = {}
    for run in _run_history:
        name = run["agent"]
        if name not in last_runs or run["run_at"] > last_runs[name]["run_at"]:
            last_runs[name] = run

    dashboard = []
    for name, info in agents_info.items():
        entry = {**info, "last_run": last_runs.get(name)}
        dashboard.append(entry)

    return {
        "total_agents": len(dashboard),
        "agents": dashboard,
        "total_runs": len(_run_history),
        "system_status": "operational",
        "demo_mode": True,
        "note": "Agents are in demo mode. Connect real API credentials to enable production runs.",
    }
