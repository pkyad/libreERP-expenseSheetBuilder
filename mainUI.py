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
from dialogReviewAndSubmit import resultDialog
from datetime import datetime
import pytz

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
from libreerp.ui import getLibreUser , libreHTTPDownload , libreHTTP
from dialogStart import WelcomeDialog
from dialogSearchSheet import searchSheetDialog
from dialogNewSheet import NewSheetDialog
from dialogSearchVendor import addressToString

import os, shutil
from wand.image import Image
import time

def cleanFolder(folder):
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            #elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)


# class Window(QtGui.QMainWindow , ApplicationSession):
class Window(QtGui.QMainWindow):
    def __init__(self , parent = None, config=None , user = None, sheet = None , name = None , mode = None):
        super(Window, self).__init__(parent)

        self.scans = []

        # if mode == 'New':
        #     # self.sheetID = sheet['pk']
        #     self.scans = ['scan.jpg' , 'scan2.jpg', 'scan3.jpg']
        #     self.sheet = sheet
        # elif mode == 'Open':
        self.openSheet(sheet)

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

        addFileAction = QtGui.QAction(QtGui.QIcon('./essential_icons/attachment.png'), 'Add File', self)
        addFileAction.triggered.connect(self.addFile)

        addFileAction = QtGui.QAction(QtGui.QIcon('./essential_icons/compose.png'), 'Edit Sheet Details', self)
        addFileAction.triggered.connect(self.editSheetDetails)

        submitSheetAction = QtGui.QAction(QtGui.QIcon('./essential_icons/archive-3.png'), 'Review and Submit', self)
        submitSheetAction.triggered.connect(self.reviewAndSubmit)

        self.toolbar = self.addToolBar('main')
        self.toolbar.addAction(newAction)
        self.toolbar.addAction(openAction)
        self.toolbar.addAction(scanAction)
        self.toolbar.addAction(zoomInAction)
        self.toolbar.addAction(zoomOutAction)
        self.toolbar.addAction(addFileAction)
        self.toolbar.addAction(submitSheetAction)
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
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.currentCellChanged.connect(self.changeImageInView)
        self.table.customContextMenuRequested.connect(self.tableContextMenuHandler)
        # self.table.cellDoubleClicked .connect(self.doubleClickedItem)

        self.refreshScansList()
        # self.configureWidget.setLayout(self.table)

        self.formArea = QtGui.QWidget()

        self.formAreaLayout = QtGui.QGridLayout()

        vendorLbl = QtGui.QLabel('Vendor')
        self.vendorEdit = QtGui.QLineEdit()
        self.vendorEdit.setEnabled(False)

        descLbl = QtGui.QLabel('Description')
        self.descEdit = QtGui.QTextEdit()
        self.descEdit.setMaximumHeight(200)

        amountLbl = QtGui.QLabel('Amount')
        self.amountEdit = QtGui.QLineEdit()

        dateLbl = QtGui.QLabel('Date')

        self.dateSelectedLbl = QtGui.QLabel('No date selected')

        self.cal = QtGui.QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.clicked[QtCore.QDate].connect(self.showDate)
        self.cal.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)

        saveBtn = QtGui.QPushButton('Save')
        saveBtn.clicked.connect(self.saveBillDetails)

        searchVendorBtn = QtGui.QPushButton('Search vendor')
        searchVendorBtn.clicked.connect(self.searchVendorHandler)

        self.expenseSheetIDLbl = QtGui.QLabel('ES-%s'%(self.sheet['pk']))

        self.formAreaLayout.addWidget(QtGui.QLabel('Sheet ID') , 0,0)
        self.formAreaLayout.addWidget(self.expenseSheetIDLbl , 0,1)

        self.formAreaLayout.addWidget(vendorLbl , 1,0)
        self.formAreaLayout.addWidget(self.vendorEdit , 1,1)
        self.formAreaLayout.addWidget(searchVendorBtn , 1,1)
        self.updateVendorDetails()
        self.formAreaLayout.addWidget(descLbl , 4,0)
        self.formAreaLayout.addWidget(self.descEdit , 4,1)
        self.formAreaLayout.addWidget(amountLbl , 5,0)
        self.formAreaLayout.addWidget(self.amountEdit , 5,1)
        self.formAreaLayout.addWidget(dateLbl , 6,0)
        self.formAreaLayout.addWidget(self.cal , 6,1)
        self.formAreaLayout.addWidget(self.dateSelectedLbl , 7,1)
        self.formAreaLayout.addWidget(saveBtn , 8,0)
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

        self.changeImageInView(0,0,0,0, loading = True)

        # print self.scrollArea.width()
        # print self.scrollArea.height()
        # print self.imageLabel.width()
        # print self.imageLabel.height()
        # print self.zoomOutAct.isEnabled()
    def reviewAndSubmit(self):
        dialog = resultDialog(self , self.sheet, self.user)
        dialog.exec_()

    def editSheetDetails(self):
        sheetEditor = NewSheetDialog(full = True , sheet = self.sheet)
        if sheetEditor.exec_() == QtGui.QDialog.Accepted:
            if sheetEditor.project is not None:
                data = {'notes' : str(sheetEditor.sheetName) , 'project' : sheetEditor.project['pk']}
                self.sheet['project'] = sheetEditor.project
            else:
                data = {'notes' : str(sheetEditor.sheetName)}
                # update the project ID in the sheet
            self.sheet['notes'] = sheetEditor.sheetName
            res = libreHTTP(url = '/api/finance/expenseSheet/%s/' %(self.sheet['pk']) ,method = 'patch' , data= data , debug = True)


    def addFile(self):
        fileName = QtGui.QFileDialog.getOpenFileName(self, "Existing scans file", QtCore.QDir.homePath())
        tmpFolderPath = os.path.join(os.getcwd() , '.tmp')
        try:
            os.mkdir(tmpFolderPath)
        except:
            pass
        fileName = str(fileName)
        # basically the fileName is the file path from the QT file picker
        if len(fileName)!=0:
            if fileName.endswith('pdf'):
                cleanFolder(tmpFolderPath)
                with Image(filename=fileName, resolution=300) as img:
                    img.save(filename=os.path.join(tmpFolderPath , "temp.png"))
                for i, f in enumerate(os.listdir(tmpFolderPath)):
                    filePath =os.path.join(tmpFolderPath , f)
                    self.scans.append(filePath)
                    invoice = {'pk' : None , 'user' : self.user.pk , 'created' : datetime.now() , 'service' : None , 'amount' : 0 , 'currency': 'INR' , 'dated' : datetime.now() , 'attachment' : None , 'sheet' : self.sheetID , 'description' : '' , 'approved' : False , 'file' :  filePath}
                    self.sheet['invoices'].append(invoice)
            elif fileName.endswith('jpg') or fileName.endswith('png'):
                self.scans.append(fileName)
                invoice = {'pk' : None , 'user' : self.user.pk , 'created' : datetime.now() , 'attachment' : None ,'service' : None , 'amount' : 0 , 'currency': 'INR' , 'dated' : datetime.now() , 'sheet' : self.sheetID , 'description' : '' , 'approved' : False , 'file' :  fileName}
                self.sheet['invoices'].append(invoice)
            self.refreshScansList()


    def changeImageInView(self, row , col , oldRow , oldCol , loading = False):
        print oldRow, row , oldCol , col
        if oldRow>=0 and not loading:
            self.sheet['invoices'][oldRow]['amount'] = int(self.amountEdit.text())
            self.sheet['invoices'][oldRow]['description'] = str(self.descEdit.toPlainText())

        if len(self.sheet['invoices'])==0:
            return

        invoice = self.sheet['invoices'][row]
        print invoice
        print '--------------------------'
        amount = invoice['amount']
        desc = invoice['description']
        service = invoice['service']
        dated = invoice['dated']
        self.amountEdit.setText(str(amount))
        self.descEdit.setText(desc)
        # print invoice['service']

        self.showDate(dated)
        self.cal.setSelectedDate(dated)
        # if service is not None:
        self.updateVendorInVIew(service)

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

    def updateVendorInVIew(self , vendor):
        if vendor is None:
            vendorLabel = QtGui.QLabel('Browse and Select one')
            vendorName = 'Not selected'
        else:
            vendorLabel = QtGui.QLabel(QtCore.QString('<span style=" font-size:8pt; font-weight:600; color:black;">Name : </span>' + vendor['name'] + '<br/><span style=" font-size:8pt; font-weight:600; color:black;"> Address : </span>' + vendor['address']))
            vendorName = vendor['name']
        self.vendorDetailsGb.deleteLater()
        self.vendorDetailsGb = None
        self.vendorDetailsGb = QtGui.QGroupBox('Vendor details')
        self.vendorLyt = QtGui.QGridLayout()
        self.vendorLyt.addWidget(vendorLabel)
        self.vendorDetailsGb.setLayout(self.vendorLyt)
        self.formAreaLayout.addWidget(self.vendorDetailsGb , 2,1)
        self.vendorEdit.setText(vendorName)

    def searchVendorHandler(self):

        dialog = searchVendorDialog(self)
        if dialog.exec_() == QtGui.QDialog.Accepted:
            vendor = dialog.selectedValue
            self.updateVendorInVIew(vendor)
            self.sheet['invoices'][self.table.currentRow()]['service'] = vendor
            print vendor

    def updateVendorDetails(self , vendor = None):

        if vendor is None:
            self.vendorDetailsGb = QtGui.QGroupBox('Vendor details')
            self.vendorLyt = QtGui.QGridLayout()
            self.vendorLyt.addWidget(QtGui.QLabel('Please search and select a vendor <br/> to see its details'))
            self.vendorDetailsGb.setLayout(self.vendorLyt)
            self.formAreaLayout.addWidget(self.vendorDetailsGb , 3,1)
        else:
            pass

    def tableContextMenuHandler(self, pt):
        menu = QtGui.QMenu(self)
        replace = menu.addAction("Replace")
        delete = menu.addAction("Delete")
        scan = menu.addAction("Scan")
        print pt
        action = menu.exec_(self.table.mapToGlobal(pt))
        if action == replace:
            # print 'replace'
            filePath = QtGui.QFileDialog.getOpenFileName(self, "Existing scans file", QtCore.QDir.homePath())
            fileName = self.sheet['invoices'][ind]['attachment'].split('/')[-1]
            self.sheet['invoices'][self.table.currentRow()]['file'] = filePath

        elif action == delete:
            # print 'delete'
            if QtGui.QMessageBox.question(None, '', "Are you sure you want to delete the invoie from the server ?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.No:
                return
            invPk = self.sheet['invoices'][self.table.currentRow()]['pk']
            ind = self.table.currentRow()
            fileName = self.sheet['invoices'][ind]['attachment'].split('/')[-1]
            os.remove(os.path.join(os.curdir , 'temp' , fileName))
            self.sheet['invoices'].pop(ind)
            self.scans.pop(ind)
            res = libreHTTP(url = '/api/finance/invoice/' + str(invPk) + '/' , method = 'delete')
            # print res
            self.refreshScansList()
            # self.changeImageInView(0,0,0,0, loading = True)
            # self.table.setCurrentCell(0,0)

        elif action == scan:
            print 'scan'

    def saveBillDetails(self):
        # get the selected row in the table and make a post request to save the data
        # print self.table.currentRow()

        invoice = self.sheet['invoices'][self.table.currentRow()]
        if invoice['attachment'] is None:
            files = {'attachment' : open(invoice['file'], 'rb')}
        else:
            # if the user changed or added a file the attachment is None and the file is to be uploaded from the .tmp folder
            files = None
        if invoice['service'] is None:
            return
        try:
            dateStr = str(self.cal.selectedDate().toString('yyyy-MM-dd'))
        except:
            dateStr = str(self.cal.selectedDate().strftime("%Y-%m-%d"))

        data = {
            'service' : invoice['service']['pk'],
            'amount' : str(self.amountEdit.text()),
            'currency' : 'INR',
            'dated' : dateStr,
            'sheet' : self.sheetID,
            'description' : str(self.descEdit.toPlainText())
        }
        # print '---------------------------------'
        # print invoice
        # print invoice['pk']
        url = '/api/finance/invoice/'
        if invoice['pk'] is None:
            method = 'post'
        else:
            method = 'patch'
            url +=  str(invoice['pk']) + '/'

        res = libreHTTP(url = url , method = method , data = data , files = files , debug = True )
        print res


    def showDate(self , date):
        # print date.__class__
        try:
            self.dateSelectedLbl.setText(date.toString('dd-MMM-yyyy'))
        except:
            self.dateSelectedLbl.setText(date.strftime("%d-%m-%Y"))
        self.sheet['invoices'][self.table.currentRow()]['dated'] = date

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

    def refreshScansList(self):
        self.table.setRowCount(len(self.scans))
        for i in range(len(self.scans)):
            s = self.scans[i]
            self.table.setCellWidget(i,0 , self.getImgWidget(s))
            self.table.setRowHeight(i, 300)

        # self.configureWidget = QtGui.QWidget()
        self.table.setMaximumWidth(240)

    def newFileActionHandler(self):
        if QtGui.QMessageBox.question(None, '', "Are you sure you want to start a new ? any unsaved data will be lost", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            self.scans = []
            self.sheet = None
            self.sheetID = -1
            self.refreshScansList()
            self.imageLabel = QtGui.QLabel()
            self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
            self.imageLabel.setSizePolicy(QtGui.QSizePolicy.Ignored,
                    QtGui.QSizePolicy.Ignored)
            self.imageLabel.setScaledContents(True)
            self.scrollArea.setWidget(self.imageLabel)


    def openFileActionHandler(self):
        search = searchSheetDialog()
        if search.exec_() == QtGui.QDialog.Accepted:
            sheet = search.selectedValue
            self.openSheet(sheet , alreadyOpen = True)

    def openSheet(self , sheet , alreadyOpen = False):
        if sheet is None:
            print 'No sheet data provided'
        else:
            self.sheet = sheet
            self.scans = []
            utc=pytz.UTC
            self.sheetID = sheet['pk']
            for i in self.sheet['invoices']:

                link = i['attachment']
                path , name = libreHTTPDownload(link , os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'temp'))
                self.scans.append(path)

                i['service']['address'] = addressToString(i['service']['address'])
                i['dated'] = datetime.strptime(i['dated'], '%Y-%m-%d')
                i['dated'] = i['dated'].replace(tzinfo=utc)
            if alreadyOpen:
                self.refreshScansList()
                self.changeImageInView(0,0,0,0 , loading = True)
                self.table.setCurrentCell(0,0)

    def scanActionHandler(self):
        pass

    def exitHandler(self):
        if QtGui.QMessageBox.question(None, '', "Are you sure you want to quit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes:
            QtGui.QApplication.quit()

    def createActions(self):

        self.newAct = QtGui.QAction("&New", self, triggered=self.newFileActionHandler)
        self.openAct = QtGui.QAction("&Open", self, triggered=self.openFileActionHandler)
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

        self.normalSizeAct = QtGui.QAction("&Normal Size", self, enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QtGui.QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)
        # tab related menu options

        self.logoutAct = QtGui.QAction("Logout" , self , triggered = self.logout)

    def print_(self):
        # fix it
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

    invalid = False
    sheetName = None
    sheet = None
    welcome = WelcomeDialog()
    welcome.mode = 'Open'
    if False:
        if welcome.exec_() == QtGui.QDialog.Accepted:
            print welcome.mode
            if welcome.mode == 'New':
                newSheet = NewSheetDialog()
                if newSheet.exec_() == QtGui.QDialog.Accepted and newSheet.sheetName is not None and len(newSheet.sheetName):
                    sheetName = newSheet.sheetName
                    data = {
                        'approved': False,
                        'approvalMatrix': 3,
                        'notes': str(sheetName),
                        'project': int(newSheet.project)
                    }
                    print 'If'
                    print newSheet.project
                    # break
                    # make a post request
                    res = libreHTTP(url = '/api/finance/expenseSheet/' , method = 'post' , data= data)
                    # print res
                    sheet = res.json()
                else:
                    print 'Else'
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
    else:

        sheetJSONStr = """{"pk":1,"user":2,"created":"2016-12-02T10:04:34.203000Z","approved":false,"approvalMatrix":3,"approvalStage":1,"dispensed":false,"notes":"first sheet","project":{"pk":3,"title":"proj1","description":"sdas"},"transaction":1,"invoices":[{"pk":1,"user":2,"created":"2016-12-09T06:43:29.158000Z","service":{"pk":1,"created":"2016-11-16T14:12:41.235000Z","name":"Service 1","user":2,"cin":"CIN123","tin":"TIN123","address":{"pk":1,"street":"street1","city":"city1","state":"state1","pincode":201301,"lat":"12","lon":"13"},"mobile":9876543210,"telephone":"9876543210","logo":"gitlab.com","about":"test","doc":null},"amount":123,"currency":"INR","dated":"2001-01-01","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481265809_16_pradeep.yadav_New_Doc_6_1.jpg","sheet":1,"description":"a desc text","approved":false},{"pk":3,"user":72,"created":"2016-12-16T18:12:05.248555Z","service":{"pk":3,"created":"2016-11-16T14:16:38.984000Z","name":"service 2","user":2,"cin":"CIN1234","tin":"CIN1234","address":{"pk":3,"street":"Street 2","city":"City 2","state":"State 2","pincode":201301,"lat":"13","lon":"14"},"mobile":9876543210,"telephone":"123456789","logo":"gitlab.com","about":"another service","doc":null},"amount":1000,"currency":"INR","dated":"2017-01-01","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481911925_25_admin_scan.jpg","sheet":1,"description":"a desc text from python","approved":false},{"pk":4,"user":72,"created":"2016-12-16T18:16:04.244139Z","service":{"pk":1,"created":"2016-11-16T14:12:41.235000Z","name":"Service 1","user":2,"cin":"CIN123","tin":"TIN123","address":{"pk":1,"street":"street1","city":"city1","state":"state1","pincode":201301,"lat":"12","lon":"13"},"mobile":9876543210,"telephone":"9876543210","logo":"gitlab.com","about":"test","doc":null},"amount":1000,"currency":"INR","dated":"2017-01-02","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481912164_24_admin_scan.jpg","sheet":1,"description":"a desc text from python","approved":false}]}"""

        sheet = json.loads(sheetJSONStr)

    print sheet

    window = Window(user = usr , sheet = sheet , name = sheetName , mode = welcome.mode)
    window.show()

    sys.exit(app.exec_())
