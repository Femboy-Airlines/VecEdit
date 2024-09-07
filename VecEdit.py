import sys
import json
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtUiTools import *
from PySide6.QtCore import *
import os
import shutil
import gzip
import platform
import reference as ref # separate reference file for a cleaner main file

if os.path.exists("./ve_log.log"):
	os.remove("./ve_log.log")
def log_to_file(text):
	with open("./ve_log.log", "a") as file:
		file.write(f"{text}\n")

json_data = {}

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
		self.ui.RemoveBuildingsButton.clicked.connect(self.remove_enemy_buildings)
		self.ui.UnlockResearchButton.clicked.connect(self.unlock_all_research)
		self.ui.RemoveDecryptorsButton.clicked.connect(self.remove_all_decryptors)

		self.ui.mapTable.verticalHeader().setVisible(False)
		self.ui.mapTable.horizontalHeader().setVisible(False)

		self.cell_size = 30
		self.update_cell_size()

		# Zoom in and zoom out shortcuts
		self.zoom_in_shortcut = QShortcut(QKeySequence("Ctrl+="), self)
		self.zoom_in_shortcut.activated.connect(self.zoom_in)
		self.zoom_in_shortcut.setEnabled(False)
		self.zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
		self.zoom_out_shortcut.activated.connect(self.zoom_out)
		self.zoom_out_shortcut.setEnabled(False)

		self.ui.mapTable.cellClicked.connect(self.cell_was_clicked)

		self.ui.Tabs.currentChanged.connect(self.on_tab_changed)

		self.ui.updateSimpleButton.clicked.connect(self.update_json_simple)
		self.ui.updateMapButton.clicked.connect(self.update_json_map)
		self.ui.updateManualButton.clicked.connect(self.update_json_manual)
		self.ui.reloadButton.clicked.connect(self.reload_editors)
	
		self.map_update_shortcut = QShortcut(QKeySequence(Qt.CTRL | Qt.Key_Return), self)
		self.map_update_shortcut.activated.connect(self.update_map_tile)
		self.map_update_shortcut.setEnabled(False)

		self.ui.input1.setVisible(False)
		self.ui.input2.setVisible(False)
		self.ui.input3.setVisible(False)
		self.ui.input4.setVisible(False)
		self.ui.input5.setVisible(False)

	def toggle_stylesheet(self, state):
		if state == 2:
			print("Dark mode enabled")
			app.setStyleSheet(ref.dark_stylesheet)
		else:
			print("Dark mode disabled")
			app.setStyleSheet(ref.light_stylesheet)

	def load_json_data(self):
		self.ui.statusLabel.setText("Status: Loading file...")
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

			print("Populating simple view...")
			self.populate_simple_view()
			print("Simple view populated. Processing entities...")
			self.process_entities()
			print("Entities processed. Populating map view...")
			self.populate_map_table()
			print("Map view populated. Populating tree view...")
			self.populate_tree_view()
			print("Tree view populated.")
			self.ui.statusLabel.setText("Status: File loaded.")

	def populate_simple_view(self):
		global json_data
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

		playtime_float = float(json_data['WorldTime'])
		print(f"Float is set. | {playtime_float}")
		self.ui.PlaytimeInput.setValue(playtime_float)

		seed_int = int(json_data['Seed'])
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

	def process_entities(self):
		global resources
		resources = {}
		for resource in json_data["regions"]["region_the_abyss"]["resources"]:
			for tile in json_data["regions"]["region_the_abyss"]["resources"][resource]:
				resources[f"{tile['X']},{tile['Y']}"] = resource
		resources = dict(sorted(resources.items()))

		global buildings
		buildings = {}
		for entity in (entity for entity in json_data["regions"]["region_the_abyss"]["entities"] if entity not in ref.unit_list and entity not in ["vec_cargo_drone", "vec_builder_drone", "vec_courier_drone", "vec_fabricator_drone", "vec_dark_builder_drone", "vec_bullet"]):
			for tile in json_data["regions"]["region_the_abyss"]["entities"][entity]:
				if float(tile["PosX"])//5 <= 0.0 or float(tile["PosY"])//5 <= 0.0:
					continue
				buildings[f"{int(float(tile["PosX"])//5)},{int(float(tile["PosY"])//5)}"] = tile
		buildings = dict(sorted(buildings.items()))

		# Get dir of script
		script_dir = os.path.dirname(os.path.abspath(__file__))

		# List of resources we have an image for
		resource_image_list = ["resource_gold", "resource_crystallite", "resource_essence", "resource_iridium", "resource_lumina", "resource_nitrium", "resource_celite", "resource_osmium", "resource_gilded_crystal", "resource_ether_shard", "resource_arcana_steel", "resource_voidstone", "resource_phantomite", "resource_dark_gold", "resource_alcheminium", "resource_abyssminite"]
		global resource_images
		resource_images = {}
		for resource in resource_image_list:
			resource_images[resource] = QPixmap(script_dir + "/Images/" + resource + ".png")
		
		# List of buildings we have an image for
		building_image_list = ["vec_barrier", "vec_basic_core", "vec_ranger", "vec_reclaimer", "vec_repeater", "vec_resource_port", "vec_shotgunner", "vec_sprayer", "vec_wall"]
		global building_images
		building_images = {}
		for building in building_image_list:
			building_images[building] = QPixmap(script_dir + "/Images/" + building + ".png")
		log_to_file(building_images)

	def populate_map_table(self):
		self.ui.mapTable.setRowCount(480)
		self.ui.mapTable.setColumnCount(480)

		global resource_images
		global resources
		for tile in resources:
			x = int(tile.split(",")[0])
			y = int(tile.split(",")[1])
			item = QTableWidgetItem()
			try:
				icon = QIcon(resource_images[resources[tile]])
				item.setIcon(icon)
				item.setTextAlignment(Qt.AlignLeft)
				if icon.isNull():
					print(resources[tile])
					print("Icon is null")
			except KeyError:
				pass
			item.setText(resources[tile][9:])
			self.ui.mapTable.setItem(y, x, item)

		global building_images
		global buildings
		for tile in buildings:
			x = int(float(tile.split(",")[0]))
			y = int(float(tile.split(",")[1]))
			item = QTableWidgetItem()
			building_id = buildings[tile]["EntityID"]
			try:
				icon = QIcon(building_images[building_id])
				item.setIcon(icon)
				item.setTextAlignment(Qt.AlignLeft)
				if icon.isNull():
					print(buildings[tile])
					print("Icon is null")
			except KeyError:
				pass
			item.setText(building_id[4:])
			self.ui.mapTable.setItem(y, x, item)

	def populate_tree_view(self):
		model = QStandardItemModel()
		model.setHorizontalHeaderLabels(['Key', 'Value'])

		def add_items(parent, elements):
			stack = [(parent, elements)]
			while stack:
				parent, ellements = stack.pop()
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

		self.ui.JsonTree.setColumnWidth(0, 200)
		self.ui.JsonTree.setColumnWidth(1, 500)

	def remove_enemy_units(self):
		print("Removing enemy units...")
		for unit in ref.unit_list:
			if unit in json_data['regions']['region_the_abyss']['entities']:
				json_data['regions']['region_the_abyss']['entities'][unit] = [unit for unit in json_data['regions']['region_the_abyss']['entities'][unit] if unit.get("FactionID") != "faction_redscar"]
			if 'region_phantom_plains' in json_data['regions']:
				if unit in json_data['regions']['region_phantom_plains']['entities']:
					json_data['regions']['region_phantom_plains']['entities'][unit] = [unit for unit in json_data['regions']['region_phantom_plains']['entities'][unit] if unit.get("FactionID") != "faction_redscar"]
		print("Enemy units removed.")

	def remove_enemy_buildings(self):
		print("Removing enemy buildings...")
		for building in ref.building_list:
			if building in json_data['regions']['region_the_abyss']['entities']:
				json_data['regions']['region_the_abyss']['entities'][building] = [building for building in json_data['regions']['region_the_abyss']['entities'][building] if building.get("FactionID") != "faction_redscar"]
			# if 'region_phantom_plains' in json_data['regions']:
			# 	if building in json_data['regions']['region_phantom_plains']['entities']:
			# 		json_data['regions']['region_phantom_plains']['entities'][building] = []
		print("Enemy buildings removed.")

	def unlock_all_research(self):
		print("Unlocking all research...")
		json_data['researchTechResources'] = []
		json_data['completedResearchTechs'] = ref.all_techs
		print("All research unlocked.")

	def remove_all_decryptors(self):
		print("Removing all decryptors...")
		if "vec_decryptor" in json_data['regions']['region_the_abyss']['worldFeatures']:
			json_data['regions']['region_the_abyss']['worldFeatures']['vec_decryptor'] = []
		if 'region_phantom_plains' in json_data['regions']:
			if 'vec_decryptor' in json_data['regions']['region_phantom_plains']['worldFeatures']:
				json_data['regions']['region_phantom_plains']['worldFeatures']['vec_decryptor'] = []
		print("All decryptors removed.")

	def check_components(self, components, key, value):
		for index, component in enumerate(components):
			if component.get(key) == value:
				return index
		return -1

	def cell_was_clicked(self, column, row):
		global resources
		self.ui.coordsDisplay.setText(f"{row},{column}")
		try:
			self.ui.resourceInput.setText(" ".join(resources[f"{row},{column}"].split("_")[1:]).title())
		except KeyError:
			self.ui.resourceInput.setText("No resource selected")

		global buildings
		try:
			building = buildings[f"{row},{column}"]
			self.ui.buildingLabel.setText("Buliding: " + " ".join(building["EntityID"].split("_")[1:]).title())
			self.ui.factionInput.setText(building["FactionID"].split("_")[1].capitalize())
			self.ui.healthInput.setValue(0)
		except KeyError:
			self.ui.buildingLabel.setText("Building: No building selected")
			self.ui.factionInput.setText("")
			self.ui.healthInput.setValue(0)
		
		# TODO: Add some coments and make it look better since this is a mess
		info = {}
		if 'building' in locals() and building is not None and building.get("Components"):
			if self.check_components(building["Components"], "Type", "ResourceModule") != -1:
				i = self.check_components(building["Components"], "Type", "ResourceModule")
				if building["Components"][i]["HasInputStorage"]:
					inputStorage = building["Components"][i]["InputStorage"]
					info["Input Storage:"] = str(inputStorage[0].get("Amount")) + " " + " ".join(inputStorage[0].get("ID").split("_")[1:]).title()
				if building["Components"][i]["HasOutputStorage"]:
					outputStorage = building["Components"][i]["OutputStorage"]
					info["Output Storage:"] = str(outputStorage[0].get("Amount")) + " " + " ".join(outputStorage[0].get("ID").split("_")[1:]).title()
			if self.check_components(building["Components"], "Type", "Turret") != -1:
				i = self.check_components(building["Components"], "Type", "ResourceModule")
				info["Barrel Rotation:"] = str(building["Components"][i].get("BarrelRotation"))
				info["Cooldown:"] = str(building["Components"][i].get("Cooldown"))
				targetModes = {0: "Default", 1: "Closest", 2: "Strongest", 3: "Weakest"}
				targetMode = targetModes.get(building["Components"][i].get("TargetMode"))
				info["Target Mode:"] = str(targetMode)
			if self.check_components(building["Components"], "Type", "Decryptor") != -1:
				i = self.check_components(building["Components"], "Type", "Decryptor")
				info["Tech:"] = " ".join(building["Components"][i].get("TechID").split("_")[1:]).title()

		for i in range(5):
			label = getattr(self.ui, f"label{i+1}")
			label.setText("")
			input = getattr(self.ui, f"input{i+1}")
			input.setVisible(False)

		if len(info) != 0:
			for index, key in enumerate(info):
				label = getattr(self.ui, f"label{index+1}")
				label.setText(key)
				input = getattr(self.ui, f"input{index+1}")
				input.setVisible(True)
				input.setText(info[key])

	def update_map_tile(self):
		global resources
		global buildings
		if self.ui.coordsDisplay.text() == "No tile selected":
			return
		
		# Get x and y of current cell
		x = int(self.ui.coordsDisplay.text().split(",")[0])
		y = int(self.ui.coordsDisplay.text().split(",")[1])
		# Print for debugging
		print(f"Updating tile {x},{y}")

		# Update tile resource
		resource_name = self.ui.resourceInput.toPlainText().title()
		print(f"Resource: {resource_name}")

		# If not showing "No resource selected" and resource is valid, update resource list
		resource = "resource_" + resource_name.lower().replace(" ", "_")
		if self.ui.resourceInput.toPlainText() != "No resource selected" and (resource in ref.resource_list or resource_name == ""):
			if self.ui.resourceInput.toPlainText() == "":
				resources.pop(f"{x},{y}", None)
				self.ui.mapTable.setItem(y, x, None)
			else:
				resources[f"{x},{y}"] = resource
		
			# Write new resource to current cell
			global resource_images
			item = QTableWidgetItem()
			try:
				icon = QIcon(resource_images[resources[f"{x},{y}"]])
				item.setIcon(icon)
				item.setTextAlignment(Qt.AlignLeft)
				if icon.isNull():
					print(resources[f"{x},{y}"])
					print("Icon is null")
				self.ui.mapTable.setItem(y, x, item)
			except KeyError:
				item.setText(resource_name.lower())
				self.ui.mapTable.setItem(y, x, item)
		else:
			print("Resource not valid")

		info = {}
		building = buildings[f"{x},{y}"]

		# Update faction
		faction = self.ui.factionInput.toPlainText().lower()
		if faction in ["redscar", "player"]:
			faction = "faction_" + faction
		elif faction in ["faction_redscar", "faction_player"]:
			faction = faction
		else:
			faction = "faction_player"
		building["FactionID"] = faction
		
		# TODO: Once health gets stored in save file, add some code for it. Should be pretty simple

		# Get all attributes
		for i in range(5):
			label = getattr(self.ui, f"label{i+1}")
			input = getattr(self.ui, f"input{i+1}")
			if input.isVisible():
				key = label.text().replace(" ", "").replace(":", "")
				value = input.toPlainText()
				info[key] = value
		
		for key in info:
			value = info[key]
			if key in ["InputStorage", "OutputStorage"]:
				i = self.check_components(building["Components"], "Type", "ResourceModule")
				# Fallback in case they put no resource. Should probably change this, but it works for now (hopefully)
				if value == "":
					value = "0 Gold"
				value = [{"ID": "resource_" + value.split(" ")[1].lower(), "Amount": int(value.split(" ")[0])}]
			elif key in ["BarrelRotation", "Cooldown", "TargetMode"]:
				i = self.check_components(building["Components"], "Type", "Turret")
				if key in ["BarrelRotation", "Cooldown"]:
					value = float(value)
				elif key in ["TargetMode"]:
					targetModes = {'Default': 0, 'Closest': 1, 'Strongest': 2, 'Weakest': 3}
					value = targetModes.get(value)
					if value not in targetModes:
						value = 0
			building["Components"][i][key] = value

		self.cell_was_clicked(y, x)

	def update_json_simple(self):
		self.ui.statusLabel.setText("Status: Updating JSON from simple...")
		QApplication.processEvents()
		global json_data
		json_data['FileName'] = self.ui.FilenameInput.toPlainText()
		json_data['Name'] = self.ui.SavenameInput.toPlainText()
		json_data['Description'] = self.ui.DescriptionInput.toPlainText()
		json_data['Version'] = self.ui.VersionInput.toPlainText()
		json_data['WorldTime'] = float(self.ui.PlaytimeInput.value())
		json_data['Seed'] = int(self.ui.SeedInput.value())
		
		gamemode_index = self.ui.GamemodeInput.currentIndex()
		gamemode_string = self.ui.GamemodeInput.itemText(gamemode_index)
		json_data['GamemodeData']['ID'] = gamemode_string

		region_index = self.ui.RegionInput.currentIndex()
		region_string = self.ui.RegionInput.itemText(region_index)
		json_data['ActiveRegion'] = region_string
		self.ui.statusLabel.setText("Status: JSON updated from simple.")

	def update_json_map(self):
		self.ui.statusLabel.setText("Status: Updating JSON from map...")
		QApplication.processEvents()
		global json_data
		
		# For resources
		global resources
		json_data["regions"]["region_the_abyss"]["resources"] = {}
		for tile in resources:
			x = int(tile.split(",")[0])
			y = int(tile.split(",")[1])
			resource = resources[tile]
			if resource not in json_data["regions"]["region_the_abyss"]["resources"]:
				json_data["regions"]["region_the_abyss"]["resources"][resource] = []
			json_data["regions"]["region_the_abyss"]["resources"][resource].append({"X": x, "Y": y})
		
		# For buildings
		global buildings
		for tile in buildings:
			x = int(tile.split(",")[0])
			y = int(tile.split(",")[1])
			building = buildings[tile]["EntityID"]
			if building not in json_data["regions"]["region_the_abyss"]["entities"]:
				json_data["regions"]["region_the_abyss"]["entitiies"][resource] = []
			for thing in json_data["regions"]["region_the_abyss"]["entities"][building]:
				if thing["PosX"] == x and thing["PosY"] == y:
					thing = tile

		self.ui.statusLabel.setText("Status: JSON updated from map.")

	def update_json_manual(self):
		self.ui.statusLabel.setText("Status: Updating JSON from manual...")
		QApplication.processEvents()
		model = self.ui.JsonTree.model()
		root_item = model.invisibleRootItem()

		def tree_to_dict(item):
			data = {}
			for row in range(item.rowCount()):
				key_item = item.child(row, 0)
				value_item = item.child(row, 1)
				key = key_item.text()
				if key_item.hasChildren():
					if key_item.child(0).text().startswith("["):  # List detected
						data[key] = tree_to_list(key_item)
					else:  # Dict detected
						data[key] = tree_to_dict(key_item)
				else:
					data[key] = value_item.text()
			return data

		def tree_to_list(item):
			data = []
			for row in range(item.rowCount()):
				child_item = item.child(row, 0)
				if child_item.hasChildren():
					if child_item.child(0).text().startswith("["):  # Nested list
						data.append(tree_to_list(child_item))
					else:  # Nested dict
						data.append(tree_to_dict(child_item))
				else:
					data.append(child_item.text())
			return data

		global json_data
		json_data = tree_to_dict(root_item)
		self.ui.statusLabel.setText("Status: JSON updated from manual.")

	def reload_editors(self):
		self.ui.statusLabel.setText("Status: Reloading editors...")
		QApplication.processEvents()
		print("Populating simple view...")
		self.populate_simple_view()
		print("Simple view populated. Processing entities...")
		self.process_entities()
		print("Entities processed. Populating map view...")
		self.populate_map_table()
		print("Map view populated. Populating tree view...")
		self.populate_tree_view()
		print("Tree view populated.")
		self.ui.statusLabel.setText("Status: Editors reloaded.")

	def export_json_data(self):
		global json_data
		print("Outputing file...")
		file_dialog = QFileDialog(self)
		file_path, _ = file_dialog.getSaveFileName(self, "Save JSON File", self.ui.FilenameInput.toPlainText(), "SAV Files (*.sav)")
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
		print("File saved as " + file_path)

	def update_cell_size(self):
		self.ui.mapTable.verticalHeader().setDefaultSectionSize(self.cell_size)
		self.ui.mapTable.horizontalHeader().setDefaultSectionSize(self.cell_size)
		self.ui.mapTable.setIconSize(QSize(self.cell_size, self.cell_size))
		print("Cell size: " + str(self.cell_size))

	def on_tab_changed(self, index):
		# Enable shortcuts only if the current tab is the second tab
		if self.ui.Tabs.currentWidget() == self.ui.MapTab:
			self.zoom_in_shortcut.setEnabled(True)
			self.zoom_out_shortcut.setEnabled(True)
			self.map_update_shortcut.setEnabled(True)
		else:
			self.zoom_in_shortcut.setEnabled(False)
			self.zoom_out_shortcut.setEnabled(False)
			self.map_update_shortcut.setEnabled(False)

	def zoom_in(self):
		print("Zooming in")
		self.cell_size += 5
		self.update_cell_size()

	def zoom_out(self):
		if self.cell_size > 10:
			print("Zooming out")
			self.cell_size -= 5
			self.update_cell_size()

if __name__ == "__main__":
	loader = QUiLoader()
	app = QApplication(sys.argv)
	window = MainWindow()
	if detect_dark_mode():
		app.setStyleSheet(ref.dark_stylesheet)
	else:
		app.setStyleSheet(ref.light_stylesheet)
	window.show()
	sys.exit(app.exec())
