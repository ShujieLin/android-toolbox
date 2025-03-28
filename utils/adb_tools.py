import subprocess
import logging
import threading

# 为 ADBTools 类创建独立的日志记录器
logger = logging.getLogger('ADBTools')

# 数据层 (ADBTools)：专注ADB命令执行
class ADBTools:
    def __init__(self):
        self.selected_device = None
        self.current_path = "/"

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

    
    # 用于执行adb shell命令
    def execute_adb_shell_command_with_run(device, command):
        """
        Execute an ADB shell command on a specific device using subprocess.run.

        :param device: The device ID to execute the command on.
        :param command: The ADB shell command to execute.
        :return: The completed process object or None if an error occurs.
        """
        try:
            logging.info(f"Executing ADB shell command: {command} on device {device}")
            adb_cmd = ['adb', '-s', device, 'shell', command]
            result = subprocess.run(adb_cmd, text=True, capture_output=True, check=True)
            logging.info(f"Command output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while executing shell command: {e}")
            return None
        
    def change_directory_to_log(self, device,target_dir='sdcard/pudu/log'):
        """
        Change the current directory to sdcard/pudu/log on a specific device.

        :param device: The device ID to execute the command on.
        :return: The completed process object or None if an error occurs.
        """
        try:
            logging.info(f"Changing directory to {target_dir} on device {device}")
            adb_cmd = ['adb', '-s', device, 'shell', 'cd {target_dir} && pwd']
            result = subprocess.run(adb_cmd, text=True, capture_output=True, check=True)
            logging.info(f"Command output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while changing directory: {e}")
            return None
        
    def execute_ls_command(self, device, directory='.'):
        """
        Execute the 'ls' command on a specific device in the specified directory.

        :param device: The device ID to execute the command on.
        :param directory: The directory to list files and directories, default is the current directory.
        :return: The completed process object or None if an error occurs.
        """
        try:
            logging.info(f"Executing 'ls' command in {directory} on device {device}")
            adb_cmd = ['adb', '-s', device, 'shell', 'ls', directory]
            result = subprocess.run(adb_cmd, text=True, capture_output=True, check=True)
            logging.info(f"Command output: {result.stdout}")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while executing 'ls' command: {e}")
            return None

    def list_files_in_log_dir(self, device, target_dir='sdcard/pudu/log'):
        """
        Execute 'cd' and 'ls' commands on a specific device, 
        and store the filenames listed by 'ls' in a list.

        :param device: The device ID to execute the command on.
        :param target_dir: The target directory to change to and list files, 
                          default is 'sdcard/pudu/log'.
        :return: A list of filenames or an empty list if an error occurs.
        """
        try:
            logging.info(f"Listing files in {target_dir} on device {device}")
            # 构建组合命令
            adb_cmd = ['adb', '-s', device, 'shell', f'cd {target_dir} && ls']
            result = subprocess.run(adb_cmd, text=True, capture_output=True, check=True)
            # 将输出按行分割并去除空白元素，得到文件名列表
            file_names = [line.strip() for line in result.stdout.splitlines() if line.strip()]
            # logging.info(f"Files in {target_dir}: {file_names}")
            return file_names
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while listing files in {target_dir}: {e}")
            return []

    def filter_logs_by_category(self,file_names):
          # 处理文件名，提取服务名
            log_categorys = []
            # 过滤file_names，只保留带有.pdlog后缀的文件
            file_names = [file_name for file_name in file_names if file_name.endswith('.pdlog')]

            for file_name in file_names:
                parts = file_name.split('.')
                if parts:
                    log_categorys.append(parts[0])
              # 过滤掉重复元素
            unique_log_categorys = list(set(log_categorys))
            logging.info(f"log categories: {unique_log_categorys}")
            return unique_log_categorys                                     

    def get_log_categorys(self,device):
        file_names = self.list_files_in_log_dir(device)
        return self.filter_logs_by_category(file_names)
    

    def set_selected_log_categorys(self,selected_items):
        self.selected_log_categorys = selected_items
        logging.info(f"Selected log categories: {self.selected_log_categorys}")


    def pull_one_type_one_day_logs(self, device, log_type, date):
        """Pull logs of one type for one day from device"""
        try:
            logging.info(f"Pulling logs for {device}")

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


    def pull_all_logs_for_selected_items(self):
        """Pull all logs for selected items"""
        if not self.selected_log_categorys:
            logging.info("No log categories selected")
            return

        devices = self.get_connected_devices()
        if not devices:
            logging.error("No connected devices found.")
            return

        device = devices[0]  # 选择第一个连接的设备
        log_dir = "/sdcard/pudu/log"

        for log_type in self.selected_log_categorys:
            try:
                # 构建日志文件的通配符模式
                log_pattern = f"{log_dir}/{log_type}.g3log.*.pdlog"
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
                logging.info(f"Successfully pulled logs for {log_type}")
            except subprocess.CalledProcessError as e:
                logging.error(f"ADB error while pulling {log_type} logs: {e}")


    def pull_all_logs_in_thread(self, device, pattern):
        """在子线程中执行 pull_all_logs_for_selected_items 方法"""
        thread = threading.Thread(target=self.pull_logs_by_pattern, kwargs={'device': device, 'pattern': pattern})
        thread.start()


    def pull_logs_by_pattern(self, device, pattern):
        """
        根据指定的文件模式从设备中拉取日志文件到当前目录。

        :param device: 要执行命令的设备 ID
        :param pattern: 日志文件的通配符模式，例如 '/sdcard/pudu/log/SpeechService.g3log.20241202*'
        """
        try:
            logging.info(f"Pulling logs matching pattern: {pattern}")
            # 获取通过正则表达式过滤出来的日志文件
            list_cmd = ['adb', '-s', device, 'shell', 'ls', pattern]
            # 执行查找命令并获取输出
            list_result = subprocess.check_output(list_cmd, text=True)
            # 遍历找到的每个日志文件
            for log_file in list_result.splitlines():
                log_file = log_file.strip()
                if log_file:
                    # 构建拉取文件的 ADB 命令
                    pull_cmd = ['adb', '-s', device, 'pull', log_file, self.selected_windows_path]
                    logging.info(f"Pulling file: {log_file}")
                    # 执行拉取命令
                    subprocess.check_output(pull_cmd)
            logging.info(f"Successfully pulled logs matching pattern: {pattern}")
        except subprocess.CalledProcessError as e:
            logging.error(f"ADB error while pulling logs matching pattern {pattern}: {e}")

    def set_selected_windows_path(self, path):
        self.selected_windows_path = path
        logging.info(f"Selected Windows path: {self.selected_windows_path}")