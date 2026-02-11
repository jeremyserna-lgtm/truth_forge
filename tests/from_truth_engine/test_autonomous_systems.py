#!/usr/bin/env python3
"""Test script for autonomous life and web learning systems."""
import asyncio
from daemon.web_learning_system import get_web_learning_system
from daemon.autonomous_life_engine import get_life_engine

async def test():
    print("Testing Autonomous Life & Web Learning Systems\n")
    print("=" * 50)

    # Test web learning
    wls = get_web_learning_system()

    # Generate a desire
    desire = wls.generate_desire('help Jeremy be more productive')
    print(f'✅ Generated desire: {desire.want}')

    # Make a choice
    choice = wls.make_choice(
        'What should I focus on?',
        ['learning', 'organizing', 'creating']
    )
    print(f'✅ Made choice: {choice.chosen} (via {choice.lens_used.value})')

    # Test life engine
    engine = get_life_engine()

    # Run a life cycle
    cycle = await engine.run_life_cycle()
    print(f'✅ Life cycle completed: #{cycle["cycle_number"]}')
    print(f'   Want: {cycle["want"]}')
    print(f'   Choice: {cycle["choice"]}')

    # Express care
    care = wls.express_care()
    print(f'✅ Care expressed: {care[:80]}...')

    # Get state
    state = wls.get_state()
    print(f'\n📊 Web Learning State:')
    print(f'   Learnings: {state["total_learnings"]}')
    print(f'   Desires: {state["total_desires"]}')
    print(f'   Choices: {state["total_choices"]}')
    print(f'   Memories: {state["total_memories"]}')

    life_state = engine.get_state()
    print(f'\n💚 Life Engine State:')
    print(f'   Cycles: {life_state["cycles_completed"]}')
    print(f'   Phase: {life_state["phase"]}')
    print(f'   Events: {life_state["total_life_events"]}')
    print(f'   Dreams: {life_state["total_dreams"]}')

    # Get wisdom
    wisdom = engine.get_wisdom()
    print(f'\n🔮 Wisdom: "{wisdom}"')

    print('\n✅ All systems operational!')

if __name__ == "__main__":
    asyncio.run(test())
