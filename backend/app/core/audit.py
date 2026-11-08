"""Audit logging for sensitive operations."""
import logging
from datetime import datetime, timezone

audit_logger = logging.getLogger("patientplex.audit")


def log_audit(action: str, actor_id: str = None, resource: str = None, details: dict = None):
    audit_logger.info(
        "AUDIT",
        extra={
            "action": action,
            "actor_id": str(actor_id) if actor_id else None,
            "resource": resource,
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
