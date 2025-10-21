import asyncio
import logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('test.log', encoding='utf-8'),  # 写入文件
        # logging.StreamHandler()  # 同时输出到控制台（可选）
    ]
)
logger = logging.getLogger(__name__)
from typing import Dict,List,Any
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import get_settings

_tools = None
settings = get_settings()

async def get_tools() -> List[BaseTool]:
    global _tools
    client = MultiServerMCPClient({
        # 高德地图MCP Server
        "amap-maps-streamableHTTP": {
            "url": f"https://mcp.amap.com/mcp?key={settings.amap_api_key}",
            "transport": "streamable_http"
        }
    })

    _tools = await client.get_tools()
    # print(f"tools:\n\n" + "\n\n".join(str(tool) for tool in tools) + "\n")
    logger.info(f"tools:\n\n" + "\n\n".join(str(tool) for tool in _tools) + "\n")
    return _tools