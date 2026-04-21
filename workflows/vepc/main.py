"""Main entry point for vEPC workflow."""
import asyncio
from workflows.vepc.vepc_workflow import run_vepc_workflow


async def main():
    """Run example vEPC queries."""

    print("=" * 60)
    print("vEPC Workflow - Example Queries")
    print("=" * 60)

    # Example 1: Show configuration (English)
    print("\n[Example 1] Show configuration")
    print("-" * 60)
    result1 = await run_vepc_workflow(
        user_query="Show me the current MCC, MNC and MME code",
        language="en"
    )
    print(f"Response:\n{result1['final_response']}")
    print(f"Intent: {result1['intent']}")
    print(f"CLI Commands: {result1['cli_commands']}")

    # Example 2: Update configuration (English)
    print("\n[Example 2] Update configuration")
    print("-" * 60)
    result2 = await run_vepc_workflow(
        user_query="Set timer T3412 to 60 minutes",
        language="en"
    )
    print(f"Response:\n{result2['final_response']}")
    print(f"Intent: {result2['intent']}")
    print(f"Risk Level: {result2['risk_level']}")

    # Example 3: Explain concept (Vietnamese)
    print("\n[Example 3] Explain concept (Vietnamese)")
    print("-" * 60)
    result3 = await run_vepc_workflow(
        user_query="CSFB là gì?",
        language="vi"
    )
    print(f"Response:\n{result3['final_response']}")
    print(f"Intent: {result3['intent']}")

    # Example 4: Greeting (Vietnamese)
    print("\n[Example 4] Greeting (Vietnamese)")
    print("-" * 60)
    result4 = await run_vepc_workflow(
        user_query="Xin chào, bạn có thể giúp gì?",
        language="vi"
    )
    print(f"Response:\n{result4['final_response']}")
    print(f"Intent: {result4['intent']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
