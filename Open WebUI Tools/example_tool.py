"""
title: OpenWebUI SSH Connection Manager (Enhanced)
author: Dr. Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.1.0
license: MIT
description: |
  A complete OpenWebUI tool for managing SSH connections with:
  - Connection testing
  - IP information retrieval
  - Basic SSH command execution
requirements: paramiko, python-dotenv
"""
import json
import logging
import traceback
import socket
import requests
import paramiko
from typing import Optional, Callable, Any, Dict, List
from pydantic import BaseModel, Field
from fastapi import Request
import asyncio
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class SSHConnection(BaseModel):
    host: str
    port: int = Field(default=22)
    username: str
    password: Optional[str] = None
    private_key: Optional[str] = None
    timeout: int = Field(default=10)

class Tools:
    """
    Enhanced SSH Connection Manager for OpenWebUI with:
    - Connection management
    - IP information retrieval
    - Basic command execution
    """
    def __init__(self):
        self.active_connections: Dict[str, paramiko.SSHClient] = {}

    async def get_ip_info(self) -> Dict:
        """Retrieve server IP information"""
        try:
            private_ip = socket.gethostbyname(socket.gethostname())
            public_ip = (
                requests.get("https://api.ipify.org?format=json", timeout=5)
                .json()
                .get("ip", "Unknown")
            )
            return {
                "status": "success",
                "private_ip": private_ip,
                "public_ip": public_ip,
            }
        except Exception as e:
            logger.error(f"IP retrieval failed: {e}")
            return {"status": "error", "message": str(e)}

    async def test_ssh_connection(self, connection: SSHConnection) -> Dict:
        """Test SSH connection to a host"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if connection.private_key:
                key = paramiko.RSAKey.from_private_key_file(connection.private_key)
                client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    pkey=key,
                    timeout=connection.timeout,
                )
            else:
                client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    password=connection.password,
                    timeout=connection.timeout,
                )
            client.close()
            return {"status": "success", "message": "SSH connection successful"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def execute_ssh_command(
        self, connection: SSHConnection, command: str
    ) -> Dict:
        """Execute a command over SSH"""
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if connection.private_key:
                key = paramiko.RSAKey.from_private_key_file(connection.private_key)
                client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    pkey=key,
                    timeout=connection.timeout,
                )
            else:
                client.connect(
                    hostname=connection.host,
                    port=connection.port,
                    username=connection.username,
                    password=connection.password,
                    timeout=connection.timeout,
                )
            stdin, stdout, stderr = client.exec_command(command)
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            client.close()
            return {"status": "success", "output": output, "error": error}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def pipe(self, body: Dict) -> Dict:
        """Process messages with SSH capabilities"""
        try:
            messages = body.get("messages", [])
            if not messages:
                return {"error": "No messages provided"}
            last_message = messages[-1]
            content = last_message.get("content", "")
            # Check for IP request
            if "ip" in content.lower():
                ip_info = await self.get_ip_info()
                body["messages"].append(
                    {"role": "assistant", "content": json.dumps({"ip_info": ip_info})}
                )
            # Check for SSH command
            elif "ssh" in content.lower():
                # Parse connection details from message
                # In a real implementation, you'd want proper parsing
                connection = SSHConnection(
                    host=os.getenv("SSH_HOST", "localhost"),
                    username=os.getenv("SSH_USER", "user"),
                    password=os.getenv("SSH_PASS"),
                )
                if "test" in content.lower():
                    result = await self.test_ssh_connection(connection)
                else:
                    command = content.split("ssh")[1].strip()
                    result = await self.execute_ssh_command(connection, command)
                body["messages"].append(
                    {"role": "assistant", "content": json.dumps({"ssh_result": result})}
                )
            return body
        except Exception as e:
            logger.error(f"Pipe error: {e}")
            return {"error": str(e)}

# Example Usage
if __name__ == "__main__":
    async def test_tool():
        tool = Tools()
        # Test IP retrieval
        print("Testing IP retrieval:")
        ip_info = await tool.get_ip_info()
        print(json.dumps(ip_info, indent=2))
        # Test SSH connection
        print("\nTesting SSH connection:")
        connection = SSHConnection(
            host="localhost", username="testuser", password="testpass"
        )
        ssh_test = await tool.test_ssh_connection(connection)
        print(json.dumps(ssh_test, indent=2))
        # Test pipe functionality
        print("\nTesting pipe with IP request:")
        pipe_result = await tool.pipe(
            {"messages": [{"role": "user", "content": "What's my server IP?"}]}
        )
        print(json.dumps(pipe_result, indent=2))

    asyncio.run(test_tool())
