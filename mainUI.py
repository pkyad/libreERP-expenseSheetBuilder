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
from dialogSearchVendor import searchVendorDialog

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
from libreerp.ui import getLibreUser , libreHTTPDownload
from dialogStart import WelcomeDialog
from dialogSearchSheet import searchSheetDialog
from dialogNewSheet import NewSheetDialog


# class Window(QtGui.QMainWindow , ApplicationSession):
class Window(QtGui.QMainWindow):
    def __init__(self , parent = None, config=None , user = None, sheet = None , name = None , mode = None):
        super(Window, self).__init__(parent)

        self.scans = []

        if mode == 'New':
            self.scans = ['scan.jpg' , 'scan2.jpg', 'scan3.jpg']

        elif mode == 'Open':
            if sheet is None:
                print 'No sheet data provided'
            else:
                for i in sheet['invoices']:
                    link = i['attachment']
                    path , name = libreHTTPDownload(link , os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'temp'))
                    self.scans.append(path)

        self.user = user
        self.showMaximized()
        self.createActions()
        self.createMenus()

        newAction = QtGui.QAction(QtGui.QIcon('./essential_icons/file.png'), 'New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.triggered.connect(self.newFileActionHandler)

        openAction = QtGui.QAction(QtGui.QIcon('./essential_icons/folder-2.png'), 'Open', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.openFileActionHandler)

        scanAction = QtGui.QAction(QtGui.QIcon('./essential_icons/fax.png'), 'Scan', self)
        scanAction.setShortcut('Ctrl+S')
        scanAction.triggered.connect(self.scanActionHandler)

        zoomInAction = QtGui.QAction(QtGui.QIcon('./essential_icons/zoom-in.png'), 'Zoom In', self)
        zoomInAction.triggered.connect(self.zoomIn)

        zoomOutAction = QtGui.QAction(QtGui.QIcon('./essential_icons/zoom-out.png'), 'Zoom Out', self)
        zoomOutAction.triggered.connect(self.zoomOut)

        self.toolbar = self.addToolBar('main')
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(scanAction)
        self.toolbar.addAction(zoomInAction)
        self.toolbar.addAction(zoomOutAction)
        self.toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolbar.setIconSize(QtCore.QSize(15,15))

        self.scaleFactor = 0.0
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                QtGui.QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setBackgroundRole(QtGui.QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)
        # self.scrollArea.setWidgetResizable(True)

        self.setWindowTitle("LibreERP : Expense entry tool")


        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(1)

        self.table.setHorizontalHeaderLabels(QtCore.QString("Pages").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        # self.table.cellDoubleClicked .connect(self.doubleClickedItem)



        self.table.setRowCount(len(self.scans))
        for i in range(len(self.scans)):
            s = self.scans[i]
            self.table.setCellWidget(i,0 , self.getImgWidget(s))
            self.table.setRowHeight(i, 300)
        self.table.currentCellChanged.connect(self.changeImageInView)

        # self.configureWidget = QtGui.QWidget()
        self.table.setMaximumWidth(240)
        # self.configureWidget.setLayout(self.table)

        self.formArea = QtGui.QWidget()

        self.formAreaLayout = QtGui.QGridLayout()

        vendorLbl = QtGui.QLabel('Vendor')
        self.vendorEdit = QtGui.QLineEdit()
        self.vendorEdit.setEnabled(False)

        descLbl = QtGui.QLabel('Description')
        descEdit = QtGui.QTextEdit()
        descEdit.setMaximumHeight(200)

        amountLbl = QtGui.QLabel('Amount')
        amountEdit = QtGui.QLineEdit()

        dateLbl = QtGui.QLabel('Date')

        self.dateSelectedLbl = QtGui.QLabel('No date selected')

        cal = QtGui.QCalendarWidget(self)
        cal.setGridVisible(True)
        cal.clicked[QtCore.QDate].connect(self.showDate)
        cal.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)

        btn = QtGui.QPushButton('Save')
        btn.clicked.connect(self.saveBillDetails)

        searchVendorBtn = QtGui.QPushButton('Search vendor')
        searchVendorBtn.clicked.connect(self.searchVendorHandler)

        self.expenseSheetIDLbl = QtGui.QLabel('IS-123')

        self.formAreaLayout.addWidget(QtGui.QLabel('Sheet ID') , 0,0)
        self.formAreaLayout.addWidget(self.expenseSheetIDLbl , 0,1)

        self.formAreaLayout.addWidget(vendorLbl , 1,0)
        self.formAreaLayout.addWidget(self.vendorEdit , 1,1)
        self.formAreaLayout.addWidget(searchVendorBtn , 1,1)
        self.updateVendorDetails()
        self.formAreaLayout.addWidget(descLbl , 4,0)
        self.formAreaLayout.addWidget(descEdit , 4,1)
        self.formAreaLayout.addWidget(amountLbl , 5,0)
        self.formAreaLayout.addWidget(amountEdit , 5,1)
        self.formAreaLayout.addWidget(dateLbl , 6,0)
        self.formAreaLayout.addWidget(cal , 6,1)
        self.formAreaLayout.addWidget(self.dateSelectedLbl , 7,1)
        self.formAreaLayout.addWidget(btn , 8,0)
        self.formAreaLayout.setMargin(0)
        self.formArea.setLayout(self.formAreaLayout)


        self.form = QtGui.QWidget()
        self.formLayout = QtGui.QGridLayout()
        self.formLayout.addWidget(self.formArea , 0, 0 , QtCore.Qt.AlignTop)
        self.formLayout.setMargin(0)
        self.form.setLayout(self.formLayout)
        self.form.setMinimumWidth(300)
        self.form.setMaximumWidth(350)

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.scrollArea , 0,0)
        self.mainLayout.addWidget(self.form , 0,1)
        self.mainLayout.addWidget(self.table , 0,2)

        self.setCentralWidget(QtGui.QWidget(self))
        self.centralWidget().setLayout(self.mainLayout)

        self.changeImageInView(0,0,0,0)

        print self.scrollArea.width()
        print self.scrollArea.height()
        print self.imageLabel.width()
        print self.imageLabel.height()
        print self.zoomOutAct.isEnabled()




    def changeImageInView(self, row , col , oldRow , oldCol):

        image = QtGui.QImage(self.scans[row])
        self.pixmap = QtGui.QPixmap.fromImage(image)
        self.imageLabel.setPixmap(self.pixmap)

        self.scaleFactor = 1.0
        self.printAct.setEnabled(True)
        self.fitToWindowAct.setEnabled(True)
        self.updateActions()
        if not self.fitToWindowAct.isChecked():
            self.imageLabel.adjustSize()
        # pass

        while self.imageLabel.width() > self.scrollArea.width() and self.zoomOutAct.isEnabled():
            self.zoomOut()


    def searchVendorHandler(self):

        dialog = searchVendorDialog(self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.vendorEdit.setText(dialog.selectedValue['name'])

            self.vendorDetailsGb.deleteLater()
            self.vendorDetailsGb = None
            self.vendorDetailsGb = QtGui.QGroupBox('Vendor details')
            self.vendorLyt = QtGui.QGridLayout()
            self.vendorLyt.addWidget(QtGui.QLabel(QtCore.QString('<span style=" font-size:8pt; font-weight:600; color:black;">Name : </span>' + dialog.selectedValue['name'] + '<br/><span style=" font-size:8pt; font-weight:600; color:black;"> Address : </span>' + dialog.selectedValue['address'])))
            self.vendorDetailsGb.setLayout(self.vendorLyt)
            self.formAreaLayout.addWidget(self.vendorDetailsGb , 2,1)


    def updateVendorDetails(self , vendor = None):

        if vendor is None:
            self.vendorDetailsGb = QtGui.QGroupBox('Vendor details')
            self.vendorLyt = QtGui.QGridLayout()
            self.vendorLyt.addWidget(QtGui.QLabel('Please search and select a vendor <br/> to see its details'))
            self.vendorDetailsGb.setLayout(self.vendorLyt)
            self.formAreaLayout.addWidget(self.vendorDetailsGb , 3,1)
        else:
            pass

    def saveBillDetails(self):
        pass

    def showDate(self , date):
        self.dateSelectedLbl.setText(date.toString('dd-MMM-yyyy'))

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

    # def doubleClickedItem(self):
    #     pass

    def newFileActionHandler(self):
        pass

    def openFileActionHandler(self):
        pass

    def scanActionHandler(self):
        pass

    def exitHandler(self):
        if QtGui.QMessageBox.question(None, '', "Are you sure you want to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()

    def createActions(self):

        self.newAct = QtGui.QAction("&New", self, triggered=self.about)
        self.openAct = QtGui.QAction("&Open", self, shortcut="Ctrl+O", triggered=self.about)
        self.exitAct = QtGui.QAction("&Exit", self, triggered=self.exitHandler)

        self.printAct = QtGui.QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.aboutQtAct = QtGui.QAction("About &Qt", self,
                triggered=QtGui.qApp.aboutQt)

        self.aboutAct = QtGui.QAction("&About", self, triggered=self.about)

        self.zoomInAct = QtGui.QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QtGui.QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl+-", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QtGui.QAction("&Normal Size", self,
                shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)
        # tab related menu options

        self.logoutAct = QtGui.QAction("Logout" , self , triggered = self.logout)

    def print_(self):
        dialog = QtGui.QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QtGui.QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)

    def normalSize(self):
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()
        self.updateActions()

    def logout(self):
        os.remove(os.path.expanduser('~/.libreerp/token.key'))
        self.close()

    def createMenus(self):

        self.fileMenu = QtGui.QMenu("&File", self)
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.exitAct)
        self.fileMenu.addAction(self.printAct)

        self.helpMenu = QtGui.QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)


        self.viewMenu = QtGui.QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.viewMenu)



        if self.user is not None:
            self.userMenu =  QtGui.QMenu(("&%s %s" %(self.user.first_name , self.user.last_name)) , self)
            self.userMenu.addAction(self.logoutAct)

            self.menuBar().addMenu(self.userMenu)

        self.menuBar().addMenu(self.helpMenu)


    def about(self):
        dialog = aboutDetailsDialog(self)
        dialog.exec_()

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))
    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

