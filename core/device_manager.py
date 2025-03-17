import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.adb_tools import ADBTools
from ui.main_ui import MainWindow
import logging
from PyQt5.QtCore import pyqtSignal,QObject  
from PyQt5.QtWidgets import QApplication

#业务层 (DeviceController)：处理事件响应和逻辑协调
class DeviceController(QObject):
    # 添加设备列表更新信号
    device_list_update = pyqtSignal(list)

    def __init__(self, adb_tools: ADBTools = None, ui: MainWindow = None):
        super().__init__()  # 调用父类的构造函数
        self.adb_tools =adb_tools
        self.ui = ui
        if self.ui:
            self._connect_signals() # 连接UI事件与ADB操作
            self.device_list_update.connect(self.ui.update_device_list) # 连接信号与槽

    def _connect_signals(self):
        """连接UI事件与ADB操作"""
        self.ui.refresh_btn.clicked.connect(self.handle_refresh_devices)
        
    def handle_refresh_devices(self):
        logging.info("Handling device refresh")
        """处理设备刷新操作"""
        try:
            devices = self.adb_tools.get_connected_devices()
            logging.info(f"Found {len(devices)} devices")
            self.device_list_update.emit(devices) # 发送信号
            logging.info(f"已刷新 {len(devices)} 个设备")
        except Exception as e:
            logging.error(f"刷新设备失败: {str(e)}")



# 新增的类，用于运行应用程序
class AppRunner:
    def run(self):
        app = QApplication(sys.argv)
        controller = DeviceController(ADBTools(), MainWindow())
        controller.ui.show()
        sys.exit(app.exec_())