import asyncio
import json
from .prompt import ATTRACTION_AGENT_PROMPT,WEATHER_AGENT_PROMPT,HOTEL_AGENT_PROMPT,PLANNER_AGENT_PROMPT
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from typing import Dict,List,Any
from .tools import get_tools
from ..services.llm_service import get_llm
from ..config import get_settings,Settings
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from langgraph.graph import StateGraph,MessagesState,START,END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from ..models.schemas import TripRequest, TripPlan, DayPlan, Attraction, Meal, WeatherInfo, Location, Hotel
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.store.postgres.aio import AsyncPostgresStore
import uuid
import logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.FileHandler('memory.log', encoding='utf-8'),  # 写入文件
        logging.StreamHandler()  # 同时输出到控制台（可选）
    ]
)
logger = logging.getLogger(__name__)


class MultiAgents:

    def __init__(self):
        """定义多智能体的属性"""
        self.llm = None
        self.settings = None
        self.tools = []
        self.attraction_agent = None
        self.weather_agent = None
        self.hotel_agent = None
        self.supervisor_agent = None
        self.memory = MemorySaver()

    async def create(self):
        """初始化多智能体"""
        print("🔄 开始初始化多智能体旅行规划系统...")
        try:
            self.llm = get_llm()
            self.settings = get_settings()
            self.tools = await get_tools()

            attraction_tools = [t for t in self.tools if "maps_text_search" in t.name]
            attraction_prompt = ATTRACTION_AGENT_PROMPT
            self.attraction_agent = create_react_agent(
                name="attraction_agent",
                model=self.llm,
                prompt=attraction_prompt,
                tools=attraction_tools
            )

            # with open("attraction_agent.png", "wb") as f:
            #     f.write(self.attraction_agent.get_graph().draw_mermaid_png())

            weather_tools = [t for t in self.tools if "maps_weather" in t.name]
            weather_prompt = WEATHER_AGENT_PROMPT
            self.weather_agent = create_react_agent(
                name="weather_agent",
                model=self.llm,
                prompt=weather_prompt,
                tools=weather_tools
            )

            # with open("weather_agent.png", "wb") as f:
            #     f.write(self.weather_agent.get_graph().draw_mermaid_png())

            hotel_tools = [t for t in self.tools if "maps_text_search" in t.name]
            hotel_prompt = HOTEL_AGENT_PROMPT
            self.hotel_agent = create_react_agent(
                name="hotel_agent",
                model=self.llm,
                prompt=hotel_prompt,
                tools=hotel_tools
            )

            # with open("hotel_agent.png", "wb") as f:
            #     f.write(self.hotel_agent.get_graph().draw_mermaid_png())

            # 监督者（不需要工具，只负责调度agent、整合并产生标准化输出）
            supervisor_prompt = PLANNER_AGENT_PROMPT
            self.supervisor_agent = create_supervisor(
                [self.attraction_agent,self.weather_agent,self.hotel_agent],
                model=self.llm,
                output_mode="last_message",
                prompt=supervisor_prompt
            )


            # with open("graph.png", "wb") as f:
            #     f.write(self.supervisor_agent.get_graph().draw_mermaid_png())
            
            # 无记忆功能
            # app = supervisor_agent.compile()
            # input = {
            # "messages": [
            #         {"role":"user","content":"如果你收到了我的问题，你只需要回答我：我收到了您的问题了，我是Agent"}
            #     ]
            # }
            # result = app.invoke(input=input)
            # print(result["messages"][-1].content) # 由于是AIMessage对象，所以只能用.content

            # 有记忆功能
            # memeory = MemorySaver()
            # config = {"configurable": {"thread_id": "1"}}
            # inputs = {
            # "messages": [
            #         {"role":"user","content":"我想在2025.10.22-10.24号期间在北京旅游，请你帮我看一下天气并制定一下旅行计划"}
            #     ]
            # }
            # app = self.supervisor_agent.compile(checkpointer=memeory)
            # async for event in app.astream(inputs, config=config, stream_mode="values"):
            #     last_msg = event["messages"][-1]
            #     if last_msg.type == "ai":
            #         print(f"AI: {last_msg.content}")
            #     elif last_msg.type == "tool":
            #         print(f"工具: {last_msg.content}")


            # builder = StateGraph(MessagesState)
            # builder.add_node("supervisor",supervisor_agent)
            # builder.add_edge(START,"supervisor")
            # graph = builder.compile(checkpointer=memery)
        except Exception as e:
            print(f"❌ 多智能体系统初始化失败: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    async def plan_trip(self,request: TripRequest) -> TripPlan:
        """
        使用多智能体协作生成旅行计划
        Args:
            request: 旅行请求
        Returns:
            旅行计划
        """
        try:
            print(f"\n{'='*60}")
            print(f"🚀 开始多智能体协作规划旅行...")
            print(f"目的地: {request.city}")
            print(f"日期: {request.start_date} 至 {request.end_date}")
            print(f"天数: {request.travel_days}天")
            print(f"偏好: {', '.join(request.preferences) if request.preferences else '无'}")
            print(f"{'='*60}\n")

            # 调用多智能体完成旅行的规划
            print("生成完整的规划中...")
            # 创建完整的提问
            planner_query = await self._build_planner_query(request)
            # print(f"创建完整的提问 planner_query: {planner_query}\n")

            # 创建完整的回答
            planner_response = await self._build_planner_response(planner_query)
            # print(f"创建完整的回答 planner_response: {planner_response}\n")

            # 解析最终计划
            trip_plan = await self._parse_response(planner_response, request)
            # print(f"解析最终计划 trip_plan: {trip_plan}\n")

            return trip_plan

        except Exception as e:
            print(f"❌ 生成旅行计划失败: {str(e)}")
            import traceback
            traceback.print_exc()
            # 返回请求失败时的备用计划
            # return self._create_fallback_plan(request)
        

    async def _build_planner_query(self, request: TripRequest) -> str:
        """创建完整的提问"""
        query = f"""请根据以下信息生成{request.city}的{request.travel_days}天的旅游计划：

        ***基本信息：***
        - 城市：{request.city}
        - 日期：{request.start_date}至{request.end_date}
        - 天数：{request.travel_days}
        - 交通方式：{request.transportation}
        - 住宿：{request.accommodation}
        - 偏好：{','.join(request.preferences) if request.preferences else '无'}

        ***额外要求：***
        {','.join(request.free_text_input if request.free_text_input else '无')}

        """

        return query


    async def _build_planner_response(self, query: str) -> str:
        """调用多智能体产生回答"""

        # 得到已编译的状态图
        DB_URL = "postgresql://kai:1738560521@localhost:5432/agents_db?sslmode=disable"
        try:
            async with(
                AsyncPostgresStore.from_conn_string(DB_URL) as store,
                AsyncPostgresSaver.from_conn_string(DB_URL) as checkpointer
            ):
                await checkpointer.setup()
                await store.setup()

                app = self.supervisor_agent.compile(checkpointer=checkpointer, store=store)


                config = {"configurable": {"thread_id": "thread-1"}}
                inputs = {"messages": [{"role": "user", "content": query}]}

                short_memory = await app.aget_state(config)
                long_memory = [state async for state in app.aget_state_history(config)]

                response = await app.ainvoke(inputs,config)

                # async for event in app.astream(inputs, config=config, stream_mode="values"):
                #     if "messages" in event and len(event["messages"]) > 0:
                #         last_msg = event["messages"][-1]
                #         if getattr(last_msg, "type", None) == "ai":
                #             response = last_msg.content
                
                if not short_memory:
                    logger.info("short_memory is empty")
                else:
                    logger.info(f"short_memory:\n{short_memory}")

                return response['messages'][-1].content or "No AI response found"

        except Exception as e:
            print(f"❌ 多智能体系统连接数据库失败: {str(e)}")
            raise
        
        # self.supervisor_agent = self.supervisor_agent.compile(checkpointer=self.memory)
        # app = self.supervisor_agent

        # config = {"configurable": {"thread_id": "1"}}
        # inputs = {
        #     "messages": [
        #         {"role": "user","content": query}
        #     ]
        # }

        # i = 0

        # # 同步调用
        # # app.invoke(input=inputs,
        # #            config=config)

        # try:
        #     async for event in app.astream(inputs, config=config, stream_mode="values"):
        #         last_msg = event["messages"][-1]
        #         i+=1
        #         print(f"\n event{i}:\n{str(event)}\n")
        #         # print(f"\n last_msg{i}:\n{last_msg}\n")
        #         # print(f"\n last_msg{i}.type:\n{last_msg.type}\n")


        #         if last_msg.type == "ai":
        #             # print(f"AI: {last_msg.content}")
        #             response = last_msg.content
        #         # elif last_msg.type == "tool":
        #         #     print(f"工具: {last_msg.content}")
        # except Exception as e:
        #     raise
        
        # # print("\n✅ 多智能体协作完成，获得回答。\n")
        # # print("response:"+response+"\n")

        # return response
    

    async def _parse_response(self, response: str, request: TripRequest) -> TripPlan:
        """解析回答 str对象 为 TripPlan对象"""
        try:
            # 尝试从响应中提取JSON
            # 查找JSON代码块
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "```" in response:
                json_start = response.find("```") + 3
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.find("}", json_start) + 1
                json_str = response[json_start:json_end] 
            else:
                raise ValueError("响应中未找到JSON数据")
            
            # 解析JSON
            # json.load(file)是文件转Python对象，如dict等
            # json.loads(str)是字符串转Python对象
            data = json.loads(json_str)


            # TODO: 解析data，转换为TripPlan对象

            # 转换为TripPlan对象
            trip_plan = TripPlan(**data)


            print("✅ 成功解析旅行计划。")

            # print(f"\n{'='*60}\n")
            # print(f"data:{data}\n")
            # print(f"type(data):{type(data)}\n")

            # print(f"\n{'='*60}\n")
            # print(f"trip_plan:{trip_plan}\n")

            # print(f"\n{'='*60}\n")
            # print(f"type(trip_plan):{type(trip_plan)}\n")
            # print(f"\n{'='*60}\n")

            return trip_plan
        
        except Exception as e:
            print(f"⚠️  解析响应失败: {str(e)}")
            # print(f"   将使用备用方案生成计划")
            # return self._create_fallback_plan(request)
       
# 全局多智能体系统实例
_multi_agents = None

async def get_multi_agents():
    global _multi_agents

    if _multi_agents is None:
        _multi_agents = MultiAgents()
        await _multi_agents.create()

    return _multi_agents




