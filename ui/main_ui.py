# Add these at the top (before other imports)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Then modify the problematic import
import logging
from PyQt5.QtWidgets import  QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QTextEdit,QLabel,QFileDialog

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# UI层 (MainWindow)：只负责界面展示和事件触发
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.log_save_path = os.path.expanduser("~\\Documents")  # 默认保存到文档目录
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
        self.left_panel = QVBoxLayout()
        logging.debug('Left panel created')

        
        # 设备列表
        self.device_list = QListWidget()
        # 设备列表（动态计算三行高度）
        self.device_list = QListWidget()
        font_metrics = self.device_list.fontMetrics()
        line_height = font_metrics.height() + 4  # 增加间距
        self.device_list.setFixedHeight(line_height * 3)
        self.left_panel.addWidget(self.device_list)
        logging.debug('Device list created')

        # 日志导出路径
        self.init_explorer()

        # 新增多选列表（放在设备列表下方）
        self.multi_select_list = QListWidget()
        self.multi_select_list.setSelectionMode(QListWidget.MultiSelection)  # 设置为多选模式
        self.multi_select_list.addItems([f"Item {i+1}" for i in range(6)])  # 添加6个测试项
        self.left_panel.addWidget(QLabel("可选项目:"))
        self.left_panel.addWidget(self.multi_select_list)
        
        # 操作按钮
        self.refresh_btn = QPushButton('refresh devices')
        self.pull_one_type_one_day_logs_btn = QPushButton('pull one type one day logs')
        # self.screenshot_btn = QPushButton('屏幕截图')
        # self.install_btn = QPushButton('安装APK')
        # self.logcat_btn = QPushButton('查看日志')
        logging.debug('Buttons created')

        for btn in [
                    self.refresh_btn,
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

    
    def init_explorer(self):
        """ 初始化文件浏览器 """
        
        # 新增日志路径组件（放在设备列表下方）
        log_path_layout = QHBoxLayout()
        self.log_path_edit = QTextEdit()
        self.log_path_edit.setMaximumHeight(30)
        self.log_path_edit.setText(self.log_save_path)
        
        browse_btn = QPushButton("...")
        browse_btn.clicked.connect(self.choose_log_path)
        browse_btn.setMaximumWidth(30)

        log_path_layout.addWidget(QLabel("日志路径:"))
        log_path_layout.addWidget(self.log_path_edit)
        log_path_layout.addWidget(browse_btn)
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
        if path:
            self.log_save_path = path
            self.log_path_edit.setText(path)