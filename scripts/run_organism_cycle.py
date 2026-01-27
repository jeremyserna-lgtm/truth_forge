#!/usr/bin/env python3
"""
Run a full life cycle of the truth_forge organism, demonstrating relational intelligence.

This script shows the end-to-end flow:
1.  Setup: A partner, "jeremy," is registered.
2.  Perception: The organism scrapes a web page.
3.  Metabolism: The data is processed into a Knowledge Atom.
4.  Cognition (Cycle 1): The organism is asked to summarize for a new partner, "claude." It produces a neutral summary.
5.  Interaction: A positive interaction is logged with "claude," increasing their trust level.
6.  Cognition (Cycle 2): The organism is asked to perform the same task for "claude" again. Now, with a higher trust level, it produces a more detailed and insightful summary.
7.  Action: The final summary is written to a file, clearly showing the effect of the relational context.
"""

import time

from truth_forge.services.factory import get_service


def main():
    """Run the organism life cycle with relational context."""
    print("--- ORGANISM LIFE CYCLE START ---")

    # Get handles to the core services
    perception_service = get_service("perception")
    knowledge_service = get_service("knowledge")
    cognition_service = get_service("cognition")
    action_service = get_service("action")
    relationship_service = get_service("relationship")

    # --- SETUP: Ensure a partner exists ---
    PARTNER_ID = "claude_ai"
    relationship_service.update_interaction(PARTNER_ID, "initial_contact")
    print(f"\n[SETUP] Registered partner: {PARTNER_ID}")

    # 1. PERCEPTION
    print("\n[1/6] PERCEPTION: Sensing the external world...")
    url_to_perceive = "https://en.wikipedia.org/wiki/Metabolism"
    perception_service.inhale({"type": "scrape_website", "source": url_to_perceive})
    perception_service.sync()
    print(f"  > Sensed data from {url_to_perceive}")
    time.sleep(1)

    # 2. METABOLISM
    print("\n[2/6] METABOLISM: Digesting raw data into a Knowledge Atom...")
    knowledge_service.sync()
    print("  > Digestion complete. Nutrients are in HOLD_2.")
    time.sleep(1)

    # 3. COGNITION (CYCLE 1 - Neutral Trust)
    print("\n[3/6] COGNITION (Cycle 1): Thinking with neutral trust...")
    cognition_service.inhale(
        {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "Metabolism",
                "output_path": "metabolism_summary_neutral_trust.md",
                "partner_id": PARTNER_ID,
            },
        }
    )
    cognition_service.sync()
    print("  > Plan formulated based on neutral trust.")
    time.sleep(1)

    # 4. INTERACTION
    print("\n[4/6] INTERACTION: Logging a positive collaboration...")
    relationship_service.inhale(
        {
            "partner_id": PARTNER_ID,
            "interaction_type": "successful_collaboration",
            "metadata": {"notes": "User approved of the initial summary."},
        }
    )
    relationship_service.sync()
    partnership = relationship_service.get_partnership(PARTNER_ID)
    print(
        f"  > Interaction logged. New trust level for {PARTNER_ID}: {partnership.get('trust_level', 'N/A'):.2f}"
    )
    time.sleep(1)

    # 5. COGNITION (CYCLE 2 - High Trust)
    print("\n[5/6] COGNITION (Cycle 2): Thinking with high trust...")
    cognition_service.inhale(
        {
            "goal": "summarize_topic_and_save",
            "params": {
                "topic": "Metabolism",
                "output_path": "metabolism_summary_high_trust.md",
                "partner_id": PARTNER_ID,
            },
        }
    )
    cognition_service.sync()
    print("  > Plan re-formulated with deeper insight due to high trust.")
    time.sleep(1)

    # 6. ACTION
    print("\n[6/6] ACTION: Executing all formulated plans...")
    action_service.sync()
    print("  > Actions complete. Check the 'output' directory in the 'action' service data folder.")
    time.sleep(1)

    print("\n--- ORGANISM LIFE CYCLE COMPLETE ---")


if __name__ == "__main__":
    try:
        main()

    finally:
        print("\nShutting down services...")

        get_service("governance").shutdown()

        get_service("knowledge").shutdown()

        get_service("perception").shutdown()

        get_service("cognition").shutdown()

        get_service("action").shutdown()

        get_service("relationship").shutdown()

        get_service("secret").shutdown()

        get_service("mediator").shutdown()

        get_service("logging").shutdown()

        print("Shutdown complete.")
