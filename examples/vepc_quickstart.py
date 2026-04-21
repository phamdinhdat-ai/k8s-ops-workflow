"""
vEPC Workflow - Quick Start Guide

This script demonstrates how to use the vEPC workflow for common tasks.
"""

import asyncio
from workflows.vepc import run_vepc_workflow


async def example_show_configuration():
    """Example: Show current configuration (read-only)."""
    print("\n" + "="*60)
    print("Example 1: Show Configuration")
    print("="*60)

    result = await run_vepc_workflow(
        user_query="Show me the current MCC, MNC and MME code",
        language="en"
    )

    print(f"\nIntent: {result['intent']}")
    print(f"CLI Commands: {result['cli_commands']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"\nResponse:\n{result['final_response']}")


async def example_update_configuration():
    """Example: Update configuration with risk assessment."""
    print("\n" + "="*60)
    print("Example 2: Update Configuration")
    print("="*60)

    result = await run_vepc_workflow(
        user_query="Set timer T3412 to 60 minutes",
        language="en"
    )

    print(f"\nIntent: {result['intent']}")
    print(f"CLI Commands: {result['cli_commands']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Validation Passed: {result['validation_passed']}")
    print(f"\nResponse:\n{result['final_response']}")


async def example_explain_concept():
    """Example: Explain vEPC concept."""
    print("\n" + "="*60)
    print("Example 3: Explain Concept")
    print("="*60)

    result = await run_vepc_workflow(
        user_query="What does the T3412 timer do?",
        language="en"
    )

    print(f"\nIntent: {result['intent']}")
    print(f"\nResponse:\n{result['final_response']}")


async def example_vietnamese():
    """Example: Vietnamese query."""
    print("\n" + "="*60)
    print("Example 4: Vietnamese Query")
    print("="*60)

    result = await run_vepc_workflow(
        user_query="Hiển thị MCC và MNC hiện tại",
        language="vi"
    )

    print(f"\nIntent: {result['intent']}")
    print(f"CLI Commands: {result['cli_commands']}")
    print(f"\nResponse:\n{result['final_response']}")


async def example_conversation_context():
    """Example: Follow-up query with conversation context."""
    print("\n" + "="*60)
    print("Example 5: Conversation Context")
    print("="*60)

    # First query
    result1 = await run_vepc_workflow(
        user_query="Set timer T3412 to 60 minutes",
        language="en"
    )
    print(f"\nFirst query: Set timer T3412 to 60 minutes")
    print(f"Response: {result1['final_response'][:100]}...")

    # Follow-up query with context
    history = [
        {
            "user": "Set timer T3412 to 60 minutes",
            "assistant": result1['final_response']
        }
    ]

    result2 = await run_vepc_workflow(
        user_query="now change it to 90",
        language="en",
        conversation_history=history
    )

    print(f"\nFollow-up query: now change it to 90")
    print(f"CLI Commands: {result2['cli_commands']}")
    print(f"\nResponse:\n{result2['final_response']}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("vEPC Workflow - Quick Start Examples")
    print("="*60)

    await example_show_configuration()
    await example_update_configuration()
    await example_explain_concept()
    await example_vietnamese()
    await example_conversation_context()

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
