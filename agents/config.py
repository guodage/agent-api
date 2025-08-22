import os
from typing import Optional
from agno.models.azure import AzureOpenAI

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """应用配置管理类"""

    # Azure OpenAI 配置
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_MODEL_ID: str = "gpt-4o"

    # 报告配置
    DEFAULT_REPORT_PATH: str = "report.md"
    REPORT_ENCODING: str = "utf-8"

    # Agent 配置
    AGENT_DESCRIPTION: str = "你是一个专业的AI领域资讯分析师。你的任务是抓取全球范围内关于AI Agent的最新、最热门的资讯。"

    AGENT_INSTRUCTIONS: str = """
你是一位专业的AI Agent领域资讯分析师。你的任务是：

1. 使用搜索工具获取今日热门的AI Agent领域资讯
2. 对获取的资讯进行分析和总结
3. 用中文输出一份结构化的资讯报告

报告格式要求：
- 标题：今日AI Agent领域热门资讯
- 按重要性排序
- 每条资讯包含：标题、来源、核心内容、技术亮点
- 最后提供趋势分析和总结

请确保内容准确、有价值，重点关注创新和行业动态。
"""

    AGENT_EXPECTED_OUTPUT: str = """
一个格式清晰的Markdown报告，包含以下部分：
- 主标题：今日Agent领域热门资讯
- 每个资讯条目：
  - `### 资讯标题`
  - `**简要总结:** 总结内容...`
"""

    # 性能监控配置
    PERFORMANCE_RATING_THRESHOLDS = {
        "excellent": 2.0,  # 小于2秒为优秀
        "good": 5.0,  # 小于5秒为良好
    }

    @classmethod
    def validate_config(cls) -> bool:
        """验证必要的配置是否存在"""
        required_configs = [
            cls.AZURE_OPENAI_API_KEY,
            cls.AZURE_OPENAI_ENDPOINT,
        ]

        missing_configs = []
        for i, config in enumerate(required_configs):
            if not config:
                config_names = ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
                missing_configs.append(config_names[i])

        if missing_configs:
            print(f"❌ 缺少必要的环境变量: {', '.join(missing_configs)}")
            return False

        return True

    @classmethod
    def get_azure_openai_config(cls, id) -> dict:
        """获取Azure OpenAI配置字典"""
        # 先写死
        id = cls.AZURE_OPENAI_MODEL_ID
        return {
            "id": cls.AZURE_OPENAI_MODEL_ID if not id else id,
            "api_key": cls.AZURE_OPENAI_API_KEY,
            "api_version": cls.AZURE_OPENAI_API_VERSION,
            "azure_endpoint": cls.AZURE_OPENAI_ENDPOINT,
            "azure_deployment": cls.AZURE_OPENAI_DEPLOYMENT,
        }


def get_ai_model(model_id):
    config = Config.get_azure_openai_config(model_id)
    return AzureOpenAI(**config)

