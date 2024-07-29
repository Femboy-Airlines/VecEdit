import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeView, QInputDialog, QPushButton, QGridLayout
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader
import os
import shutil
import gzip
import platform

json_data = {}
light_stylesheet = """
	QWidget {
		background-color: white;
		color: black;
	}
	QPushButton {
		background-color: lightgray;
		color: black;
	}
"""

dark_stylesheet = """
	QWidget {
		background-color: #2d2d2d;
		color: white;
	}
	QPushButton {
		background-color: #3d3d3d;
		color: white;
	}
"""
def detect_darkmode_in_windows(): 
	try:
		import winreg
	except ImportError:
		return False
	registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
	reg_keypath = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
	try:
		reg_key = winreg.OpenKey(registry, reg_keypath)
	except FileNotFoundError:
		return False

	for i in range(1024):
		try:
			value_name, value, _ = winreg.EnumValue(reg_key, i)
			if value_name == 'AppsUseLightTheme':
				return value == 0
		except OSError:
			break
	return False

def detect_dark_mode():
	if platform.system() == 'Linux':
		try:
			import subprocess
			dark_mode = subprocess.check_output(
				'gsettings get org.gnome.desktop.interface gtk-theme', shell=True).decode().strip()
			return 'dark' in dark_mode.lower()
		except:
			pass
	elif platform.system() == 'Windows':
		return detect_darkmode_in_windows()

	elif platform.system() == 'Darwin':
		try:
			import subprocess
			dark_mode = subprocess.check_output(
				'ddefaults read -g AppleInterfaceStyle', shell=True).decode().strip()
			return 'dark' in dark_mode.lower()
		except:
			pass
	return False


