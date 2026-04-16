import sys
import os
import unittest

def main():
    """
    企业级测试启动入口
    解决所有路径依赖痛点 (Path Hell)
    """
    # 1. 获取当前脚本所在的绝对路径 (项目根目录)
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 2. 将根目录强制插入到 Python 搜索路径的第一个位置
    # 这样 Python 就能毫无障碍地找到 'config' 和 'src' 模块
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print(f"🚀 [System] Project Root Detected: {project_root}")
    print(f"🔄 [System] Injecting path dependencies...")

    # 3. 自动发现并运行所有测试
    # start_dir: 从哪里开始找测试文件 (tests 文件夹)
    # pattern: 测试文件的命名规则 (test_*.py)
    loader = unittest.TestLoader()
    start_dir = os.path.join(project_root, 'tests')
    
    # 防御性编程：检查 tests 目录是否存在
    if not os.path.exists(start_dir):
        print(f"❌ [Error] Tests directory not found at: {start_dir}")
        sys.exit(1)

    suite = loader.discover(start_dir, pattern='test_*.py')

    # 4. 运行测试并输出结果
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 5. 根据测试结果返回退出码 (CI/CD 友好)
    if result.wasSuccessful():
        print("\n✅ All tests passed! System is stable.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()