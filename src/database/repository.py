import pandas as pd
import os
import datetime
from config.settings import settings
from src.core.models import ConsultationReport

class ConsultationRepository:
    def __init__(self):
        self.db_path = settings.DB_PATH
        self._init_db()

    def _init_db(self):
        """确保 CSV 文件和目录存在，并初始化表头"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            df = pd.DataFrame(columns=[
                "时间", "咨询师", "患者姓名", "是否成交", 
                "客户意向", "评分", "痛点", "优点", 
                "失误点", "下一步建议", "摘要", "对话实录"  # <--- 新增字段
            ])
            df.to_csv(self.db_path, index=False, encoding="gbk")

    def save_record(self, consultant: str, patient: str, is_deal: str, report: ConsultationReport, transcript: str):
        """保存单条分析记录，包括对话实录"""
        new_row = {
            "时间": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "咨询师": consultant,
            "患者姓名": patient,
            "是否成交": is_deal,
            "客户意向": report.customer_intent,
            "评分": report.sales_score,
            "痛点": report.pain_points,
            "优点": report.good_points,
            "失误点": report.bad_points,
            "下一步建议": report.next_step,
            "摘要": report.summary,
            "对话实录": transcript  # <--- 保存对话内容
        }
        
        try:
            # 读取旧数据
            if os.path.exists(self.db_path):
                df = pd.read_csv(self.db_path, encoding="gbk")
            else:
                self._init_db()
                df = pd.read_csv(self.db_path, encoding="gbk")
            
            # 追加新数据 (concat 会自动处理列对齐，如果旧数据没有"对话实录"列，会自动填充 NaN)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(self.db_path, index=False, encoding="gbk", errors="replace")
            return True
        except Exception as e:
            print(f"Database Error: {e}")
            return False

    def load_records(self) -> pd.DataFrame:
        """加载所有记录 (用于主管端统计)"""
        if not os.path.exists(self.db_path):
            return pd.DataFrame()
        try:
            df = pd.read_csv(self.db_path, encoding="gbk")
            # 处理空值，防止 UI 报错
            df.fillna("", inplace=True)
            
            # 生成显示标签
            if not df.empty:
                df["显示标签"] = (
                    df["时间"] + " | " + 
                    df["咨询师"] + " vs " + df["患者姓名"] + 
                    " | " + df["评分"].astype(str) + "分"
                )
            return df.iloc[::-1] # 倒序返回（最新的在最前）
        except Exception as e:
            print(f"Load Error: {e}")
            return pd.DataFrame()