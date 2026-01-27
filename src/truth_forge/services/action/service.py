"""Action Service.

The motor system of the organism.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from truth_forge.services.base import BaseService, MediatorProtocol
from truth_forge.services.factory import get_service, register_service


@register_service()
class ActionService(BaseService):
    """A service for executing actions on the external world."""

    service_name = "action"
    mediator: MediatorProtocol  # Type annotation for the mediator

    def on_startup(self) -> None:
        """Initialize the service."""
        self.mediator = cast("MediatorProtocol", get_service("mediator"))
        # Define safe output directories within the service's data folder
        self.output_dir = self._paths["root"] / "output"
        self.sent_emails_dir = self._paths["root"] / "sent_emails"
        self.output_dir.mkdir(exist_ok=True)
        self.sent_emails_dir.mkdir(exist_ok=True)

    def process(self, record: dict[str, Any]) -> dict[str, Any]:
        """Processes an action command received via inhale."""
        action = record.get("action")
        params = record.get("params", {})
        result_status = "failed"
        result_payload = {}

        try:
            if action == "write_file":
                result_payload = self._write_file(**params)
                result_status = "success"
            elif action == "send_email":
                result_payload = self._send_email(**params)
                result_status = "success"
            else:
                self.logger.warning("unknown_action", action=action)
                result_payload = {"error": f"Unknown action: {action}"}

        except Exception as e:
            self.logger.error("action_failed", action=action, error=str(e))
            result_payload = {"error": str(e)}

        # Publish the result for governance
        self.mediator.publish(
            "governance.record",
            {
                "event_type": "action_executed",
                "service": self.service_name,
                "action": action,
                "params": params,
                "result_status": result_status,
                "result_payload": result_payload,
            },
        )
        return record

    def _send_email(self, to: str, subject: str, body: str, **kwargs: Any) -> dict[str, str]:
        """
        Saves an email as a text file to a designated 'sent_emails' directory
        instead of sending it over the network.
        """
        if not all([to, subject, body]):
            raise ValueError("Email requires 'to', 'subject', and 'body'.")

        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{to}_{subject}.eml"
        safe_filename = "".join(c if c.isalnum() or c in "._-" else "_" for c in filename)
        filepath = self.sent_emails_dir / safe_filename

        email_content = f"To: {to}\nSubject: {subject}\n\n{body}"
        filepath.write_text(email_content, encoding="utf-8")

        self.logger.info("email_saved", path=str(filepath))
        return {"status": "email_saved", "path": str(filepath)}

    def _write_file(self, path: str, content: str, **kwargs: Any) -> dict[str, str]:
        """
        Writes a file to a safe, designated output directory within the service's
        data root to prevent arbitrary file writes.
        """
        if not all([path, content]):
            raise ValueError("File write requires 'path' and 'content'.")

        # Sanitize filepath to prevent directory traversal
        safe_basename = Path(path).name
        filepath = self.output_dir / safe_basename

        filepath.write_text(content, encoding="utf-8")
        self.logger.info("file_written", path=str(filepath))
        return {"status": "file_written", "path": str(filepath)}
