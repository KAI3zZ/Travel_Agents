"""高德地图MCP服务封装"""

from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo

# 全局MCP工具实例
_amap_mcp_tool = None

def get_amap_mcp_tool() -> MCPTool:
    """
    获取高德地图MCP工具实例
    Returns:
        MCPTool实例
    """
    global _amap_mcp_tool

    if not _amap_mcp_tool:
        settings = get_settings()

        if not settings.amap_api_key:
            raise ValueError("高德地图API Key未配置,请在.env文件中设置AMAP_API_KEY")
        
        # 创建MCP工具
        _amap_mcp_tool = MCPTool(
            name="amap",
            description="高德地图服务，支持POI搜索、路线规划、天气查询等功能",
            server_command=["uvx","amap-mcp-server"],
            env={"AMAP_MAPS_API_KEY":settings.amap_api_key},
            auto_expand=True    # 自动展开为独立工具
        )

        print(f"✅ 高德地图MCP工具初始化成功")
        print(f"   工具数量: {len(_amap_mcp_tool._available_tools)}")
        
        # 打印可用工具列表
        if _amap_mcp_tool._available_tools:
            print("   可用工具:")
            for tool in _amap_mcp_tool._available_tools[:5]:  # 只打印前5个
                print(f"     - {tool.get('name', 'unknown')}")
            if len(_amap_mcp_tool._available_tools) > 5:
                print(f"     ... 还有 {len(_amap_mcp_tool._available_tools) - 5} 个工具")

    return _amap_mcp_tool



