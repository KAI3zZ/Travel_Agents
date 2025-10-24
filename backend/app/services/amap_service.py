"""高德地图MCP服务封装"""

from typing import List, Dict, Any, Optional
from hello_agents.tools import MCPTool
from ..config import get_settings
from ..models.schemas import Location, POIInfo, WeatherInfo
from ..agents.tools import get_tools


class AmapService:
    """高德地图服务封装类"""

    def __init__(self):
        """初始化服务"""
        self.mcp_tools = None
    
    async def _create(self):
        self.mcp_tools = await get_tools()

    async def search_poi(self, keywords: str, city: str, citylimit: bool) -> List[POIInfo]:
        """
        搜索POI
        Args：
            keywords: 搜索关键词
            city： 城市
            citylimit：是否限制在城市范围内
        Returns:
            POI信息列表
        """
        try:
            # 得到所有的工具列表List[BaseTool]
            await self._create()

            # 得到当前需要的工具
            maps_text_search_tool = next(
                (t for t in self.mcp_tools if "maps_text_search" in t.name),
                None
            )
            if not maps_text_search_tool:
                print("mcp工具集中无法找到maps_text_search工具")
            else:
                print(f"找到m{maps_text_search_tool.name}工具,准备进行调用...")

            # 调用该工具
            result = maps_text_search_tool.invoke({
                "keywords":keywords,
                "city": city,
                "citylimit": str(citylimit).lower()
            })

            # MCP工具返回的是字符串，需要解析为JSON
            # 先简化，不解析，打印结果进行查看
            print(f"POI搜索结果:{result[:200]}")

            # TODO: 实际解析的代码
            return []

        except Exception as e:
            print(f"❌ POI搜索失败: {str(e)}")
            return []
        
    async def get_weather(self, city: str) -> List[WeatherInfo]:
        """
        查询天气
        Args:
            city: 要查天气的城市名称
        Returns:
            天气信息列表
        """
        try:
            # 得到所有的工具列表List[BaseTool]
            await self._create()

            maps_weather_tool = next(
                (t for t in self.mcp_tools if "maps_weather" in t.name),
                None
            )
            if not maps_weather_tool:
                print("mcp工具集中无法找到maps_weather工具")
            else:
                print(f"找到{maps_weather_tool.name}工具,准备进行调用...")
            # 调用该工具
            result = maps_weather_tool.invoke({
                "city": city
            })

            # MCP工具返回的是字符串，需要解析为JSON
            # 先简化，不解析，打印结果进行查看
            print(f"天气查询结果:{result[:200]}")

            return []
            
        except Exception as e:
            print(f"❌ 天气查询失败: {str(e)}")
            return []


    async def plan_route(
        self,
        origin_address: str,
        destination_address: str,
        origin_city: Optional[str] = None,
        destination_city: Optional[str] = None,
        route_type: str = "walking"
    ) -> Dict[str, Any]:
        """
        规划路线
        Args:
            origin_address: 起点地址
            destination_address: 终点地址
            origin_city: 起点城市
            destination_city: 终点城市
            route_type: 路线类型 (walking/driving/transit)
        Returns:
            路线信息
        """
        try:
            await self._create()

            # 工具映射表
            tool_map = {
                "walking": "maps_direction_walking_by_address",
                "driving": "maps_direction_driving_by_address",
                "transit": "maps_direction_transit_integrated_by_address"
            }
            # 获取对应工具
            plan_route_tool_name = tool_map.get(route_type)
            plan_route_tool = next(
                (t for t in self.mcp_tools if plan_route_tool_name in t.name),
                None
            )
            if not plan_route_tool:
                print(f"mcp工具集中无法找到{plan_route_tool_name}工具")
            else:
                print(f"找到{plan_route_tool.name}工具,准备进行调用...")

            # 调用该工具
            result = plan_route_tool.invoke({
                "origin_address": origin_address,
                "destination_address": destination_address,
                "origin_city": origin_city or "",
                "destination_city": destination_city or ""
            })

            # MCP工具返回的是字符串，需要解析为JSON
            # 先简化，不解析，打印结果进行查看
            print(f"路线规划结果:{result[:200]}...")

            return {}

        except Exception as e:
            print(f"❌ 路线规划失败: {str(e)}")
            return []


    async def geocode(self, address: str, city: Optional[str] = None) -> Optional[Location]:
        """
        地理编码(地址转坐标)

        Args:
            address: 地址
            city: 城市

        Returns:
            经纬度坐标
        """
        try:
            # 得到所有的工具列表List[BaseTool]
            await self._create()

            # 获取地理编码工具
            geocode_tool = next(
                (t for t in self.mcp_tools if "maps_geo" in t.name),
                None
            )
            if not geocode_tool:
                print("mcp工具集中无法找到maps_geocode工具")
            else:
                print(f"找到{geocode_tool.name}工具,准备进行调用...")

            # 调用该工具
            result = geocode_tool.invoke({
                "address": address,
                "city": city or ""
            })

            # MCP工具返回的是字符串，需要解析为JSON
            # 先简化，不解析，打印结果进行查看
            print(f"地理编码结果:{result[:200]}...")

            return None
        
        except Exception as e:
            print(f"❌ 地理编码失败: {str(e)}")
            return None


    async def get_poi_detail(self, poi_id: str) -> Dict[str, Any]:
        """
        获取POI详情

        Args:
            poi_id: POI ID

        Returns:
            POI详情信息
        """
        try:
            # 得到所有的工具列表List[BaseTool]
            await self._create()

            # 获取POI详情工具
            poi_detail_tool = next(
                (t for t in self.mcp_tools if "maps_search_detail" in t),
                None
            )
            if not poi_detail_tool:
                print("mcp工具集中无法找到maps_search_detail工具")
            else:
                print(f"找到{poi_detail_tool.name}工具,准备进行调用...")
            
            # 调用该工具
            result = poi_detail_tool.invoke({
                "poi_id": poi_id
            })

            # MCP工具返回的是字符串，需要解析为JSON
            # 先简化，不解析，打印结果进行查看
            print(f"POI详情结果:{result[:200]}...")

            return {}
        
        except Exception as e:
            print(f"❌ 获取POI详情失败: {str(e)}")
            return {}

# 创建全局服务实例
_amap_service = None

def get_amap_service() -> AmapService:
    """获取高德地图服务实例(单例模式)"""
    global _amap_service
    
    if _amap_service is None:
        _amap_service = AmapService()
    
    return _amap_service