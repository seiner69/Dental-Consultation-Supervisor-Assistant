from pydantic import BaseModel, Field

class ConsultationReport(BaseModel):
    """
    咨询分析报告的数据结构
    对应 DataFlow 中的 Standardized Output
    """
    summary: str = Field(description="50字以内的对话摘要")
    customer_intent: str = Field(description="客户意向等级: 高/中/低")
    sales_score: int = Field(description="销售评分 0-100")
    pain_points: str = Field(description="客户核心痛点")
    good_points: str = Field(description="咨询师做得好的地方")
    bad_points: str = Field(description="咨询师的失误点")
    next_step: str = Field(description="下一步跟进建议")