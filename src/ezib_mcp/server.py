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
from contextlib import asynccontextmanager
from typing import AsyncIterator
from dataclasses import dataclass
from ezib_async import ezIBAsync
from typing import Any

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
        await asyncio.sleep(5)

        for i in range(len(ezib.accountCodes)):
            if i != len(ezib.accountCodes) - 1:
                ezib.disconnect()
                await ezib.connectAsync(account=ezib.accountCodes[i+1])
            
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
async def get_accounts(ctx: Context) -> dict:
    """
    Get account values for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of account values for all accounts
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
async def get_portfolios(ctx: Context) -> dict:
    """
    Get portfolios for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of portfolio items for all accounts
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
async def get_positions(ctx: Context) -> dict:
    """
    Get positions for all accounts.
    
    Args:
        ctx: The context containing the ezib connection
        
    Returns:
        dict: A dict of position items for all accounts
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
async def get_account(ctx: Context, account: str = "") -> dict:
    """
    Get account values for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get values for. Defaults to "".
        
    Returns:
        dict: A dict of account values for the active account
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        if account == "":
            return ezib.account
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.accounts[account]
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account portfolio
# ---------------------------------------
@mcp.tool()
async def get_portfolio(ctx: Context, account: str = "") -> dict:
    """
    Get portfolio for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get portfolio for. Defaults to "".
        
    Returns:
        dict: A dict of portfolio items for the active account
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        if account == "":
            return ezib.portfolio
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.portfolios[account]
    else:
        raise Exception("Not connected to Interactive Brokers")

# ---------------------------------------
# active account positions
# ---------------------------------------
@mcp.tool()
async def get_position(ctx: Context, account: str = "") -> dict:
    """
    Get positions for the active account.
    
    Args:
        ctx (Context): The context containing the ezib connection
        account (str, optional): The account to get positions for. Defaults to "".
        
    Returns:
        dict: A dict of position items for the active account
    """
    ezib = ctx.request_context.lifespan_context.ezib
    if ezib.connected:
        if account == "":
            return ezib.position
        elif account not in ezib.accountCodes:
            raise ValueError(f"Account {account} not found")

        return ezib.positions[account]
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