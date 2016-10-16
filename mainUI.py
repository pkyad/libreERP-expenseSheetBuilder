#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2016 Pradeep Kumar Yadav.
## All rights reserved.
##
##
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################

from os import environ
import sys
from argparse import ArgumentParser , ArgumentTypeError
from random import randint
import math
import os
from PyQt4 import QtCore, QtGui, QtOpenGL
import lxml.etree as etree
from xml.dom import minidom

try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL 2dpainting",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)
from dialog_about import *
import string
import random
import json
import xml.etree.ElementTree as ET



# class Window(QtGui.QMainWindow , ApplicationSession):
class Window(QtGui.QMainWindow):
    def __init__(self , parent = None, config=None , user = None):
        super(Window, self).__init__(parent)
        self.user = user
        self.showMaximized()
        self.createActions()
        self.createMenus()

        newAction = QtGui.QAction(QtGui.QIcon('./essential_icons/file.png'), 'New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newFileActionHandler)

        scanAction = QtGui.QAction(QtGui.QIcon('./essential_icons/fax.png'), 'Scan', self)
        scanAction.setShortcut('Ctrl+S')
        scanAction.triggered.connect(self.scanActionHandler)


        self.toolbar = self.addToolBar('main')
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(scanAction)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)

        self.scaleFactor = 0.0
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        self.setWindowTitle("LibreERP : Expense entry tool")


        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)

        self.table.setHorizontalHeaderLabels(QtCore.QString("Pages").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.table.cellDoubleClicked .connect(self.doubleClickedItem)

        scans = ['scan.jpg' , 'scan.jpg', 'scan.jpg', 'scan.jpg', 'scan.jpg', 'scan.jpg', 'scan.jpg', 'scan.jpg', 'scan.jpg']

        self.table.setRowCount(len(scans))
        for i in range(len(scans)):
            s = scans[i]

            self.table.setCellWidget(i,0 , self.getImgWidget(s))
            self.table.setRowHeight(i, 300)

        # self.configureWidget = QtGui.QWidget()
        self.table.setMaximumWidth(240)
        # self.configureWidget.setLayout(self.table)

        self.formArea = QtGui.QWidget()

        self.formAreaLayout = QtGui.QGridLayout()

        vendorLbl = QtGui.QLabel('Vendor')
        vendorEdit = QtGui.QLineEdit()
        vendorEdit.setEnabled(False)

        descLbl = QtGui.QLabel('Description')
        descEdit = QtGui.QTextEdit()
        descEdit.setMaximumHeight(200)

        amountLbl = QtGui.QLabel('Amount')
        amountEdit = QtGui.QLineEdit()

        dateLbl = QtGui.QLabel('Date')

        cal = QtGui.QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.clicked[QtCore.QDate].connect(self.showDate)

        btn = QtGui.QPushButton('Save')
        btn.clicked.connect(self.saveBillDetails)

        searchVendorBtn = QtGui.QPushButton('Search vendor')
        searchVendorBtn.clicked.connect(self.saveBillDetails)

        gb = QtGui.QGroupBox('Vendor details')


        self.formAreaLayout.addWidget(vendorLbl , 0,0)
        self.formAreaLayout.addWidget(vendorEdit , 0,1)
        self.formAreaLayout.addWidget(searchVendorBtn , 1,1)
        self.formAreaLayout.addWidget(gb , 2,1)
        self.formAreaLayout.addWidget(descLbl , 3,0)
        self.formAreaLayout.addWidget(descEdit , 3,1)
        self.formAreaLayout.addWidget(amountLbl , 4,0)
        self.formAreaLayout.addWidget(amountEdit , 4,1)
        self.formAreaLayout.addWidget(dateLbl , 5,0)
        self.formAreaLayout.addWidget(cal , 5,1)
        self.formAreaLayout.addWidget(btn , 6,0)
        self.formAreaLayout.setMargin(0)
        self.formArea.setLayout(self.formAreaLayout)


        self.form = QtGui.QWidget()
        self.formLayout = QtGui.QGridLayout()
        self.formLayout.addWidget(self.formArea , 0, 0 , QtCore.Qt.AlignTop)
        self.formLayout.setMargin(0)
        self.form.setLayout(self.formLayout)
        self.form.setMinimumWidth(300)
        self.form.setMaximumWidth(400)

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.scrollArea , 0,0)
        self.mainLayout.addWidget(self.form , 0,1)
        self.mainLayout.addWidget(self.table , 0,2)

        self.setCentralWidget(QtGui.QWidget(self))
        self.centralWidget().setLayout(self.mainLayout)

    def saveBillDetails(self):
        pass

    def showDate(self , date):
        print date

    def getImgWidget(self , s):
        imageLabel = QtGui.QLabel()
        imageLabel.setFixedWidth(200)
        image = QtGui.QImage(s)
        myPixmap = QtGui.QPixmap.fromImage(image)
        myScaledPixmap = myPixmap.scaled(imageLabel.size(), QtCore.Qt.KeepAspectRatio)
        imageLabel.setPixmap(myScaledPixmap)
        wdg = QtGui.QWidget()
        wdgLt = QtGui.QGridLayout()
        wdgLt.setMargin(10)
        wdgLt.addWidget(imageLabel)
        wdg.setLayout(wdgLt)
        return wdg

    def goToPrev(self):
        pass
    def goToNext(self):
        pass

    def doubleClickedItem(self):
        pass

    def newFileActionHandler(self):
        pass
    def scanActionHandler(self):
        pass

    def createActions(self):
        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        # tab related menu options

        self.logoutAct = QtGui.QAction("Logout" , self , triggered = self.close)

    def createMenus(self):

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        self.menuBar().addMenu(self.helpMenu)

        if self.user is not None:
            self.userMenu =  QtGui.QMenu(("&%s %s" %(self.user.first_name , self.user.last_name)) , self)
            self.userMenu.addAction(self.logoutAct)

            self.menuBar().addMenu(self.userMenu)

    def about(self):
        dialog = aboutDetailsDialog(self)
        dialog.exec_()

if __name__ == '__main__':

    app = QtGui.QApplication(sys.argv)
    # app_icon = QtGui.QIcon()
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(16,16))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(24,24))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(32,32))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(48,48))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(256,256))
    # app.setWindowIcon(app_icon)
    # welcomeScreen = loginScreen()
    # if welcomeScreen.exec_() == QtGui.QDialog.Accepted:
    #     window = Window(user = welcomeScreen.user)
    #     window.show()
    # else:
    #     sys.exit()


    # # if wamp is required
    # pyqt4reactor.install()
    # runner = ApplicationRunner(url= u"ws://localhost:8080/ws", realm = u"default")
    # runner.run(Window)
    #
    # # if wamp is not required
    window = Window()
    window.show()

    sys.exit(app.exec_())
