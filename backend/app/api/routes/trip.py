"""旅行规划API路由"""

from fastapi import APIRouter, HTTPException
from ...models.schemas import (
    TripRequest,
    TripPlanResponse,
    ErrorResponse
)
from ...agents.multi_agents import get_multi_agents

router = APIRouter(prefix="/trip",tags=["旅行计划"])

@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求,生成详细的旅行计划"
)
async def plan_trip(request: TripRequest):
    """
    根据request,调用多智能体生成回答(TripPlan类型),最后生成响应
    Args:
        request:旅行请求
    Returns:
        旅行计划响应
    """
    try:
        print("🔄 获取多智能体系统实例...")
        multi_agents = await get_multi_agents()

        print("🚀 开始生成旅行计划...")
        trip_plan = await multi_agents.plan_trip(request=request)

        # print("返回到前端的相应数据:\n"+"data=trip_plan:\n"+str(trip_plan)+"\n")

        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan
        )
    
    except Exception as e:
        print(f"❌ 生成旅行计划失败：{str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败：{str(e)}"
        )

@ router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常"
)
async def health_check():
    """健康检查"""
    try:
        multi_agents = await get_multi_agents()

        return {
            "status" : "health",
            "service" : "trip",
            "agents_name" : multi_agents.supervisor_agent.name
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"服务不可用:{str(e)}"
        )