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

from PyQt4 import QtCore, QtGui

class searchVendorDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(searchVendorDialog, self).__init__(parent)
        self.setWindowTitle('Search vendor')

        self.mainWidget = QtGui.QWidget()

        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.setPlaceholderText('Search for vendor using name')
        self.searchEdit.textChanged.connect(self.handleSearch)

        # self.searchBtn = QtGui.QPushButton('Search')
        # self.searchBtn.clicked.connect(self.handleSearch)
        # self.searchBtn.setFixedWidth(60)

        self.resultGb = QtGui.QGroupBox('Suggestions')
        self.resultGbLayout = QtGui.QGridLayout()
        noResultLabel = QtGui.QLabel('No results')
        noResultLabel.setFixedHeight(370)

        self.resultGbLayout.addWidget(noResultLabel)

        self.resultGb.setLayout(self.resultGbLayout)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)


        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.searchEdit , 0, 0)
        # self.layout.addWidget(self.searchBtn , 0, 1)
        self.layout.addWidget(self.resultGb , 1, 0)
        self.layout.addWidget(self.buttonBox , 2, 0, QtCore.Qt.AlignBottom)

        self.setFixedWidth(800)
        self.setFixedHeight(500)
        self.mainWidget.setLayout(self.layout)

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.addWidget(self.mainWidget , 0, 0, QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)


    def handleSearch(self):

        self.resultGb.deleteLater()
        self.resultGb = None

        self.resultGb = QtGui.QGroupBox('Suggestions')


        self.resultGbLayout = QtGui.QGridLayout()

        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(QtCore.QString(";Name;ID;Address").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0,16)
        self.table.setColumnWidth(1,230)
        self.table.setColumnWidth(2,120)
        self.table.setFixedHeight(370)

        vendors = [
            {'name' : 'name 1' , 'pk' : 2 ,  'address' : 'an address'},
            {'name' : 'name 2' , 'pk' : 3 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 4 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 5 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 7 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 8 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 9 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 40 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 47,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 42 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 48 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 41 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 24 ,  'address' : 'an address'},
            {'name' : 'name 3' , 'pk' : 44 ,  'address' : 'an address'}
        ]

        self.table.setRowCount(len(vendors))

        self.radioBtnArray = []
        for v in vendors:
            i = vendors.index(v)
            self.radioBtnArray.append(QtGui.QRadioButton())
            self.table.setCellWidget(i,0, self.radioBtnArray[i])
            self.table.setItem(i,1, QtGui.QTableWidgetItem(str(v['name'])))
            self.table.setItem(i,2, QtGui.QTableWidgetItem(str(v['pk'])))
            self.table.setItem(i,3, QtGui.QTableWidgetItem(str(v['address'])))



        self.resultGbLayout.addWidget(self.table)
        self.resultGb.setLayout(self.resultGbLayout)
        self.layout.addWidget(self.resultGb , 1, 0)


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    screen = searchVendorDialog()
    if screen.exec_() == QtGui.QDialog.Accepted:
        sys.exit()
    sys.exit()
