"""
MIT License

Copyright (c) 2025 Kelvin Gao

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import os
import asyncio

from mcp.server.fastmcp import FastMCP, Context
from ezib_async import ezIBAsync, AccountValue, PortfolioItem, Position
from typing import Dict, List, Any
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass
class EzIBContext:
    """Context for the ezibAsync MCP server."""
    ezib: Any
    
@asynccontextmanager
async def ezib_lifespan(server: FastMCP) -> AsyncIterator[EzIBContext]:
    """
    Manages the ezIBAsync client lifecycle.
    
    Args:
        server: The FastMCP server instance
        
    Yields:
        EzIBContext: The context containing the ezib connection
    """
    # create ezIBAsync instance
    ezib = ezIBAsync(
        ibhost=os.getenv("IB_HOST", "127.0.0.1"),
        ibport=os.getenv("IB_PORT", "4001"),
        ibclient=os.getenv("IB_CLIENTID", "0")
    )
    
    try:
        await ezib.connectAsync()
        yield EzIBContext(ezib=ezib)
    finally:
        # close the connection when done
        ezib.disconnect()

mcp = FastMCP(
    "ezib-mcp",
    lifespan=ezib_lifespan,
    description="MCP server built on `ezib_async` that exposes Interactive Brokers' trading and market data functionality.",
    host=os.getenv("HOST", "0.0.0.0"),
    port=os.getenv("PORT", "8050")
)

# =============================================
# Multi-account infomation
# ---------------------------------------
# multi-account account values
# ---------------------------------------
@mcp.tool()
async def get_accounts(ctx: Context) -> Dict[str, List[AccountValue]]:
    """
    Returns all the accounts values of all the multi-account.
    
    :param ctx: The context containing the ezib connection
    :return: A dictionary mapping account names to a list of account values
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ezib.accounts
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# multi-account portfolios
# ---------------------------------------
@mcp.tool()
async def get_portfolios(ctx: Context) -> Dict[str, List[PortfolioItem]]:
    """
    Returns all the account portfolios of all the multi-account.
    
    :param ctx: The context containing the ezib connection
    :return: A dictionary mapping account names to a list of portfolio items
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ezib.portfolios
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# multi-account positions
# ---------------------------------------
@mcp.tool()
async def get_positions(ctx: Context) -> Dict[str, List[Position]]:
    """
    Returns all the account positions of all the multi-account.
    
    :param ctx: The context containing the ezib connection
    :return: A dictionary mapping account names to a list of position items
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ezib.positions
    else:
        raise Exception("Not connected to Interactive Brokers")


# =============================================
# Active account infomation
# ---------------------------------------
# active account account values
# ---------------------------------------
@mcp.tool()
async def get_account(ctx: Context) -> List[AccountValue]:
    """
    Returns the account values of the active account.
    
    :param ctx: The context containing the ezib connection
    :return: A list of account values
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ezib.account
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account portfolio
# ---------------------------------------
@mcp.tool()
async def get_portfolio(ctx: Context) -> List[PortfolioItem]:
    """
    Returns the portfolio items of the active account.
    
    :param ctx: The context containing the ezib connection
    :return: A list of portfolio items
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ctx.ezib.portfolio
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account positions
# ---------------------------------------
@mcp.tool()
async def get_position(ctx: Context) -> List[Position]:
    """
    Returns the position items of the active account.
    
    :param ctx: The context containing the ezib connection
    :return: A list of position items
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        return ezib.position
    else:
        raise Exception("Not connected to Interactive Brokers")


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