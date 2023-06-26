import sys
from WebAppMicroscopy import MainWindow
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QMessageBox, QFileDialog, QGridLayout, QSizePolicy, QMainWindow
    

if not QApplication.instance():
    app = QApplication(sys.argv)
else:
    app = QApplication.instance()


if __name__ == "__main__":
    app = QApplication(sys.argv)
  
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())




