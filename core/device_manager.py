import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.adb_tools import ADBTools
from ui.main_ui import MainWindow
import logging
from PyQt5.QtCore import pyqtSignal,QObject  
from PyQt5.QtWidgets import QApplication

# 为类创建独立的日志记录器
logger = logging.getLogger('DeviceController')

#业务层 (DeviceController)：处理事件响应和逻辑协调
class DeviceController(QObject):
    # 添加设备列表更新信号
    signal_pull_one_type_one_day_logs = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()  # 调用父类的构造函数
        self.adb_tools = ADBTools()
        self.ui = MainWindow(self.adb_tools)
        if self.ui:
            self._init_ui_event() # 初始化UI
            self._init_others()

    def _init_ui_event(self):
        self.ui.refresh_btn.clicked.connect(self.handle_refresh_devices)
        self.ui.pull_one_type_one_day_logs_btn.clicked.connect(self.pull_one_type_one_day_logs)
        self.ui.browse_btn.clicked.connect(self.get_selected_explorer_path)
        # 添加点击事件
        self.ui.multi_select_list.itemSelectionChanged.connect(self.handle_multi_select_list_selection_changed)

    def _init_others(self):
        self.handle_refresh_devices()
        logging.info(f"默认保存路径: {self.ui.log_save_path}")
        log_categorys = []
        log_categorys = self.adb_tools.get_log_categorys(self.devices[0])
        self.ui.update_multi_select_list(log_categorys)

    def get_selected_explorer_path(self):
        logging.info(f"选择的保存路径: {self.ui.log_save_path}")

        
    def handle_multi_select_list_selection_changed(self):
        """处理多选列表选择变化"""
        selected_items = [item.text() for item in self.ui.multi_select_list.selectedItems()]
        logging.info(f"Selected items: {selected_items}")

    # 这里有两个作用，一个是分离adb_tools的耦合。另一个是分离ui的耦合。
    def handle_refresh_devices(self):
        logging.info("Handling device refresh")
        """处理设备刷新操作"""
        try:
            self.devices = self.adb_tools.get_connected_devices()
            logging.info(f"Found {len(self.devices)} devices")
            self.ui.update_device_list(self.devices) # 调用UI的方法
            logging.info(f"已刷新 {len(self.devices)} 个设备")
        except Exception as e:
            logging.error(f"刷新设备失败: {str(e)}")

    def pull_one_type_one_day_logs(self):
        logging.info("Handling pull one type one day logs")
        try:
            
            self.adb_tools.pull_one_type_one_day_logs(self.adb_tools.get_connected_devices()[0],"SpeechService","20250324")
        except Exception as e:
            logging.error(f"拉取日志失败: {str(e)}")


# 新增的类，用于运行应用程序
class AppRunner:
    def run(self):
        app = QApplication(sys.argv)
        controller = DeviceController()
        controller.ui.show()
        sys.exit(app.exec_())