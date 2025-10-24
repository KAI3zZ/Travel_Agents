"""POI相关API路由"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from ...models.schemas import POIDetailResponse
from ...services.amap_service import get_amap_service
from ...services.unsplash_service import get_unsplash_service

router = APIRouter(prefix="/poi",tags=["POI"])

@router.get(
    "/detail/{poi_id}",
    response_model=POIDetailResponse,
    summary="获取POI详情",
    description="根据POI ID获取详情"
)
async def get_poi_detail(poi_id: str):
    """
    获取POI详情
    Args:
        poi_id: POI ID
    Returns:
        POI详情响应
    """
    try:

        service = get_amap_service()

        # 调用高德地图POI详情API
        result = service.get_poi_detail(poi_id)

        return POIDetailResponse(
            success=True,
            message="获取POI详情成功",
            data=result
        )
    except Exception as e:
        print(f"❌ 获取POI详情失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取POI详情失败: {str(e)}"
        )

@router.get(
    "/search",
    summary="搜索POI",
    description="根据关键词搜索POI"
)
async def search_poi(keywords: str, city: str = "北京"):
    """
    搜索POI
    Args:
        keywords: 搜索关键词
        city: 城市名称
    Returns:
        搜索结果
    """
    try:
        amap_service = get_amap_service()
        result = amap_service.search_poi(keywords, city)

        return {
            "success": True,
            "message": "搜索成功",
            "data": result
        }

    except Exception as e:
        print(f"❌ 搜索POI失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"搜索POI失败: {str(e)}"
        )
    
@router.get(
    "/photo",
    summary="获取景点图片",
    description="根据景点名称从Unsplash获取图片"
)
async def get_attraction_photo(name: str):
    """
    获取景点图片
    Args:
        name: 景点名称
    Returns:
        图片URL
    """
    try:
        service = get_unsplash_service()

        result = service.get_photo_url(f"{name} China landmark")

        # print(f"景区图片的名称: {name}\n", f"图片URL: {result}\n")

        if not result:
            # 如果没找到,尝试只用景点名称搜索
            result = service.get_photo_url(name)

        return {
            "success": True,
            "message": f"成功获取{name}景点图片",
            "data": {
                "name": name,
                "photo_url": result
            }
        }

    except Exception as e:
        print(f"❌ 获取景点图片失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取景点图片失败: {str(e)}"
        )