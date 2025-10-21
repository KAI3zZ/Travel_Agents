"""LLM服务模块"""
from langchain_openai import ChatOpenAI
from ..config import get_settings

# 全局LLM实例
_llm_instance = None

def get_llm() -> ChatOpenAI:
    """
    获取LLM实例(单例模式)
    Returns:
        CharOpenAI实例
    """
    global _llm_instance

    if not _llm_instance:
        settings = get_settings()
        _llm_instance = ChatOpenAI(
            model=settings.llm_model_id,
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            temperature=0.1
        )

        print(f"✅ LLM服务初始化成功")
        print(f"   模型: {_llm_instance.model_name}")

    return _llm_instance

def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None