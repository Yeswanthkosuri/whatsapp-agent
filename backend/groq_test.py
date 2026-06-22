"""Local Groq smoke test for text responses."""

import asyncio

from app.services.openai_service import generate_structured_response


async def main() -> None:
    result = await generate_structured_response(
        system_prompt="You are a helpful assistant.",
        user_message="Tell me a joke",
        history=[],
        media_library={},
    )
    print(result["content"])


if __name__ == "__main__":
    asyncio.run(main())
