import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QAction, QVBoxLayout, QWidget, QPushButton, QLabel, QStatusBar, QFileDialog, QMenu, QMessageBox, QStyle, QStyleFactory, QTextBrowser, QVBoxLayout, QSpacerItem
from PyQt5.QtGui import QIcon
from urllib.parse import urlparse
import re
import csv
import json
import base64

class URLExtractor(QMainWindow):
	def __init__(self):
		super().__init__()

		self.initUI()

	def initUI(self):
		self.setWindowTitle('Pot-O URL Extract version 1.0.5')
		self.setGeometry(100, 100, 800, 650)

		# Set the window icon
		icon_path = 'favicon.ico'  # Replace 'path_to_your_icon' with the actual path
		self.setWindowIcon(QIcon(icon_path))

		self.textEditInput = QTextEdit(self)
		self.textEditInput.customContextMenuRequested.connect(self.showInputContextMenu)
		self.textEditInput.textChanged.connect(self.clearOutput)

		self.textEditOutput = QTextEdit(self)
		self.textEditOutput.customContextMenuRequested.connect(self.showOutputContextMenu)

		extractButton = QPushButton('EXTRACT URL', self)
		extractButton.setFixedSize(300, 50)  # Set fixed width and height
		extractButton.clicked.connect(self.extractURLs)

		# Centering the button horizontally
		layout = QVBoxLayout()
		layout.addWidget(self.textEditInput)
		layout.addWidget(extractButton, alignment=Qt.AlignCenter)  # Aligning button to the center
		layout.addWidget(self.textEditOutput)

		centralWidget = QWidget()
		centralWidget.setLayout(layout)
		self.setCentralWidget(centralWidget)

		self.statusBar = QStatusBar()
		self.setStatusBar(self.statusBar)

		self.createMenu()

		# Set Fusion style
		QApplication.setStyle(QStyleFactory.create('Fusion'))

	def createMenu(self):
		menubar = self.menuBar()

		fileMenu = menubar.addMenu('File')
		openFile = QAction('Open', self)
		openFile.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))
		openFile.triggered.connect(self.openFile)
		fileMenu.addAction(openFile)

		# Add Open URL Document action to the File menu
		openUrlDocumentAction = QAction('Open Encrypted URL Document', self)
		openUrlDocumentAction.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
		openUrlDocumentAction.triggered.connect(self.openUrlDocument)
		fileMenu.addAction(openUrlDocumentAction)

		# Add Save URLs action to the File menu
		saveUrlsAction = QAction('Save URLs', self)
		saveUrlsAction.setIcon(self.style().standardIcon(QStyle.SP_DialogSaveButton))
		saveUrlsAction.triggered.connect(self.saveUrls)
		fileMenu.addAction(saveUrlsAction)

		# Add Save Encrypted URLs action to the File menu
		saveEncryptedUrlsAction = QAction('Save Encrypted URLs', self)
		saveEncryptedUrlsAction.setIcon(self.style().standardIcon(QStyle.SP_VistaShield))
		saveEncryptedUrlsAction.triggered.connect(self.saveEncryptedUrls)
		fileMenu.addAction(saveEncryptedUrlsAction)

		exitAction = QAction('Exit', self)
		exitAction.setIcon(self.style().standardIcon(QStyle.SP_DialogCloseButton))
		exitAction.triggered.connect(self.close)
		fileMenu.addAction(exitAction)

		editMenu = menubar.addMenu('Edit')

		cutAction = QAction('Cut', self)
		cutAction.setIcon(self.style().standardIcon(QStyle.SP_LineEditClearButton))  # Set cut icon
		cutAction.triggered.connect(self.cutText)
		editMenu.addAction(cutAction)

		copyAction = QAction('Copy', self)
		copyAction.setIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))  # Set copy icon
		copyAction.triggered.connect(self.copyText)
		editMenu.addAction(copyAction)

		pasteAction = QAction('Paste', self)
		pasteAction.setIcon(self.style().standardIcon(QStyle.SP_DialogApplyButton))  # Set paste icon
		pasteAction.triggered.connect(self.pasteText)
		editMenu.addAction(pasteAction)

		selectAllAction = QAction('Select All', self)
		selectAllAction.setIcon(self.style().standardIcon(QStyle.SP_FileDialogListView))  # Set select all icon
		selectAllAction.triggered.connect(self.selectAllText)
		editMenu.addAction(selectAllAction)

		# Add Sort URL sub-menu (checkable))
		sortAction = QAction('Sort URL', self)
		sortAction.setIcon(self.style().standardIcon(QStyle.SP_ToolBarVerticalExtensionButton))
		sortAction.triggered.connect(self.sort_urls_by_filename)
		editMenu.addAction(sortAction)

		aboutMenu = menubar.addMenu('About')
		aboutAction = QAction('About', self)
		aboutAction.setIcon(self.style().standardIcon(QStyle.SP_DialogHelpButton))
		aboutAction.triggered.connect(self.showAboutDialog)
		aboutMenu.addAction(aboutAction)

	def showInputContextMenu(self, position):
		menu = self.textEditInput.createStandardContextMenu()
		menu.exec_(self.textEditInput.mapToGlobal(position))

	def showOutputContextMenu(self, position):
		menu = self.textEditOutput.createStandardContextMenu()
		cutAction = QAction("Cut", self)
		cutAction.triggered.connect(self.textEditOutput.cut)
		copyAction = QAction("Copy", self)
		copyAction.triggered.connect(self.textEditOutput.copy)
		selectAllAction = QAction("Select All", self)
		selectAllAction.triggered.connect(self.textEditOutput.selectAll)

		menu.addAction(cutAction)
		menu.addAction(copyAction)
		menu.addAction(selectAllAction)

		menu.exec_(self.textEditOutput.mapToGlobal(position))

	def openFile(self):
		filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")

		if filename:
			with open(filename, 'r') as file:
				data = file.read()
				self.textEditInput.setPlainText(data)

	def openUrlDocument(self):
		options = QFileDialog.Options()

		filename, _ = QFileDialog.getOpenFileName(self, "Open URL Document", "", "All Files (*);;Text Files (*.txt)", options=options)

		if filename:
			with open(filename, 'r', encoding='utf-8') as file:
				content = file.read().splitlines()

			decrypted_urls = []
			for line in content:
				try:
					decrypted_urls.append(base64.b64decode(line.encode()).decode())
				except base64.binascii.Error:
					decrypted_urls.append(line)

			self.textEditInput.setPlainText('\n'.join(decrypted_urls))
			QMessageBox.information(self, 'Open Successful', f'URL Document opened successfully.')

	def saveUrls(self):
		if not hasattr(self, 'urls_list') or not self.urls_list:
			QMessageBox.warning(self, 'No URLs', 'No URLs to save. Please extract URLs first.')
			return

		options = QFileDialog.Options()

		formats = "CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt)"
		file_format, selected_filter = QFileDialog.getSaveFileName(self, "Save URLs", "", formats, options=options)

		if file_format:
			try:
				selected_extension = selected_filter.split(" ")[-1][2:-1]  # Extract the extension from the selected filter

				# If the chosen file format doesn't have an extension, add the selected one
				if not file_format.lower().endswith(selected_extension):
					file_format += selected_extension

				if selected_extension == '.csv':
					with open(file_format, 'w', newline='', encoding='utf-8') as csvfile:
						csv_writer = csv.writer(csvfile)
						csv_writer.writerow(['URLs'])  # Write header row
						for url in self.urls_list:
							csv_writer.writerow([url])
				elif selected_extension == '.json':
					with open(file_format, 'w', encoding='utf-8') as jsonfile:
						json.dump({'URLs': self.urls_list}, jsonfile, indent=4)
				elif selected_extension == '.txt':
					with open(file_format, 'w', encoding='utf-8') as textfile:
						textfile.write('\n'.join(self.urls_list))
			except Exception as e:
				QMessageBox.warning(self, 'Error', f'Failed to save file: {str(e)}')
				return

			QMessageBox.information(self, 'Save Successful', f'URLs saved as {selected_extension.upper()} to: {file_format}')


	def saveEncryptedUrls(self):
		if not hasattr(self, 'urls_list'):
			QMessageBox.warning(self, 'No URLs', 'No URLs to save. Please extract URLs first.')
			return

		options = QFileDialog.Options()

		file_format, _ = QFileDialog.getSaveFileName(self, "Save Encrypted URLs", "", "Text Files (*.txt)", options=options)

		if file_format:
			encrypted_urls = [base64.b64encode(url.encode()).decode() for url in self.urls_list]
			with open(file_format, 'w', encoding='utf-8') as encrypted_file:
				encrypted_file.write('\n'.join(encrypted_urls))

			QMessageBox.information(self, 'Save Successful', f'Encrypted URLs saved to: {file_format}')

	def clearOutput(self):
		self.textEditOutput.clear()

	def extractURLs(self):
		input_text = self.textEditInput.toPlainText()

		urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', input_text)

		parsed_urls = [urlparse(url) for url in urls]

		formatted_urls = [f"{url.scheme}://{url.netloc}{url.path}" for url in parsed_urls]

		unique_formatted_urls = list(set(formatted_urls))

		self.urls_list = unique_formatted_urls  # Store the unique formatted URLs in self.urls_list

		# Join URLs with a newline (\n) for a line break between each URL
		urls_with_line_break = '\n'.join(unique_formatted_urls)

		self.textEditOutput.setPlainText(urls_with_line_break)  # Set the URLs with line breaks
		self.statusBar.showMessage(f"{len(unique_formatted_urls)} unique URL(s) extracted.")

	def sort_urls_by_filename(self):
		def get_filename_from_url(url):
			parsed_url = urlparse(url)
			path = parsed_url.path
			# Split the path by '/' and get the last part
			filename = path.rsplit('/', 1)[-1]
			# Remove file extension if present
			filename = filename.split('.')[0]
			return filename

		def sorting_key(url):
			filename = get_filename_from_url(url)
			return [int(s) if s.isdigit() else s.lower() for s in re.split(r'(\d+)', filename)]

		self.urls_list = sorted(self.urls_list, key=sorting_key)

		self.textEditOutput.setPlainText('\n'.join(self.urls_list))
		self.statusBar.showMessage(f"{len(self.urls_list)} URLs sorted by filename.")

	def cutText(self):
		self.textEditInput.cut()
		self.textEditOutput.cut()

	def copyText(self):
		self.textEditInput.copy()
		self.textEditOutput.copy()

	def pasteText(self):
		self.textEditInput.paste()
		self.textEditOutput.paste()

	def selectAllText(self):
		self.textEditInput.selectAll()
		self.textEditOutput.selectAll()

	def showAboutDialog(self):
		software_license = (
		"Software License Agreement for Pot-O URL Extract v1.0.5\n\n"
		"1. Definitions\n\n"
		"\"Software\" means the computer program(s) and associated documentation "
		"licensed hereunder.\n\n"
		"2. Grant of License\n\n"
		"Licensor grants Licensee a non-exclusive, non-transferable license to use "
		"the Software for internal business purposes only.\n\n"
		"3. Restrictions\n\n"
		"Licensee may not:\n"
		"* Modify, translate, reverse engineer, decompile, or disassemble the Software.\n"
		"* Create derivative works based on the Software.\n"
		"* Distribute, sublicense, rent, lease, or otherwise transfer the Software "
		"to any third party.\n"
		"* Remove or alter any copyright notices or trademarks contained within "
		"the Software.\n\n"
		"4. Copyright\n\n"
		"The Software is protected by copyright laws and international copyright "
		"treaties. All rights reserved.\n\n"
		"5. Disclaimer of Warranties\n\n"
		"THE SOFTWARE IS PROVIDED \"AS IS,\" WITHOUT WARRANTY OF ANY KIND, EXPRESS "
		"OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
		"FITNESS FOR A PARTICULAR PURPOSE, TITLE, AND NON-INFRINGEMENT. LICENSOR "
		"DISCLAIMS ANY LIABILITY FOR ANY HARM ARISING OUT OF THE USE OR INABILITY TO "
		"USE THE SOFTWARE.\n\n"
		"6. Limitation of Liability\n\n"
		"IN NO EVENT SHALL LICENSOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, "
		"SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, "
		"PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; "
		"OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, "
		"WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) "
		"ARISING IN ANY WAY OUT OF THE USE OF THE SOFTWARE, EVEN IF ADVISED OF THE "
		"POSSIBILITY OF SUCH DAMAGE.\n\n"
		"7. Term and Termination\n\n"
		"This Agreement shall commence on the Effective Date and shall continue until "
		"terminated by either party. This Agreement may be terminated by Licensor "
		"immediately upon any breach by Licensee.\n\n"
		"8. Entire Agreement\n\n"
		"This Agreement constitutes the entire agreement between the parties with "
		"respect to the subject matter hereof and supersedes all prior or contemporaneous "
		"communications, representations, or agreements, whether oral or written.\n\n"
		"9. Severability\n\n"
		"If any provision of this Agreement is held to be invalid or unenforceable, "
		"such provision shall be struck and the remaining provisions shall remain in full "
		"force and effect.\n\n"
		"10. Notices\n\n"
		"All notices and other communications hereunder shall be in writing and shall "
		"be deemed to have been duly given when delivered personally, sent by certified "
		"or registered mail, return receipt requested, postage prepaid, or sent by "
		"overnight courier service to the addresses set forth above.\n\n"
		"11. Waiver\n\n"
		"No waiver by either party of any breach or default hereunder shall be deemed "
		"to be a waiver of any subsequent breach or default.\n\n"
		"12. Construction\n\n"
		"This Agreement shall be construed against the drafting party.\n\n"
		"BY PURCHASING, DOWNLOADING AND USING THE SOFTWARE, YOU AGREE TO BE BOUND BY "
		"THE TERMS OF THIS AGREEMENT.\n"
		)

		about_text = (
			f"Pot-O URL Extract v1.0.5\n\n"
			f"A simple tool to extract unique URLs from any inputted text.\n"
			f"Thank you for using this software/tools.\n"
			f"\n"
			f"Copyright by Muhammad Umar Hasyim Ashari\n"
			f"Jawa Timur, Indonesia.\n"
			f"\n"
			f"Website: https://www.superman.my.id\n"
			f"\n"
			f"This software is build with: Python 3 and PyQt5.\n"
			f"Software Purpose: To help blogging and simplified repetitive task.\n\n"
			f"\n"
			f"{software_license}"
		)

		# Create a QTextEdit widget and set the text
		text_edit = QTextEdit()
		text_edit.setReadOnly(True)
		text_edit.setPlainText(about_text)
		text_edit.setMinimumWidth(500)  # Set minimum width for the QTextEdit

		# Display the QMessageBox with the QTextEdit widget embedded
		msg_box = QMessageBox(self)
		msg_box.setWindowTitle("About Pot-O URL Extract v1.0.5")
		msg_box.setText("License Agreement and Information")
		msg_box.setIcon(QMessageBox.Information)
		msg_box.setInformativeText("Scroll through the license agreement and information:")

		msg_box.layout().addWidget(text_edit)  # Add the QTextEdit widget to the message box layout
		msg_box.exec_()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = URLExtractor()
	window.show()
	sys.exit(app.exec_())
