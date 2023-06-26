import sys
from PyQt5.QtCore import Qt,QUrl
import os
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap, QKeySequence,QFont,QDesktopServices
from PyQt5.QtWidgets import QGroupBox,QComboBox, QApplication, qApp, QWidget,QAction, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QMessageBox, QFileDialog, QGridLayout, QSizePolicy, QMainWindow
import cv2
from flask import Flask, render_template, Response
import numpy as np



class MainWindow(QMainWindow):
    
    
    def __init__(self):
        
       
        super().__init__()
        self.setGeometry(50, 50, 950, 1000)
        # Initialize the draw_contours attribute to False
        self.draw_contours = False
        
        stylesheet = """border: 2px solid; border-color:red; background-color:Darkgray; 
        
        """
        stylesheet = """border: 2px solid; background-color:black"""
        self.setStyleSheet(stylesheet)
    
        # Initialize the UI
        self.initUI()
        
    def reset_image(self):
        if hasattr(self, "image"):
            self.slider.setValue(0)
    
    def load_image(self):
        # Open a file dialog to select an image file
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        if file_name:
            # Load the image and display it in the label
            self.image = cv2.imread(file_name)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.draw_contours = False
            self.update_image()
            
    
    def update_image(self):
        
        
        threshold2 = 10

        # Check if an image is currently loaded  
        if hasattr(self, "image"):
            # Create a copy of the original image to draw contours on
            img_with_contours = self.image.copy()
        
            # Convert the image to grayscale
            gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
            # Apply threshold using the slider value
            _, thresh = cv2.threshold(gray, 255-self.slider.value(), 255, cv2.THRESH_BINARY)


            _, thresh = cv2.threshold(gray, 255-self.slider.value(), 255, cv2.THRESH_BINARY)

            slider_text = "Threshold Value: " + str( 255-self.slider.value())
            self.slider_value_label.setText(slider_text)
            # Initialize the contours variable
            contours = []

            # Find the contours
            if self.draw_contours:
                contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                cv2.drawContours(img_with_contours, contours, -3, (0, 0, 255), 2, cv2.LINE_AA)

                # Calculate total cell mass
                total_mass = 0
                for contour in contours:
                    area = cv2.contourArea(contour)
                    total_mass += area

                # Add total cell mass text to the bottom of the window
                mass_text = "Total Cell Mass in Image: " + str(total_mass)
                self.mass_label.setText(mass_text)
                self.mass_label.setFont(QFont("Cascadia Mono"))
                self.mass_label.setStyleSheet("background-color: black; color :lime; border: 0.5px solid black;")

                # Filter out contours that are too small
            filtered_contours = []

            for contour in contours:
                area = cv2.contourArea(contour)

                if area >= threshold2:
                    filtered_contours.append(contour)

            # Count the number of cells
            num_cells = len(filtered_contours)

            # Add cell count text to the bottom of the window
            cell_count_text = "Cell Count: " + str(num_cells)
            self.cell_count_label.setText(cell_count_text)
            self.cell_count_label.setFont(QFont("Cascadia Mono"))
            self.cell_count_label.setStyleSheet("background-color: black; color :lime; border: 0.5px solid black;")

        
            # Convert the threshold image to RGB for display
            self.thresh_rgb = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
        
            # Resize the images to fit the label widgets
            h, w, c = self.image.shape
            dpi = 72  # assuming the DPI of the image is 72
            new_w = int(10 * dpi)
            new_h = int(10 * dpi)
            resized_image = cv2.resize(self.image, (new_w, new_h))
            resized_gray = cv2.resize(gray, (new_w, new_h))
            resized_thresh = cv2.resize(self.thresh_rgb, (new_w, new_h))
            self.resized_contours = cv2.resize(img_with_contours, (new_w, new_h))
        
            # Convert the images to QPixmap and update the existing labels
            pixmap_contours = QPixmap.fromImage(QImage(self.resized_contours.data, self.resized_contours.shape[1], self.resized_contours.shape[0], QImage.Format_RGB888))
            #self.final_image = np.array(pixmap_contours)
            self.contours_label.setPixmap(pixmap_contours)




        else:
            self.image_label.clear()
            
    def info_box(self):
        msg = QMessageBox()
        msg.setWindowTitle("Additional Information")
        msg.setStyleSheet("background-color: black; color :lime; border: 0.5px solid black;")
        msg.setFont(QFont("Cascadia Mono"))
        msg.setText('''
Developers: Jan Ramos, Nicolas Ruiz

Supervisors: Ruy Andrade Louzada, Ernesto Bernal-Mizrachi

Contributors: Chris Fraker, Flavia Leticia Martins Pecanha
                    ''')
        msg.exec_()
        
        
        
    def toggle_contours(self, state):
        
        # Set the draw contours flag based on the state of the button
        self.draw_contours = state
        # Update the image display
        self.update_image()
        
    def save_image(self):
        # Check if an image is currently loaded
        if hasattr(self, "image"):
            # Open a file dialog to select a save location
            file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Image Files (*.png *.jpg *.bmp)")
            if file_name:
                # Save the image to the selected location
                cv2.imwrite(file_name, self.resized_contours)
                
    def delete_image(self):
        ## Check if an image is currently loaded
        if hasattr(self, "image"):  
            # Ask the user for confirmation before deleting the image
            msg_box = QMessageBox()
            msg_box.setText("Are you sure you want to delete the image?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            response = msg_box.exec_()
            if response == QMessageBox.Yes:
                # Delete the image and clear the label
                del self.image 
                self.image_label.clear()
                
    def adjust_label_size(self, event):
        self.image_label.setFixedSize(self.width(), self.height())

    def openUrl(self):
        url = QtCore.QUrl('https://www.riverbankcomputing.com/software/pyqt/')
        if not QDesktopServices.openUrl(url):
            QMessageBox.warning(self, 'Open Url', 'Could not open url')        
   
    def initUI(self):
        
        
        '''
        Structure:
            
        menu_bar{
            File: Save
            Help: About Qt, Info
            Exit
            }
        layout{
            main_layout{
                title_layout
                
                threshold_layout
                
                image_layout
                    {
                    slider -> contour image
                    }
                    
                results_layout
                    {
                    cell count 
                    cell mass
                    }
                
                right_layout
                    {
                    buttons_layout
                    }
                }
            }
        
        '''
        
        # Add title to App window
        self.setWindowTitle("Image Processing App")
        
        # Add main menu bar to App
        self.menu = self.menuBar()
        self.menu.setStyleSheet("background-color: Darkgray; color :black; border: 0.5px solid black;")
        
        #File tab allows users to save or delete their files. 
        self.menu_file = self.menu.addMenu("File")
        
        # Add save function to File tab
        self.save = QAction("Save", self)
        self.menu_file.addAction(self.save)
        self.save.triggered.connect(self.save_image)
        
        # Add delete function to File tab
        #self.delete = QAction("Delete", self)
        #self.menu_file.addAction(self.delete)
        #self.delete.triggered.connect(self.delete_image)
        
        #Help tab allows users to Exit program
        self.menu_about = self.menu.addMenu("&Help")
        
        # Add about function to File tab
        self.qtabout = QAction("About Qt", self)
        self.menu_about.addAction(self.qtabout)
        self.qtabout.triggered.connect(self.openUrl)
        
        # Add info function to File tab
        self.info = QAction("Info", self)
        self.menu_about.addAction(self.info)
        self.info.triggered.connect(self.info_box)


        # Add exit to menu bar
        self.menu_exit = self.menu.addAction("Exit")
        self.menu_exit.triggered.connect(self.close)
        
        
        
        #This is the main layout of our application. It is a vertical layout
        self.main_layout = QVBoxLayout()
        
        #This is the title layout of the App
        title_layout = QVBoxLayout()
        self.title = QLabel("Computational Microscopy")
        self.title.setAlignment(Qt.AlignTop)
        self.title.setFont(QFont("Cascadia Mono",20))
        self.title.setStyleSheet("background-color: black; color :lime; border: 0.5px solid lime;")
        self.title.setSizePolicy(100, 100)
        self.title.move(100,100)
        title_layout.addWidget(self.title)
        
        
        #Add title layout onto main layout
        self.main_layout.addLayout(title_layout)
        
        
        #This is the threshold layout that displays the thresholding
        threshold_layout = QVBoxLayout()
        
        
        self.slider_value_label = QLabel(self)
        self.slider_value_label.setAlignment(Qt.AlignCenter)
        self.slider_value_label.setFont(QFont("Cascadia Mono"))
        self.slider_value_label.setStyleSheet("background-color: black; color :lime; border: 0.5px solid black;")
        threshold_layout.addWidget(self.slider_value_label)


        #Add threshold layout onto main_layout
        self.main_layout.addLayout(threshold_layout)
        
        #This is the layout for the slider and image. It is a horizontal layout
        image_layout = QHBoxLayout()
        
        
        # Create slide bar to adjust threshold
        self.slider = QSlider()
        self.slider.setGeometry(QtCore.QRect(190, 100, 160, 16))
        self.slider.setMinimum(0)
        self.slider.setMaximum(255) 
        self.slider.setValue(115)
        self.slider.valueChanged.connect(self.update_image)
        self.slider.setStyleSheet("background-color: black; color :lime; border: 0.5px solid black;")
        
        # Add slider to image layout
        image_layout.addWidget(self.slider)
        
        #Creates the widget for our image
        self.contours_label = QLabel("No Image Uploaded")
        self.contours_label.setAlignment(Qt.AlignCenter)
        self.contours_label.setStyleSheet("background-color: black; color :lime; border: 0.5px solid Darkgray;")
        self.contours_label.setFont(QFont("Cascadia Mono",18,-0.05))
        
        
        # Adds context menu to image 
        self.contours_label.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.contours_label.addAction(self.save)

        # Add image to image layout
        image_layout.addWidget(self.contours_label)
        
        # Add image layout to main layout
        self.main_layout.addLayout(image_layout)
       
        
        # Create results layout
        results_layout =  QVBoxLayout() 
        
        # Create a label to display the cell count
        self.cell_count_label = QLabel(self)
        self.cell_count_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.cell_count_label)

        # Create a label to display the cell mass
        self.mass_label = QLabel(self)
        self.mass_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.mass_label)
    
        self.main_layout.addLayout(results_layout)
       
        
       # Create button layout
        # Use similar horizontal layout
        buttons_layout = QHBoxLayout()
        
        # This creates the button widgets
        self.button1 = QPushButton("Load Image")
        self.button1.setFont(QFont("Cascadia Mono",12))
        self.button1.setSizePolicy(200, 200)
        self.button1.setStyleSheet("background-color: black; color :lime; border: 0.5px solid lime;")
        self.button1.clicked.connect(self.load_image)
        
        
        self.button2 = QPushButton("Toggle Contour")
        self.button2.setFont(QFont("Cascadia Mono",12))
        self.button2.setCheckable(True)
        self.button2.clicked.connect(self.toggle_contours)
        self.button2.setStyleSheet("background-color: black; color :lime; border: 0.5px solid lime;")
        self.button2.setSizePolicy(100, 100)
        
        #Adds the widgets to our box layour
        buttons_layout.addWidget(self.button1)
        buttons_layout.addWidget(self.button2)
        
        
        # Additional layout to place buttons closer
        right_layout = QHBoxLayout()
        right_layout.addLayout(buttons_layout, 1)
     
        layout = QVBoxLayout()
        layout.addLayout(self.main_layout)
        layout.addLayout(right_layout)
        
        # Create Widget
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        
        
        
        
         