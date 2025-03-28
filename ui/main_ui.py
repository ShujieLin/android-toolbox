# Add these at the top (before other imports)
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Then modify the problematic import
import logging
from datetime import datetime
from PyQt5.QtWidgets import  QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QTextEdit,QLabel,QFileDialog,QLineEdit
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp


# UI层 (MainWindow)：只负责界面展示和事件触发
class MainWindow(QMainWindow):
    def __init__(self,adb_tools):
        super().__init__()
        self._init_datas()
        self.initUI()
        self.adb_tools = adb_tools

    def _init_datas(self):
        self.config_path = os.path.expanduser("~/.AndroidDevTools/config.json")
        self._load_config()
        if not hasattr(self, 'log_save_path'):
            self.log_save_path = os.path.expanduser("~\\Documents")  # 默认保存到文档目录

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
        self.left_panel = QVBoxLayout()
        logging.debug('Left panel created')

    
        self.__init_multi_select_list_part()
       

        # 日志导出路径
        self.init_explorer()
        self.__init_date_part()

        self.init_multi_select_list()

        
    
        self.pull_all_logs_btn = QPushButton('pull all logs for selected items')
        self.pull_one_type_one_day_logs_btn = QPushButton('pull one type one day logs')
        logging.debug('Buttons created')

        for btn in [
                    self.pull_all_logs_btn,
                    self.pull_one_type_one_day_logs_btn
                   ]:
            self.left_panel.addWidget(btn)
            btn.setMinimumHeight(40)

        # 右侧日志显示
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        # 布局组合
        main_layout.addLayout(self.left_panel, 1)
        main_layout.addWidget(self.log_output, 3)

    def __init_date_part(self):
        # 填写日期，限制格式，比如"20250312"
        self.date_edit = QLineEdit()  # 使用 QLineEdit 替代 QTextEdit
        self.date_edit.setMaximumHeight(30)
        # 定义日期格式的正则表达式
        date_regex = QRegExp(r'^\d{8}$')
        date_validator = QRegExpValidator(date_regex, self.date_edit)

        # 设置验证器到输入框
        self.date_edit.setValidator(date_validator)

        # 获取当前日期并格式化为 YYYYMMDD 格式
        today = datetime.today().strftime("%Y%m%d")
        # 设置默认日期
        self.date_edit.setText(today)

        # 添加到左侧控制面板
        self.left_panel.addWidget(QLabel("输入日志日期 (YYYYMMDD), 例如:20250312"))
        self.left_panel.addWidget(self.date_edit)

    def get_date_input(self):
        """
        获取 date_edit 输入框中填写的日期。

        :return: 输入的日期字符串，如果输入框为空则返回空字符串。
        """
        return self.date_edit.text()

    def __init_multi_select_list_part(self):
        """
        初始化设备列表和刷新按钮，并添加到左侧控制面板。
        """
        # 设备列表
        self.device_list = QListWidget()
        # 设备列表（动态计算三行高度）
        font_metrics = self.device_list.fontMetrics()
        line_height = font_metrics.height() + 4  # 增加间距
        self.device_list.setFixedHeight(line_height * 3)
        self.left_panel.addWidget(self.device_list)
        logging.debug('Device list created')
        # 操作按钮
        self.refresh_btn = QPushButton('refresh devices')
        self.left_panel.addWidget(self.refresh_btn)


    def init_multi_select_list(self):
              # 新增多选列表（放在设备列表下方）
        self.multi_select_list = QListWidget()
        self.multi_select_list.setSelectionMode(QListWidget.MultiSelection)  # 设置为多选模式
        self.left_panel.addWidget(QLabel("可选项目:"))
        self.left_panel.addWidget(self.multi_select_list)

    def update_multi_select_list(self, items):
        # 清空列表
        self.multi_select_list.clear()
        # 直接将 items 中的元素逐个添加到列表中
        self.multi_select_list.addItems(items)  
   
    def _load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_path):
                logging.info(f"加载配置文件: {self.config_path}")
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    self.log_save_path = config.get('log_save_path', os.path.expanduser("~\\Documents"))
                    logging.info(f"日志保存路径: {self.log_save_path}")
        except Exception as e:
            print(f"加载配置文件失败: {e}")

    def _save_config(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump({'log_save_path': self.log_save_path}, f)
                logging.info(f"配置已保存到: {self.config_path}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def init_explorer(self):
        """ 初始化文件浏览器 """
        
        # 新增日志路径组件（放在设备列表下方）
        log_path_layout = QHBoxLayout()
        self.log_path_edit = QTextEdit()
        self.log_path_edit.setMaximumHeight(30)
        self.log_path_edit.setText(self.log_save_path)
        
        self.browse_btn = QPushButton("...")
        self.browse_btn.clicked.connect(self.choose_log_path)
        self.browse_btn.setMaximumWidth(30)

        log_path_layout.addWidget(QLabel("日志路径:"))
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(self.browse_btn)
        self.left_panel.addLayout(log_path_layout)


    def update_device_list(self, devices):
        """
        更新设备列表
        :param devices: 设备列表
        """
        self.device_list.clear()
        self.device_list.addItems(devices)

    def get_selected_items(self):
        """ 获取当前选中的项目 """
        return [item.text() for item in self.multi_select_list.selectedItems()]
    


    def choose_log_path(self):
        """选择日志保存路径"""
        path = QFileDialog.getExistingDirectory(self, "选择日志保存目录", self.log_save_path)
        logging.info("Choosing log path:%s",path)
        if path:
            self.log_save_path = path
            self.log_path_edit.setText(path)
            self._save_config()  # 保存新路径
        return path