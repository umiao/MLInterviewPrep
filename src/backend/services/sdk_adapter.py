"""Claude Agent SDK adapter for async LLM interactions."""
import logging

logger = logging.getLogger(__name__)

# Check if Claude Agent SDK is available
try:
    from claude_agent_sdk import create_agent

    SDK_AVAILABLE = True
except ImportError:
    SDK_AVAILABLE = False


async def run_query(
    prompt: str,
    system_prompt: str,
    model: str = "claude-sonnet-4-20250514",
) -> str:
    """Run a query using the Claude Agent SDK.

    Args:
        prompt: User message content.
        system_prompt: System instruction.
        model: Model name (currently ignored, SDK uses default).

    Returns:
        Response text from the agent.

    Raises:
        RuntimeError: If SDK is not available.
    """
    if not SDK_AVAILABLE:
        raise RuntimeError(
            "claude_agent_sdk is not installed. "
            "Install it or set LLM_BACKEND='anthropic' in config."
        )

    agent = create_agent(system_prompt=system_prompt)
    response = await agent.run(prompt)
    return response
