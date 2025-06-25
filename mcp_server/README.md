# Leasing Assistant MCP Server

A Model Context Protocol (MCP) server that provides apartment leasing tools for checking availability, pet policies, and pricing information.

## Features

The server provides three domain tools:

- **check_availability**: Check apartment unit availability by community and bedroom count
- **check_pet_policy**: Check pet policies for specific communities and pet types
- **get_pricing**: Get detailed pricing information for units and move-in dates

## Project Structure

```
mcp_server/
├── server.py              # Main MCP server entry point
├── data/
│   ├── __init__.py
│   ├── inventory.py        # InventoryService and data providers
│   ├── communities.json    # Community information
│   ├── units.json         # Unit inventory data
│   ├── pet_policies.json  # Pet policy data
│   └── specials.json      # Special offers data
├── tools/
│   ├── __init__.py
│   └── tools.py           # Domain tool implementations
├── tests/
│   ├── __init__.py
│   ├── test_inventory_service.py  # Tests for InventoryService methods
│   └── test_tools.py      # Tests for domain tools
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

### Direct execution:
```bash
python server.py
```

### As a module:
```bash
python -m server
```

The server runs using stdio transport and communicates via JSON-RPC following the MCP protocol.

## Using with Claude Desktop

To use this MCP server with Claude Desktop, you need to configure it in your Claude Desktop settings:

### 1. Configuration File Location

Find your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### 2. Add Server Configuration

Add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "leasing-assistant": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/absolute/path/to/your/mcp_server"
    }
  }
}
```

**Important**: Replace `/absolute/path/to/your/mcp_server` with the actual absolute path to your mcp_server directory.

### 3. Example Full Configuration

If you have other MCP servers, your full config might look like:

```json
{
  "mcpServers": {
    "leasing-assistant": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/Users/yourusername/dev/assistant/mcp_server"
    },
    "other-server": {
      "command": "node",
      "args": ["index.js"],
      "cwd": "/path/to/other/server"
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration file, restart Claude Desktop completely for the changes to take effect.

### 5. Verify Connection

Once Claude Desktop restarts, you should be able to use the leasing assistant tools in your conversations:

- Ask Claude to check apartment availability
- Inquire about pet policies for specific communities  
- Request pricing information for units

Claude will automatically use the MCP server tools to provide real apartment data in responses.

## Data Structure

The server uses JSON files for data storage:

- **communities.json**: Community information (name, location, amenities)
- **units.json**: Unit inventory (bedrooms, rent, availability, etc.)
- **pet_policies.json**: Pet policies per community and pet type
- **specials.json**: Current special offers and discounts

## Running Tests

Run the test suite using pytest:

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_inventory_service.py
pytest tests/test_tools.py
```

## API Usage

The server provides the following tools via MCP:

### check_availability
```json
{
  "name": "check_availability",
  "arguments": {
    "community_id": "sunset-ridge",
    "bedrooms": 2
  }
}
```

### check_pet_policy
```json
{
  "name": "check_pet_policy",
  "arguments": {
    "community_id": "sunset-ridge",
    "pet_type": "cat"
  }
}
```

### get_pricing
```json
{
  "name": "get_pricing",
  "arguments": {
    "community_id": "sunset-ridge",
    "unit_id": "12B",
    "move_in_date": "2025-07-15"
  }
}
```

## Architecture

- **InventoryService**: Main service class with pluggable data providers
- **JsonFileLoader**: Loads data from JSON files (default)
- **DatabaseReader**: Stub for future database integration
- **Domain Tools**: Business logic for apartment leasing operations

The system uses a data provider pattern allowing easy switching between JSON files and database backends.

bug report:
https://github.com/modelcontextprotocol/python-sdk/issues/987
