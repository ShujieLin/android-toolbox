import subprocess
import logging
# 数据层 (ADBTools)：专注ADB命令执行
class ADBTools:
    def __init__(self):
        self.selected_device = None
        self.current_path = "/"

    def pull_one_type_one_day_logs(self, device, log_type, date):
        """Pull logs of one type for one day from device"""
        try:
            logging.info(f"Pulling logs for {device} on {date}")

            # 构建日志文件的通配符模式
            log_pattern = f"/sdcard/pudu/log/{log_type}.g3log.{date}*"
            # 构建用于查找日志文件的 ADB 命令
            list_cmd = ['adb', '-s', device, 'shell', 'ls', log_pattern]
            # 执行查找命令并获取输出
            list_result = subprocess.check_output(list_cmd, text=True)
            # 遍历找到的每个日志文件
            for log_file in list_result.splitlines():
                # 构建拉取文件的 ADB 命令
                pull_cmd = ['adb', '-s', device, 'pull', log_file, '.']
                # 执行拉取命令
                subprocess.check_output(pull_cmd)
            logging.info(f"Successfully pulled logs for {device} on {date}")
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while pulling logs: {e}")

    def get_connected_devices(self):
        logging.info("Getting connected devices")
        """Get list of connected ADB devices"""
        try:
            result = subprocess.check_output(['adb', 'devices'], text=True)
            logging.info(f"Connected devices: {result}")
            return [line.split('\t')[0] for line in result.splitlines()[1:] if 'device' in line]
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error: {e}")
            return []
