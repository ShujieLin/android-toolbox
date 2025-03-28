import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.adb_tools import ADBTools
from ui.main_ui import MainWindow
from core.log_category_manager import LogCategoryManager
import logging
import threading
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
        self.log_category_manager = LogCategoryManager(self.adb_tools) 
        if self.ui:
            self._init_others()
            self._init_ui_event() # 初始化UI
          

    def _init_ui_event(self):
        self.ui.refresh_btn.clicked.connect(self.handle_refresh_devices)
   
        self.ui.browse_btn.clicked.connect(self.get_selected_explorer_path)
        # 添加点击事件
        self.ui.multi_select_list_view.itemSelectionChanged.connect(self.handle_multi_select_list_selection_changed)
     
        self.ui.pull_one_type_one_day_logs_btn.clicked.connect(self.pull_selected_logs_1_day)
        

    def _init_others(self):
        self.handle_refresh_devices()
        logging.info(f"默认保存路径: {self.ui.log_save_path}")
        self.adb_tools.set_selected_windows_path(self.ui.log_save_path)
        self.all_log_categorys = []
        self.all_log_categorys = self.adb_tools.get_log_categorys(self.devices[0])
        self.ui.init_multi_select_list_items(self.all_log_categorys)
        self.selected_logs_categorys = [] # 当前选中的日志类型

    def pull_all_logs_wrapper(self):
        self.log_category_manager.pull_all_logs_wrapper(self.devices[0])
    
    def pull_selected_logs_1_day(self):
        try:
            logging.info("Entering pull_selected_logs_1_day method")

            if not self.devices:
                logging.error("No devices connected")
                # 添加弹窗提示
                self.ui.show_message_box("No devices connected")
                return
            
            # 获取填写的日期
            self.date = self.ui.date_edit.text()
            if not self.date:
                logging.error("No date selected")
                self.ui.show_message_box("No date selected")
                return
            
            if not self.selected_logs_categorys:
                logging.error("No log categories selected")
                self.ui.show_message_box("No log categories selected")
                return
            
            logging.info("Pulling logs for selected items")
            self.log_category_manager.pull_selected_logs_1_day(self.devices[0],self.selected_logs_categorys,self.date)
        except Exception as e:
            logging.error(f"拉取日志失败: {str(e)}")

    def get_selected_explorer_path(self):
        logging.info(f"选择的保存路径: {self.ui.log_save_path}")
        self.adb_tools.set_selected_windows_path(self.ui.log_save_path)

        
    def handle_multi_select_list_selection_changed(self):
        """处理多选列表选择变化"""
        selected_items = [item.text() for item in self.ui.multi_select_list_view.selectedItems()]
        self.selected_logs_categorys = selected_items
        logging.info(f"Selected items: {selected_items}")
        # 把选中的日志类型传递给adb_tools
        self.adb_tools.set_selected_log_categorys(selected_items)

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

# 新增的类，用于运行应用程序
class AppRunner:
    def run(self):
        app = QApplication(sys.argv)
        controller = DeviceController()
        controller.ui.show()
        sys.exit(app.exec_())