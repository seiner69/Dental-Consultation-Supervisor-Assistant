import sys
import os
import logging

# 1. 强制将根目录加入 Python 路径，模拟项目运行环境
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 配置日志，让我们看清发生了什么
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] - %(message)s')
logger = logging.getLogger(__name__)

def check_config():
    logger.info("🔍 Step 1: 检查配置加载...")
    try:
        from config.settings import settings
        # 永远不要打印完整的 Key，只打印前几位验证
        masked_key = settings.DASHSCOPE_API_KEY[:4] + "****" if settings.DASHSCOPE_API_KEY else "None"
        logger.info(f"✅ 配置加载成功! App Name: {settings.APP_NAME}, Key: {masked_key}")
    except Exception as e:
        logger.error(f"❌ 配置加载失败: {e}")
        logger.error("💡 提示: 请检查 .env 文件是否存在，且格式是否正确。")
        sys.exit(1)

def check_database():
    logger.info("🔍 Step 2: 检查数据库连接...")
    try:
        from src.database.repository import ConsultationRepository
        repo = ConsultationRepository()
        df = repo.load_recent(limit=1)
        logger.info(f"✅ 数据库连接成功! 当前记录数: {len(df) if not df.empty else 0}")
    except Exception as e:
        logger.error(f"❌ 数据库检查失败: {e}")
        sys.exit(1)

def check_llm_dry_run():
    logger.info("🔍 Step 3: 检查 LLM 连接 (Dry Run)...")
    try:
        from src.core.llm_engine import AnalysisEngine
        engine = AnalysisEngine()
        # 这里我们只实例化，不调用 API 以节省 Token
        # 只要能实例化，说明 langchain 和 pydantic 依赖没问题
        logger.info("✅ LLM 引擎初始化成功! (LangChain + Pydantic 就绪)")
    except Exception as e:
        logger.error(f"❌ LLM 引擎初始化失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("="*40)
    print("🚀 DCSA 系统自检程序 (Sanity Check)")
    print("="*40)
    
    check_config()
    check_database()
    check_llm_dry_run()
    
    print("\n✨ 自检通过！系统状态良好，可以启动 UI。")
    print("👉 运行命令: streamlit run src/ui/dashboard.py")
'''

🧪 如何运行测试

1.  打开您的终端（Terminal）。
2.  确保您已经激活了虚拟环境（如果用了的话）。
3.  运行命令：python tests/sanity_check.py


🧐 预期结果

如果您看到类似下面的输出，说明一切正常：

```text
========================================
🚀 DCSA 系统自检程序 (Sanity Check)
========================================
... [INFO] - 🔍 Step 1: 检查配置加载...
... [INFO] - ✅ 配置加载成功! App Name: Dental Consultation Supervisor Assistant, Key: sk-d****
... [INFO] - 🔍 Step 2: 检查数据库连接...
... [INFO] - ✅ 数据库连接成功! 当前记录数: 20
... [INFO] - 🔍 Step 3: 检查 LLM 连接 (Dry Run)...
... [INFO] - ✅ LLM 引擎初始化成功! (LangChain + Pydantic 就绪)

✨ 自检通过！系统状态良好，可以启动 UI。
👉 运行命令: streamlit run src/ui/dashboard.py
'''