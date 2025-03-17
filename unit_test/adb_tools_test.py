from utils.adb_tools import ADBTools
import logging
# Test when there are no connected devices
def test_get_connected_devices_no_devices(mocker):
    adb_tools = ADBTools()

    fake_output = "List of devices attached\n"
    mocker.patch('subprocess.check_output', return_value=fake_output)

    devices = adb_tools.get_connected_devices()
    assert devices == []

# Test when there are connected devices
def test_get_connected_devices_with_devices(mocker):
    adb_tools = ADBTools()

    # 模拟 adb devices 命令的预期输出，格式与真实输出一致
    # Mock the actual ADB command output
    fake_output = "List of devices attached\nemulator-5554\tdevice\nemulator-5556\tdevice\n"
    mocker.patch('subprocess.check_output', return_value=fake_output)
    
    # 预期该方法会执行 adb devices，解析输出并返回设备 ID 列表。
    devices = adb_tools.get_connected_devices()
    logging.info(f"devices: {devices}")
    assert devices == ['emulator-5554', 'emulator-5556']
