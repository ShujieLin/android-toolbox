# Add these at the top (before other imports)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Then modify the problematic import
import logging
from PyQt5.QtWidgets import  QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QTextEdit

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# UI层 (MainWindow)：只负责界面展示和事件触发
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ADB Tool - power by linshujie')
        self.setGeometry(300, 300, 800, 600)
        logging.debug('Initializing UI')

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        logging.debug('Main layout created')

        # 左侧控制面板
        left_panel = QVBoxLayout()
        logging.debug('Left panel created')
        
        # 设备列表
        self.device_list = QListWidget()
        left_panel.addWidget(self.device_list)
        logging.debug('Device list created')
        
        # 操作按钮
        self.refresh_btn = QPushButton('refresh devices')
        # self.screenshot_btn = QPushButton('屏幕截图')
        # self.install_btn = QPushButton('安装APK')
        # self.logcat_btn = QPushButton('查看日志')
        logging.debug('Buttons created')

        for btn in [
                    self.refresh_btn
                   ]:
            left_panel.addWidget(btn)
            btn.setMinimumHeight(40)

        # 右侧日志显示
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # 布局组合
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(self.log_output, 3)

        
    def update_device_list(self, devices):
        """
        更新设备列表
        :param devices: 设备列表
        """
        self.device_list.clear()
        self.device_list.addItems(devices)