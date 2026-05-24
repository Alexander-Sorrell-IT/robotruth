import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    # Use sys.executable so the server subprocess inherits the same venv/env
    # that has robotruth and mcp installed, regardless of what "python" resolves to.
    params = StdioServerParameters(command=sys.executable, args=["-m", "robotruth_mcp.server"])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            names = [t.name for t in tools.tools]
            print("MCP tools exposed:", names)
            assert "audit_pr" in names, "audit_pr tool not exposed!"
            print("SMOKE OK")


if __name__ == "__main__":
    asyncio.run(main())
