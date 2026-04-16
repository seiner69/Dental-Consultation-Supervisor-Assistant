import unittest
import os
import shutil
# 注意：不需要再 import sys 来手动修补路径了！

from src.core.models import ConsultationReport
from src.database.repository import ConsultationRepository
from config.settings import settings
class TestCoreSystem(unittest.TestCase):
    """
    DCSA 核心业务逻辑测试套件
    覆盖：数据契约验证、数据持久化、配置加载
    """

    def setUp(self):
        """
        [环境搭建] 
        每次测试开始前自动执行。
        我们将数据库路径指向一个临时的 'test_db.csv'，防止污染您的真实数据。
        """
        self.original_db_path = settings.DB_PATH
        self.test_db_path = os.path.join("data", "db", "test_consultation.csv")
        
        # 临时覆盖全局配置中的 DB_PATH
        settings.DB_PATH = self.test_db_path
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.test_db_path), exist_ok=True)
        
        # 初始化一个针对临时文件的仓库实例
        self.repo = ConsultationRepository()

    def tearDown(self):
        """
        [环境清理]
        每次测试结束后自动执行。
        删除测试用的 CSV 文件，并将配置还原，以免影响其他测试。
        """
        if os.path.exists(self.test_db_path):
            try:
                os.remove(self.test_db_path)
            except PermissionError:
                pass # 有时候文件占用会导致删除失败，忽略即可
                
        # 还原配置
        settings.DB_PATH = self.original_db_path

    def test_01_data_model_validation(self):
        """
        [测试 1] 数据契约 (Data Contract) 验证
        测试 Pydantic 是否能正确处理数据，拦截非法输入。
        这是 DataFlow 思想的体现：确保流转的数据是符合 Schema 的。
        """
        print("\n🧪 Testing Data Model Validation...")
        
        # A. 测试合法数据
        valid_data = {
            "summary": "测试摘要：患者咨询种植牙",
            "customer_intent": "高",
            "sales_score": 85,
            "pain_points": "怕痛、价格贵",
            "good_points": "流程清晰",
            "bad_points": "无",
            "next_step": "预约CT"
        }
        report = ConsultationReport(**valid_data)
        
        # 断言：验证属性是否正确赋值
        self.assertEqual(report.sales_score, 85)
        self.assertEqual(report.customer_intent, "高")

        # B. 测试非法数据 (类型错误)
        # 尝试把分数设为无法转成数字的字符串，Pydantic 应该报错
        try:
            invalid_data = valid_data.copy()
            invalid_data["sales_score"] = "NotANumber"
            ConsultationReport(**invalid_data)
            self.fail("❌ Pydantic 未能拦截非法类型数据！")
        except ValueError:
            print("   ✅ Pydantic 成功拦截了非法数据输入。")

    def test_02_database_persistence(self):
        """
        [测试 2] 数据持久化 (Data Persistence)
        测试 CSV 读写是否形成闭环：存进去的数据 = 读出来的数据。
        这是 SGI-Bench 中的“可行性 (Feasibility)”验证。
        """
        print("\n🧪 Testing Database Persistence...")
        
        # 1. 创建一条虚拟报告
        mock_report = ConsultationReport(
            summary="Unit Test Summary",
            customer_intent="High",
            sales_score=99,
            pain_points="None",
            good_points="Perfect",
            bad_points="None",
            next_step="Close deal"
        )
        
        # 2. 保存记录
        success = self.repo.save_record(
            consultant="Test Dr.",
            patient="Test Patient 007",
            is_deal="No",
            report=mock_report,
            transcript="[说话人 0]: Test dialogue"
        )
        self.assertTrue(success, "保存记录失败，请检查 save_record 方法")
        
        # 3. 读取并验证
        df = self.repo.load_records()
        self.assertFalse(df.empty, "数据库不应为空")
        
        # 获取最新的一条记录（因为是倒序的，所以是第一条）
        latest_record = df.iloc[0]
        
        # 验证关键字段是否一致
        self.assertEqual(latest_record["患者姓名"], "Test Patient 007")
        self.assertEqual(latest_record["评分"], 99)
        self.assertEqual(latest_record["客户意向"], "High")
        print("   ✅ 数据库 读/写 回环测试通过。")

    def test_03_config_loading(self):
        """
        [测试 3] 配置安全性检查
        确保环境变量被正确加载。
        """
        print("\n🧪 Testing Configuration...")
        
        # 验证 Key 是否存在
        # 注意：这里假设您已经在本地配置了 .env 或者环境变量
        # 如果是 CI/CD 环境，需要注入 Mock 环境变量
        if not settings.DASHSCOPE_API_KEY:
            print("   ⚠️ 警告：DASHSCOPE_API_KEY 为空。请检查 .env 文件。")
        else:
            # 简单的格式验证，例如 Key 长度是否合理
            self.assertTrue(len(settings.DASHSCOPE_API_KEY) > 10, "API Key 格式似乎不对")
            print("   ✅ 配置加载正常。")
            
        self.assertEqual(settings.APP_NAME, "Dental Consultation Supervisor Assistant")

if __name__ == "__main__":
    unittest.main()
'''

### 🚀 如何运行这个测试？

1.  打开您的终端（Terminal）。
2.  确保您在项目的**根目录**下（即可以看到 `src` 和 `tests` 文件夹的地方）。
3.  运行以下命令：

```bash
python -m unittest tests/test_core.py
```

### 🧐 预期输出结果

如果您的环境配置正确，且代码没有逻辑错误，您应该会看到类似以下的绿色输出：

```text
🧪 Testing Data Model Validation...
   ✅ Pydantic 成功拦截了非法数据输入。

🧪 Testing Database Persistence...
   ✅ 数据库 读/写 回环测试通过。

🧪 Testing Configuration...
   ✅ 配置加载正常。
.
----------------------------------------------------------------------
Ran 3 tests in 0.xxx s

OK
'''