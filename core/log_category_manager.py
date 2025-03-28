import logging

logger = logging.getLogger('LogCategoryManager')
class LogCategoryManager:

    def __init__(self,adb_tools):
        self.adb_tools = adb_tools
        self.log_categorys = []
        self.selected_log_categorys = []


    def pull_all_logs_wrapper(self,device):
        # pattern = '/sdcard/pudu/log/SpeechService.g3log.20250327*'
        # self.adb_tools.pull_all_logs_in_thread(device, pattern) 

        log_categorys = ["SpeechService","OTAService"]
        date = "20250327"
        self.pull_selected_logs_1_day(device,log_categorys,date)

    def pull_selected_logs_1_day(self,device,log_categorys,date):
        logging.info(f"选择的日期: {date}")
        logging.info(f"选择的日志: {log_categorys}")
        for log_category in log_categorys:
            # 一次拉一个类别的日志，例如core是一个类别
            pattern = f'/sdcard/pudu/log/{log_category}.g3log.{date}*'
            self.adb_tools.pull_all_logs_in_thread(device,pattern)