if __name__ == '__main__':

    # app_icon = QtGui.QIcon()
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(16,16))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(24,24))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(32,32))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(48,48))
    # app_icon.addFile('./robot_icon.png', QtCore.QSize(256,256))
    # app.setWindowIcon(app_icon)


    # # if wamp is required
    # pyqt4reactor.install()
    # runner = ApplicationRunner(url= u"ws://localhost:8080/ws", realm = u"default")
    # runner.run(Window)
    #
    # # if wamp is not required


    usr = getLibreUser()

    print usr
    app = QtGui.QApplication(sys.argv)

    welcome = WelcomeDialog()
    invalid = False
    sheetName = None
    sheet = None

    if welcome.exec_() == QtGui.QDialog.Accepted:
        print welcome.mode
        if welcome.mode == 'New':
            newSheet = NewSheetDialog()
            if newSheet.exec_() == QtGui.QDialog.Accepted:
                sheetName = newSheet.sheetName
            else:
                invalid = True
        elif welcome.mode == 'Open':
            search = searchSheetDialog()
            if search.exec_() == QtGui.QDialog.Accepted:
                sheet = search.selectedValue
            else:
                invalid = True
        if invalid:
            sys.exit()
    else:
        sys.exit()

    print sheet

    window = Window(user = usr , sheet = sheet , name = sheetName , mode = welcome.mode)
    window.show()

    sys.exit(app.exec_())
