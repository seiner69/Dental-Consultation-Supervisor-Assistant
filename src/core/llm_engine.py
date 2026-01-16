import logging
from langchain_community.chat_models import ChatTongyi
from langchain_core.messages import SystemMessage, HumanMessage
from config.settings import settings
from src.core.models import ConsultationReport

logger = logging.getLogger(__name__)

class AnalysisEngine:
    def __init__(self):
        self.llm = ChatTongyi(
            model="qwen-plus", # 建议使用 plus 或 max 以获得更好的推理能力
            api_key=settings.DASHSCOPE_API_KEY,
            temperature=0.1    # 保持客观冷静
        )
        # 核心：使用结构化输出解析器
        self.parser = self.llm.with_structured_output(ConsultationReport)

    def analyze_consultation(self, text: str) -> ConsultationReport:
        if not text:
            raise ValueError("输入文本为空")

        system_prompt = """
        你是一名专业的口腔门诊运营督导（Supervisor）。
        任务：根据咨询录音文本，对咨询师的专业性、沟通技巧和销售逻辑进行深度审计。
        原则：
        1. 评分严格：满分100，及格60。未挖掘出预算或病史的一律不及格。
        2. 痛点精准：必须指出客户最担心的问题（如怕痛、嫌贵、不信任）。
        3. 建议落地：给出具体的话术改进建议。
        """

        try:
            result = self.parser.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"【录音文本】：\n{text}")
            ])
            return result
        except Exception as e:
            logger.error(f"Analysis Failed: {e}")
            raise e