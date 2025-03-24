import sys
import subprocess
from PyQt5.QtCore import Qt, QModelIndex, QAbstractItemModel
from PyQt5.QtWidgets import QApplication, QTreeView, QFileIconProvider

class AdbFileModel(QAbstractItemModel):
    def __init__(self, root_path="/", parent=None):
        super().__init__(parent)
        self.root_path = root_path
        self.icon_provider = QFileIconProvider()
        self._data = self.get_adb_files(root_path)

    def get_adb_files(self, path):
        try:
            result = subprocess.run(
                ["adb", "shell", f"ls -la {path}"],
                capture_output=True,
                text=True,
                check=True
            )
            return self.parse_ls_output(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"ADB Error: {e.stderr}")
            return []

    def parse_ls_output(self, output):
        entries = []
        for line in output.splitlines():
            if line.startswith('total'):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            entry = {
                'permissions': parts[0],
                'owner': parts[1],
                'group': parts[2],
                'size': parts[3],
                'date': ' '.join(parts[4:6]),
                'name': ' '.join(parts[6:]),
                'is_dir': parts[0].startswith('d')
            }
            entries.append(entry)
        return entries

    # 创建节点索引
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        return self.createIndex(row, column)

    def parent(self, index):
        return QModelIndex()

    # 返回子项数量
    def rowCount(self, parent=QModelIndex()):
        return len(self._data) if not parent.isValid() else 0

    # 定义列数
    def columnCount(self, parent=QModelIndex()):
        return 4  # 名称/类型/大小/修改时间

    # 提供显示数据
    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        item = self._data[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            return {
                0: item['name'],
                1: "目录" if item['is_dir'] else "文件",
                2: item['size'],
                3: item['date']
            }.get(col)

        if role == Qt.DecorationRole and col == 0:
            return self.icon_provider.icon(
                QFileIconProvider.Folder if item['is_dir'] 
                else QFileIconProvider.File
            )

        return None

class AdbExplorer(QTreeView):
    def __init__(self):
        super().__init__()
        self.setModel(AdbFileModel())
        self.doubleClicked.connect(self.navigate)
        # self.setHeaderLabels(["名称", "类型", "大小", "修改时间"])

    def navigate(self, index):
        item = self.model()._data[index.row()]
        if item['is_dir']:
            new_path = f"{self.model().root_path}/{item['name']}".replace('//', '/')
            self.setModel(AdbFileModel(new_path))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AdbExplorer()
    window.show()
    sys.exit(app.exec_())