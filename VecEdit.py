import sys
import json
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTreeView, QInputDialog
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtUiTools import QUiLoader

json_data = {}

class MainWindow(QMainWindow):
	def __init__(self):
		super(MainWindow, self).__init__()
		loader = QUiLoader()
		self.ui = loader.load("main_window.ui", self)
		
		self.ui.import_button.clicked.connect(self.load_json_data)
		self.ui.export_button.clicked.connect(self.export_json_data)
		self.ui.JsonTree.doubleClicked.connect(self.edit_item)
		
		self.tree_model = QStandardItemModel()
		self.ui.JsonTree.setModel(self.tree_model)
		self.tree_model.setHorizontalHeaderLabels(['Key', 'Value'])

	def load_json_data(self):
		global json_data
		file_dialog = QFileDialog(self)
		file_path, _ = file_dialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")
		if file_path:
			with open(file_path, 'r') as file:
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
		file_path, _ = file_dialog.getSaveFileName(self, "Save JSON File", "", "JSON Files (*.json)")
		if file_path:
			with open(file_path, 'w') as file:
				json.dump(json_data, file, separators=(',', ':'))
				
if __name__ == "__main__":
	app = QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())
