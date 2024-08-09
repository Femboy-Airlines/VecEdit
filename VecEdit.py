import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtUiTools import *
import os
import shutil
import gzip
import platform

if os.path.exists("./ve_log.log"):
	os.remove("./ve_log.log")
def log_to_file(text):
	with open("./ve_log.log", "a") as file:
		file.write(f"{text}\n")

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
	QTabWidget::pane {
		border: 1px solid lightgray;
	}
	QTabBar::tab {
		background: lightgray;
		color: black;
		padding: 5px;
	}
	QTabBar::tab:selected {
		background: white;
		border: 1px solid lightgray;
		border-bottom-color: white;
	}
	QTreeView {
		background-color: white;
		color: black;
	}
	QTreeView::item:selected {
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
	QTabWidget::pane {
		border: 1px solid #3d3d3d;
	}
	QTabBar::tab {
		background: #3d3d3d;
		color: white;
		padding: 5px;
	}
	QTabBar::tab:selected {
		background: #2d2d2d;
		border: 1px solid #3d3d3d;
		border-bottom-color: #2d2d2d;
	}
	QTreeView {
		background-color: #2d2d2d;
		color: white;
	}
	QTreeView::item:selected {
		background-color: #3d3d3d;
		color: white;
	}
	QHeaderView::section {
		background-color: #3d3d3d;
		color: white;
		padding: 4px;
		border: 1px solid #3d3d3d;
	}
"""

def detect_darkmode_in_windows():
	log_to_file("Other function called.")
	try:
		import winreg
	except ImportError:
		return False
	log_to_file("Winreg works")
	registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
	reg_keypath = r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize'
	try:
		reg_key = winreg.OpenKey(registry, reg_keypath)
	except FileNotFoundError:
		return False
	log_to_file("Key imported")

	for i in range(1024):
		try:
			value_name, value, _ = winreg.EnumValue(reg_key, i)
			if value_name == 'AppsUseLightTheme':
				log_to_file(f"Dark mode in Windows: {value == 0}")
				return value == 0
		except OSError:
			break

	log_to_file("Everything else broke.")
	return False

def detect_dark_mode():
	log_to_file("Detecting dark mode")
	if platform.system() == 'Linux':
		try:
			log_to_file("You are a Linux user.")
			import subprocess
			dark_mode = subprocess.check_output(
				'gsettings get org.gnome.desktop.interface gtk-theme', shell=True).decode().strip()
			log_to_file(f"Dark mode for Linux: {'dark' in dark_mode.lower()}")
			return 'dark' in dark_mode.lower()
		except:
			pass
	elif platform.system() == 'Windows':
		log_to_file("You're a windows person. Moving detection to other function")
		return detect_darkmode_in_windows()

	elif platform.system() == 'Darwin':
		log_to_file("ew macos")
		try:
			import subprocess
			dark_mode = subprocess.check_output(
				'ddefaults read -g AppleInterfaceStyle', shell=True).decode().strip()
			log_to_file(f"Dark mode for $$$: {'dark' in dark_mode.lower()}")
			return 'dark' in dark_mode.lower()
		except:
			pass

	log_to_file("You're not using Windows, MacOS, or Linux. Why? WHY?")
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

		ui_file_path = resource_path('main_window.ui')
		self.ui = loader.load(ui_file_path, self)

		self.ui.ImportButton.clicked.connect(self.load_json_data)
		self.ui.ExportButton.clicked.connect(self.export_json_data)

		# Connect the checkbox signal to the slot
		self.ui.checkBox.stateChanged.connect(self.toggle_stylesheet)
		
		# Ensure the checkbox is checked by default
		self.ui.checkBox.setChecked(True)

		self.ui.RemoveUnitsButton.clicked.connect(self.remove_enemy_units)
	
	def toggle_stylesheet(self, state):
		if state == 2:
			print("Dark mode enabled")
			app.setStyleSheet(dark_stylesheet)
		else:
			print("Dark mode disabled")
			app.setStyleSheet(light_stylesheet)

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

			#We want the JSON to be the same name without the gz extension, so this strips the last 3 characters
			#vecedit_temp/example
			temp_json_path = temp_gz_path[:-3]
			print(f"Json path is {temp_json_path}")
			with gzip.open(temp_gz_path, 'rb') as file_in:
				shutil.copyfileobj(file_in, open(temp_json_path, "wb"))
			
			with open(temp_json_path, 'r') as file:
				json_data = json.load(file)

			filename_string = json_data['FileName']
			print(f"String is set. | {filename_string}")
			self.ui.FilenameInput.setText(filename_string)

			savename_string = json_data['Name']
			print(f"String is set. | {savename_string}")
			self.ui.SavenameInput.setText(savename_string)

			description_string = json_data['Description']
			print(f"String is set. | {description_string}")
			self.ui.DescriptionInput.setText(description_string)

			version_string = json_data['Version']
			print(f"Float is set. | {version_string}")
			self.ui.VersionInput.setText(version_string)

			playtime_double = json_data['WorldTime']
			print(f"Float is set. | {playtime_double}")
			self.ui.PlaytimeInput.setValue(playtime_double)

			seed_int = json_data['Seed']
			print(f"Int is set. | {seed_int}")
			self.ui.SeedInput.setValue(seed_int)

			gamemode_data = json_data['GamemodeData']
			gamemode_string = gamemode_data["ID"]
			print(f"String is set. | {gamemode_string}")

			# Find the index of the gamemode_string
			gamemode_index = self.ui.GamemodeInput.findText(gamemode_string)
			if gamemode_index == -1:
				print(f"Error: gamemode_string '{gamemode_string}' not found in GamemodeInput.")
			else:
				self.ui.GamemodeInput.setCurrentIndex(gamemode_index)

			region_string = json_data['ActiveRegion']
			print(f"String is set. | {region_string}")

			# Find the index of the gamemode_string
			region_index = self.ui.RegionInput.findText(region_string)
			if region_index == -1:
				print(f"Error: region_string '{region_string}' not found in RegionInput.")
			else:
				self.ui.RegionInput.setCurrentIndex(region_index)

			print("Loading finished. Populating tree view.")

			self.populate_tree_view()

			print("Tree view populated.")

	def populate_tree_view(self):
		model = QStandardItemModel()
		model.setHorizontalHeaderLabels(['Key', 'Value'])

		def add_items(parent, elements):
			if isinstance(elements, dict):
				for key, value in elements.items():
					key_item = QStandardItem(key)
					if isinstance(value, (dict, list)):
						value_item = QStandardItem("")
						parent.appendRow([key_item, value_item])
						add_items(key_item, value)
					else:
						value_item = QStandardItem(str(value))
						parent.appendRow([key_item, value_item])
			elif isinstance(elements, list):
				for index, value in enumerate(elements):
					key_item = QStandardItem(f"[{index}]")
					if isinstance(value, (dict, list)):
						value_item = QStandardItem("")
						parent.appendRow([key_item, value_item])
						add_items(key_item, value)
					else:
						value_item = QStandardItem(str(value))
						parent.appendRow([key_item, value_item])

		root_item = model.invisibleRootItem()
		add_items(root_item, json_data)

		self.ui.JsonTree.setModel(model)

		self.ui.JsonTree.setColumnWidth(0, 175)

	def remove_enemy_units(self):
		enemy_list = ["vec_sawblade", "vec_triangle", "vec_fighter", "vec_bomber", "vec_carrier", "vec_hammerhead"]
		for enemy in enemy_list:
			if enemy in json_data['regions']['region_the_abyss']['entities']:
				json_data['regions']['region_the_abyss']['entities'][enemy] = []
			if 'region_phantom_plains' in json_data['regions']:
				if enemy in json_data['regions']['region_phantom_plains']['entities']:
					json_data['regions']['region_phantom_plains']['entities'][enemy] = []

	def update_json_data_from_inputs(self):
		global json_data
		json_data['FileName'] = self.ui.FilenameInput.toPlainText()
		json_data['Name'] = self.ui.SavenameInput.toPlainText()
		json_data['Description'] = self.ui.DescriptionInput.toPlainText()
		json_data['Version'] = self.ui.VersionInput.toPlainText()
		json_data['WorldTime'] = self.ui.PlaytimeInput.value()
		json_data['Seed'] = self.ui.SeedInput.value()
		
		gamemode_index = self.ui.GamemodeInput.currentIndex()
		gamemode_string = self.ui.GamemodeInput.itemText(gamemode_index)
		json_data['GamemodeData']['ID'] = gamemode_string

		region_index = self.ui.RegionInput.currentIndex()
		region_string = self.ui.RegionInput.itemText(region_index)
		json_data['ActiveRegion'] = region_string

	def export_json_data(self):
		global json_data
		self.update_json_data_from_inputs()
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
	loader = QUiLoader()
	app = QApplication(sys.argv)
	window = MainWindow()
	if detect_dark_mode():
		app.setStyleSheet(dark_stylesheet)
	else:
		app.setStyleSheet(light_stylesheet)
	window.show()
	sys.exit(app.exec())
