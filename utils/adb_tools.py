import subprocess
import logging
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

    def select_device_path(self, path):
        """Set working path on device"""
        self.current_path = path
        logging.info(f"Selected path: {path}")

    def list_device_files(self):
        """List files at current path on selected device"""
        if not self.selected_device:
            logging.error("No device selected")
            return []
            
        try:
            cmd = ['adb', '-s', self.selected_device, 'shell', 'ls', self.current_path]
            result = subprocess.check_output(cmd, text=True)
            return result.splitlines()
        except subprocess.CalledProcessError as e:
            logging.error(f"File list error: {e}")
            return []
