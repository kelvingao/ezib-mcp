<h1 align="center">EZIB-MCP: Interactive Brokers Trading for AI Agents</h1>

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io) server implementation that enables AI agents to interact with Interactive Brokers' trading platform, providing access to market data, account information, and trading functionality.

## Overview

This project provides an MCP server built on `ezib_async` that allows AI agents to connect to Interactive Brokers, retrieve account information, manage portfolios, and execute trades. It serves as both a practical tool for algorithmic trading and a reference implementation for building MCP servers.

The implementation follows the best practices laid out for building MCP servers, allowing seamless integration with any MCP-compatible client.

## Features

The server provides several powerful tools for trading and market data:

1. **Account Information**: Access account balances, positions, and portfolio data
2. **Market Data**: Retrieve real-time and historical market data
3. **Order Management**: Place, modify, and cancel orders
4. **Position Management**: Monitor and manage trading positions

## Prerequisites

- Python 3.11+
- Interactive Brokers TWS or IB Gateway running
- Docker if running the MCP server as a container (recommended)

## Installation

### Using pip

1. Clone this repository:
   ```bash
   git clone https://github.com/kelvingao/ezib-mcp.git
   cd ezib-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -e .
   ```

3. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

4. Configure your environment variables in the `.env` file (see Configuration section)

### Using Docker (Recommended)

1. Build the Docker image:
   ```bash
   docker build -t mcp/ezib --build-arg PORT=8050 .
   ```

2. Create a `.env` file based on `.env.example` and configure your environment variables

## Configuration

The following environment variables can be configured in your `.env` file:

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `IB_HOST` | Interactive Brokers host | `127.0.0.1` | `127.0.0.1` |
| `IB_PORT` | Interactive Brokers port | `4001` | `4001` |
| `IB_CLIENTID` | Client ID for IB connection | `0` | `1` |
| `TRANSPORT` | Transport protocol (sse or stdio) | - | `sse` |
| `HOST` | Host to bind to when using SSE transport | - | `0.0.0.0` |
| `PORT` | Port to listen on when using SSE transport | - | `8050` |

## Running the Server

### Using pip

#### SSE Transport

```bash
# Set TRANSPORT=sse in .env then:
python src/server.py
```

The MCP server will run as an API endpoint that you can connect to with the configuration shown below.

#### Stdio Transport

With stdio, the MCP client itself can spin up the MCP server, so nothing to run at this point.

### Using Docker

#### SSE Transport

```bash
docker run --env-file .env -p 8050:8050 mcp/ezib
```

The MCP server will run as an API endpoint within the container that you can connect to with the configuration shown below.

#### Stdio Transport

With stdio, the MCP client itself can spin up the MCP server container, so nothing to run at this point.

## Integration with MCP Clients

### SSE Configuration

Once you have the server running with SSE transport, you can connect to it using this configuration:

```json
{
  "mcpServers": {
    "ezib": {
      "transport": "sse",
      "url": "http://localhost:8050/sse"
    }
  }
}
```

> **Note for Windsurf users**: Use `serverUrl` instead of `url` in your configuration:
> ```json
> {
>   "mcpServers": {
>     "ezib": {
>       "transport": "sse",
>       "serverUrl": "http://localhost:8050/sse"
>     }
>   }
> }
> ```

> **Note for n8n users**: Use host.docker.internal instead of localhost since n8n has to reach outside of its own container to the host machine:
> 
> So the full URL in the MCP node would be: http://host.docker.internal:8050/sse

Make sure to update the port if you are using a value other than the default 8050.

### Python with Stdio Configuration

Add this server to your MCP configuration for Claude Desktop, Windsurf, or any other MCP client:

```json
{
  "mcpServers": {
    "ezib": {
      "command": "your/path/to/ezib-mcp/.venv/bin/python",
      "args": ["your/path/to/ezib-mcp/src/main.py"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

### Docker with Stdio Configuration

```json
{
  "mcpServers": {
    "ezib": {
      "command": "docker",
      "args": ["run", "--rm", "-i", 
               "-e", "TRANSPORT", 
               "mcp/ezib"],
      "env": {
        "TRANSPORT": "stdio"
      }
    }
  }
}
```

## Usage Examples

Here are some examples of how to use the EZIB MCP server with an AI agent:

### Getting Account Information

```
Retrieve my current account balance and positions.
```

### Placing an Order

```
Place a market order to buy 100 shares of AAPL.
```

### Retrieving Market Data

```
Get the current price and trading volume for TSLA.
```

### Managing Positions

```
Show me all my open positions and their current P&L.
```


## License

[MIT License](LICENSE)