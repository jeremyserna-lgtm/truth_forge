"""Universal Script Self-Awareness.

RISK MITIGATION: Ensures that every operation contributes to the organism's
knowledge base by enforcing the HOLD-AGENT-HOLD pattern at the script level.

See MIGRATION_PLAN.md for full architectural details.
"""

from __future__ import annotations

import io
import sys
import traceback
from collections.abc import Callable
from datetime import UTC, datetime


def run_script_with_knowledge_capture(script_logic: Callable[[], None]) -> None:
    """Execute a script and capture its outcome for the organism's knowledge base.

    This function acts as the canonical entry point for all scripts.

    Execution Flow:
    1. HOLD 1 (Record Intent): Logs a `script_started` event to the `governance` service.
    2. AGENT (Execute & Capture): Executes the script, capturing stdout and exceptions.
    3. HOLD 2 (Record Outcome & Generate Knowledge):
        - Logs a `script_finished` event to `governance`.
        - Inhales the captured output into the `KnowledgeService` for processing.
    """
    from truth_forge.services.factory import get_service

    governance = get_service("governance")
    knowledge = get_service("knowledge")
    script_name = sys.argv[0]

    governance.inhale(
        {
            "event_type": "script_started",
            "script_name": script_name,
            "args": sys.argv[1:],
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    old_stdout = sys.stdout
    redirected_output = io.StringIO()
    sys.stdout = redirected_output

    status = "success"
    exception_info = None

    try:
        script_logic()
    except Exception:
        status = "failed"
        exception_info = traceback.format_exc()
        # Also print to stderr for immediate feedback
        print(exception_info, file=sys.stderr)
    finally:
        sys.stdout = old_stdout

    output = redirected_output.getvalue()

    governance.inhale(
        {
            "event_type": "script_finished",
            "script_name": script_name,
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
        }
    )

    knowledge.inhale(
        {
            "content": output,
            "source": f"script:{script_name}",
            "metadata": {
                "status": status,
                "exception": exception_info,
                "args": sys.argv[1:],
            },
        }
    )

    # Immediately process the knowledge to make it available
    knowledge.sync()

    # Print the captured output to the console
    print(output)
