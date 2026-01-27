#!/usr/bin/env python3
"""Helper script to configure MCP server in Cursor/Codex.

This script helps set up the spine-analysis-mcp server configuration.
"""

import json
import os
import sys
from pathlib import Path


def find_cursor_config():
    """Find Cursor MCP configuration file."""
    home = Path.home()
    
    # Check common locations
    locations = [
        home / ".cursor" / "mcp.json",
        home / ".config" / "cursor" / "mcp.json",
        Path.cwd() / ".cursor" / "mcp.json",
    ]
    
    for loc in locations:
        if loc.exists():
            return loc
    
    # Return default location
    return home / ".cursor" / "mcp.json"


def find_codex_config():
    """Find Codex configuration file."""
    home = Path.home()
    
    locations = [
        home / ".codex" / "config.toml",
        home / ".config" / "codex" / "config.toml",
    ]
    
    for loc in locations:
        if loc.exists():
            return loc
    
    return home / ".codex" / "config.toml"


def configure_cursor():
    """Configure Cursor MCP server."""
    config_path = find_cursor_config()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get service account path
    service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account:
        service_account = input("Enter path to Google service account JSON: ").strip()
    
    # Get Python path
    python_path = sys.executable
    
    # Create or update config
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
    else:
        config = {}
    
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    config["mcpServers"]["spine-analysis"] = {
        "command": python_path,
        "args": ["-m", "spine_analysis_mcp.server"],
        "env": {
            "GOOGLE_APPLICATION_CREDENTIALS": service_account,
            "BQ_PROJECT_ID": "flash-clover-464719-g1",
            "BQ_DATASET_ID": "spine"
        }
    }
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Cursor configuration updated: {config_path}")
    return config_path


def configure_codex():
    """Configure Codex MCP server."""
    config_path = find_codex_config()
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get service account path
    service_account = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not service_account:
        service_account = input("Enter path to Google service account JSON: ").strip()
    
    # Get Python path
    python_path = sys.executable
    
    # Read existing config or create new
    if config_path.exists():
        with open(config_path) as f:
            content = f.read()
    else:
        content = ""
    
    # Check if already configured
    if "spine-analysis" in content:
        print(f"⚠️  Codex configuration already contains spine-analysis")
        print(f"   Edit manually: {config_path}")
        return config_path
    
    # Add configuration
    config_section = f"""
[mcp_servers.spine-analysis]
command = "{python_path}"
args = ["-m", "spine_analysis_mcp.server"]
env = {{
  GOOGLE_APPLICATION_CREDENTIALS = "{service_account}"
  BQ_PROJECT_ID = "flash-clover-464719-g1"
  BQ_DATASET_ID = "spine"
}}
"""
    
    with open(config_path, "a") as f:
        f.write(config_section)
    
    print(f"✅ Codex configuration updated: {config_path}")
    return config_path


def main():
    """Main configuration function."""
    print("Spine Analysis MCP Server - Configuration Helper")
    print("=" * 60)
    
    print("\nWhich MCP client would you like to configure?")
    print("1. Cursor")
    print("2. Codex")
    print("3. Both")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        configure_cursor()
    elif choice == "2":
        configure_codex()
    elif choice == "3":
        configure_cursor()
        configure_codex()
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Configuration complete!")
    print("\nNext steps:")
    print("1. Restart your MCP client (Cursor/Codex)")
    print("2. Verify the server is available in your client")
    print("3. Test with: python test_server.py")


if __name__ == "__main__":
    main()
