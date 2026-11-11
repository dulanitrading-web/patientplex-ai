"""PatientPlex AI Agent Registry.

Imports all 14 agents and provides lookup helpers.
"""
from app.services.agents.night_owl import NightOwl
from app.services.agents.lead_hunter import LeadHunter
from app.services.agents.sales_prep import SalesPrep
from app.services.agents.ads_optimizer import AdsOptimizer
from app.services.agents.csm_copilot import CSMCopilot
from app.services.agents.health_check import HealthCheck
from app.services.agents.seo_writer import SEOWriter
from app.services.agents.reel_writer import ReelWriter
from app.services.agents.onboarding_agent import OnboardingAgent
from app.services.agents.content_creator import ContentCreator
from app.services.agents.finance_bot import FinanceBot
from app.services.agents.devops_agent import DevOpsAgent
from app.services.agents.ml_trainer import MLTrainer
from app.services.agents.dashboard_agent import DashboardAgent

AGENT_REGISTRY: dict[str, type] = {
    "night_owl": NightOwl,
    "lead_hunter": LeadHunter,
    "sales_prep": SalesPrep,
    "ads_optimizer": AdsOptimizer,
    "csm_copilot": CSMCopilot,
    "health_check": HealthCheck,
    "seo_writer": SEOWriter,
    "reel_writer": ReelWriter,
    "onboarding_agent": OnboardingAgent,
    "content_creator": ContentCreator,
    "finance_bot": FinanceBot,
    "devops_agent": DevOpsAgent,
    "ml_trainer": MLTrainer,
    "dashboard_agent": DashboardAgent,
}


def get_agent(name: str):
    """Instantiate and return a named agent."""
    cls = AGENT_REGISTRY.get(name)
    if cls is None:
        available = ", ".join(sorted(AGENT_REGISTRY.keys()))
        raise ValueError(f"Unknown agent '{name}'. Available: {available}")
    return cls()


def get_all_agents() -> dict:
    """Return info dict for every registered agent."""
    return {name: cls().get_info() for name, cls in AGENT_REGISTRY.items()}
