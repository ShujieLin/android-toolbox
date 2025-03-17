import sys
import os
# 将项目根目录添加到系统路径，确保可以找到其他模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.device_manager import AppRunner

# __name__ 变量：
# 当 Python 文件被直接运行时，__name__ 的值是 "__main__"。
# 当 Python 文件被导入时，__name__ 的值是模块的文件名（不含 .py 后缀）。
# if __name__ == "__main__": 的作用：
# 判断当前模块是否作为主程序运行，从而决定是否执行其中的代码。
if __name__ == "__main__":
    runner = AppRunner()
    runner.run()

