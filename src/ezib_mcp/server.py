import os
import asyncio

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mpc = FastMCP(
    "ezib-mcp",
    description="An MCP server built on `ezib_async` that exposes Interactive Brokers' trading and market data functionality.",
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)

async def main():
    transport = os.getenv("TRANSPORT", "sse")
    if transport == 'sse':
        # Run the MCP server with sse transport
        await mcp.run_sse_async()
    else:
        # Run the MCP server with stdio transport
        await mcp.run_stdio_async()
    
    
if __name__ == "__main__":
    asyncio.run(main())