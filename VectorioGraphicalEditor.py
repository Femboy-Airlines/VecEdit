import json
import gzip
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import shutil

class CollapsibleMenu(tk.Frame):
	def __init__(self, master, title="", *args, **kwargs):
		tk.Frame.__init__(self, master, *args, **kwargs)
		self.title = tk.StringVar()
		self.title.set(title)
		self.show = tk.IntVar()
		self.show.set(0)

		self.title_frame = tk.Frame(self)
		self.title_frame.pack(fill="x", expand=1)

		self.label = tk.Label(self.title_frame, textvariable=self.title)
		self.label.pack(side="left", fill="x", expand=1)

		self.toggle_button = tk.Checkbutton(self.title_frame, width=2, text='+', command=self.toggle, variable=self.show)
		self.toggle_button.pack(side="left")

		self.sub_frame = tk.Frame(self, relief="sunken", borderwidth=1)

	def toggle(self):
		if bool(self.show.get()):
			self.sub_frame.pack(fill="x", expand=1)
			self.toggle_button.configure(text='-')
		else:
			self.sub_frame.forget()
			self.toggle_button.configure(text='+')

class vecedit:
	def __init__(self, master):
		self.master = master
		self.master.title("VecEdit")

		self.frame = tk.Frame(self.master)
		self.frame.pack(padx=10, pady=10)

		self.data = {}

		self.import_btn = tk.Button(self.frame, text="Import", command=self.import_file)
		self.import_btn.grid(row=0, column=0, padx=5, pady=5)

		self.export_btn = tk.Button(self.frame, text="Export", command=self.export_file)
		self.export_btn.grid(row=0, column=1, padx=5, pady=5)

		# Create a canvas with a scrollbar
		self.canvas = tk.Canvas(self.master)
		self.scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
		self.scrollable_frame = ttk.Frame(self.canvas)

		self.scrollable_frame.bind(
			"<Configure>",
			lambda e: self.canvas.configure(
				scrollregion=self.canvas.bbox("all")
			)
		)

		self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
		self.canvas.configure(yscrollcommand=self.scrollbar.set)

		self.canvas.pack(side="left", fill="both", expand=True)
		self.scrollbar.pack(side="right", fill="y")

	def import_file(self):
		file_path = filedialog.askopenfilename(filetypes=[("vectorio save files", "*.sav")])
		if file_path:
			if not os.path.exists("./temp/"):
				os.makedirs("./temp/")

			# we have to do this, because for whatever reason, gzip whines at files named "*.sav"
			# no clue why
			if file_path.endswith(".sav"):
				file_name = os.path.basename(file_path)
				temp_path = f"./temp/{file_name}"
				temp_path = f"{temp_path[:-4]}.gz"
				print(f"Temp path is {temp_path}")
				shutil.copyfile(file_path, temp_path)
				with gzip.open(temp_path, 'rb') as f:
					file_content = f.read()

			else:
				with gzip.open(file_path, 'rb') as f:
					file_content = f.read()

			self.data = json.loads(file_content)
			self.display_data()

	def export_file(self):
		self.save_data()
		if not self.data:
			messagebox.showerror("Error", "No data to export")
			return
		file_path = filedialog.asksaveasfilename(initialfile="", defaultextension=".sav", filetypes=[("vectorio save files", "*.sav")])
		if file_path:
			with gzip.open(file_path, 'wb') as f:
				f.write(json.dumps(self.data).encode('utf-8'))
			messagebox.showinfo("Success", "File exported successfully")

	def display_data(self):
		for widget in self.scrollable_frame.winfo_children():
			widget.destroy()

		self.entries = {}
		self.create_entries(self.data, self.scrollable_frame)

	def create_entries(self, data, parent):
		row = 0
		if isinstance(data, dict):
			for key, value in data.items():
				label = tk.Label(parent, text=key)
				label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
				if isinstance(value, dict):
					menu = CollapsibleMenu(parent, title=key)
					menu.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
					self.create_entries(value, menu.sub_frame)
				elif isinstance(value, list):
					menu = CollapsibleMenu(parent, title=key)
					menu.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
					self.create_entries(value, menu.sub_frame)
				else:
					self.create_entry(parent, row, key, value)
				row += 1
		elif isinstance(data, list):
			for index, value in enumerate(data):
				label = tk.Label(parent, text=f"[{index}]")
				label.grid(row=row, column=0, padx=5, pady=5, sticky='w')
				if isinstance(value, dict):
					menu = CollapsibleMenu(parent, title=f"[{index}]")
					menu.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
					self.create_entries(value, menu.sub_frame)
				elif isinstance(value, list):
					menu = CollapsibleMenu(parent, title=f"[{index}]")
					menu.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
					self.create_entries(value, menu.sub_frame)
				else:
					self.create_entry(parent, row, index, value)
				row += 1

	def create_entry(self, parent, row, key, value):
		# Depending on the type of value, create an appropriate widget
		if isinstance(value, str):
			entry = tk.Entry(parent)
			entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
			entry.insert(0, value)
			self.entries[key] = entry
		elif isinstance(value, int):
			entry = tk.Spinbox(parent, from_=-1000000, to=1000000)
			entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
			entry.insert(0, value)
			self.entries[key] = entry
		elif isinstance(value, float):
			entry = tk.Entry(parent)
			entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
			entry.insert(0, value)
			self.entries[key] = entry
		elif isinstance(value, bool):
			var = tk.BooleanVar(value=value)
			checkbutton = tk.Checkbutton(parent, variable=var)
			checkbutton.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
			self.entries[key] = var
		else:
			# Fallback for any other types
			entry = tk.Entry(parent)
			entry.grid(row=row, column=1, padx=5, pady=5, sticky='ew')
			entry.insert(0, str(value))
			self.entries[key] = entry

	def save_data(self):
		def update_data(entries, data):
			if isinstance(data, dict):
				for key, entry in entries.items():
					if isinstance(entry, dict):
						update_data(entry, data[key])
					else:
						data[key] = entry.get()
			elif isinstance(data, list):
				for index, entry in entries.items():
					if isinstance(entry, dict):
						update_data(entry, data[index])
					else:
						data[index] = entry.get()

		update_data(self.entries, self.data)

if __name__ == "__main__":
	root = tk.Tk()
	app = vecedit(root)
	root.mainloop()