def resource_path(relative_path):
	""" Get the absolute path to the resource, works for dev and for PyInstaller """
	try:
		# PyInstaller creates a temp folder and stores path in _MEIPASS
		base_path = sys._MEIPASS
	except Exception:
		base_path = os.path.abspath(".")

	return os.path.join(base_path, relative_path)

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		loader = QUiLoader()
		ui_file_path = resource_path('main_window.ui')
		self.ui = loader.load(ui_file_path, self)
		
		self.ui.import_button.clicked.connect(self.load_json_data)
		self.ui.export_button.clicked.connect(self.export_json_data)
		self.ui.JsonTree.doubleClicked.connect(self.edit_item)
		
		self.tree_model = QStandardItemModel()
		self.ui.JsonTree.setModel(self.tree_model)
		self.tree_model.setHorizontalHeaderLabels(['Key', 'Value'])

	def load_json_data(self):
		global json_data
		file_dialog = QFileDialog(self)
		file_path, _ = file_dialog.getOpenFileName(self, "Open SAV File", "", "SAV Files (*.sav)")
		if file_path:
			temp_folder = "./vecedit_temp"
			#create temp folder
			if not os.path.exists(temp_folder):
				os.makedirs(temp_folder)
			
			#create temporary gzip file path
			#vecedit_temp/example----.gz
			temp_gz_path = os.path.join(temp_folder, os.path.basename(file_path)[:-4] + '.gz')
			print(f"gzpath is {temp_gz_path}")

			#Copy main file as gz to temp
			#vecedit_temp/example.gz from vec/saves/world_1.sav for example
			shutil.copyfile(file_path, temp_gz_path)

			#We want the JS to be the same name without the gz extension, so this strips the last 3 characters
			#vecedit_temp/example
			temp_json_path = temp_gz_path[:-3]
			print(f"Json path is {temp_json_path}")
			with gzip.open(temp_gz_path, 'rb') as file_in:
				shutil.copyfileobj(file_in, open(temp_json_path, "wb"))
			
			with open(temp_json_path, 'r') as file:
				json_data = json.load(file)
				self.populate_tree_view(json_data)

	def populate_tree_view(self, json_data, parent=None):
		if parent is None:
			self.tree_model.clear()
			self.tree_model.setHorizontalHeaderLabels(['Key', 'Value'])
			parent = self.tree_model.invisibleRootItem()

		for key, value in json_data.items():
			key_item = QStandardItem(key)
			if isinstance(value, dict):
				value_item = QStandardItem('[Object]')
				parent.appendRow([key_item, value_item])
				self.populate_tree_view(value, key_item)
			elif isinstance(value, list):
				value_item = QStandardItem('[Array]')
				parent.appendRow([key_item, value_item])
				self.populate_tree_view_list(value, key_item)
			else:
				match value:
					case str():
						value_item = QStandardItem(f'[String] {value}')

					case bool():
						value_item = QStandardItem(f'[Boolean] {value}')

					case int():
						value_item = QStandardItem(f'[Integer] {value}')

					case float():
						value_item = QStandardItem(f'[Float] {value}')

					case None:
						value_item = QStandardItem('[NoneType] None')

					case _:
						print(type(value))
						value_item = QStandardItem(str(value))

				parent.appendRow([key_item, value_item])

	def populate_tree_view_list(self, value_list, parent):
		for i, value in enumerate(value_list):
			index_item = QStandardItem(f'[{i}]')
			if isinstance(value, dict):
				value_item = QStandardItem('[Object]')
				parent.appendRow([index_item, value_item])
				self.populate_tree_view(value, index_item)
			elif isinstance(value, list):
				value_item = QStandardItem('[Array]')
				parent.appendRow([index_item, value_item])
				self.populate_tree_view_list(value, index_item)
			else:
				value_item = QStandardItem(str(value))
				parent.appendRow([index_item, value_item])

	def edit_item(self, index):
		item = self.tree_model.itemFromIndex(index)
		if item:
			new_value, ok = QInputDialog.getText(self, "Edit Value", "Enter new value:", text=item.text())
			if ok:
				item.setText(new_value)
				self.update_json_data()

	def update_json_data(self, parent=None, json_obj=None):
		if parent is None:
			parent = self.tree_model.invisibleRootItem()
			json_obj = json_data
		for row in range(parent.rowCount()):
			key_item = parent.child(row, 0)
			value_item = parent.child(row, 1)
			key = key_item.text()
			value = value_item.text()
			print(key, value)
			if value == '[Object]':
				json_obj[key] = {}	
				self.update_json_data(key_item, json_obj[key])
			elif value == '[Array]':
				json_obj[key] = []
				self.update_json_data_list(key_item, json_obj[key])

			elif value.startswith('[Integer]'):
				json_obj[key] = int(value.split(' ', 1)[1])

			elif value.startswith('[Boolean]'):
				json_obj[key] = value.split(' ', 1)[1] == 'True'

			elif value.startswith('[Float]'):
				json_obj[key] = float(value.split(' ', 1)[1])

			elif value.startswith('[String]'):
				json_obj[key] = str(value.split(' ', 1)[1])
				
			elif value == '[NoneType] None':
				json_obj[key] = None

			else:
				json_obj[key] = value

	def update_json_data_list(self, parent, json_list):
		for row in range(parent.rowCount()):
			index_item = parent.child(row, 0)
			value_item = parent.child(row, 1)
			index = int(index_item.text().strip('[]'))
			value = value_item.text()
			if value == '[Object]':
				json_list.append({})
				self.update_json_data(index_item, json_list[index])
			elif value == '[Array]':
				json_list.append([])
				self.update_json_data_list(index_item, json_list[index])
			elif value.startswith('[Integer]'):
				json_list.append(int(value.split(' ', 1)[1]))
			elif value.startswith('[Boolean]'):
				json_list.append(value.split(' ', 1)[1] == 'True')
			elif value.startswith('[Float]'):
				json_list.append(float(value.split(' ', 1)[1]))
			elif value == '[NoneType] None':
				json_list.append(None)
			else:
				json_list.append(value)

	def export_json_data(self):
		global json_data
		self.update_json_data()
		file_dialog = QFileDialog(self)
		file_path, _ = file_dialog.getSaveFileName(self, "Save JSON File", "", "SAV Files (*.sav)")
		if file_path:
			temp_folder = "vecedit_temp"
			if not os.path.exists(temp_folder):
				os.makedirs(temp_folder)
			
			temp_json_path = os.path.join(temp_folder, os.path.basename(file_path))
			with open(temp_json_path, 'w') as file:
				json.dump(json_data, file, indent=4)
			
			temp_gz_path = temp_json_path + '.gz'
			with open(temp_json_path, 'rb') as file_in:
				with gzip.open(temp_gz_path, 'wb') as file_out:
					shutil.copyfileobj(file_in, file_out)
			
			with open(temp_gz_path, 'rb') as file_in:
				with open(file_path, 'wb') as file_out:
					shutil.copyfileobj(file_in, file_out)

			shutil.rmtree(temp_folder)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	if detect_dark_mode():
		app.setStyleSheet(dark_stylesheet)
	else:
		app.setStyleSheet(light_stylesheet)
	window.show()
	sys.exit(app.exec())
