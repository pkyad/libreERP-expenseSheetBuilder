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
from welcomeScreen import getCookiedSession , getConfigs , libreHTTP


class searchVendorDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(searchVendorDialog, self).__init__(parent)
        self.results = []
        self.setWindowTitle('Search vendor')

        self.mainWidget = QtGui.QWidget()

        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.setPlaceholderText('Search for vendor using name')
        self.searchEdit.returnPressed.connect(self.handleSearch)

        # self.searchBtn = QtGui.QPushButton('Search')
        # self.searchBtn.clicked.connect(self.handleSearch)
        # self.searchBtn.setFixedWidth(60)

        self.resultGb = QtGui.QGroupBox('Suggestions')
        self.resultGbLayout = QtGui.QGridLayout()
        noResultLabel = QtGui.QLabel('No results')
        noResultLabel.setFixedHeight(370)

        self.resultGbLayout.addWidget(noResultLabel)

        self.resultGb.setLayout(self.resultGbLayout)

        self.okayBtn = QtGui.QPushButton('Ok')
        self.okayBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.okayBtn.setFixedWidth(70)
        self.cancelBtn = QtGui.QPushButton('Cancel')
        self.cancelBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelBtn.setFixedWidth(70)

        self.okayBtn.clicked.connect(self.handleOkay)
        self.cancelBtn.clicked.connect(self.reject)

        self.buttonBox = QtGui.QWidget()
        self.buttonBoxLayout = QtGui.QGridLayout()
        self.buttonBoxLayout.addWidget(self.okayBtn , 0,0 , QtCore.Qt.AlignRight)
        self.buttonBoxLayout.addWidget(self.cancelBtn , 0,1, QtCore.Qt.AlignRight)
        self.buttonBoxLayout.setMargin(0)
        self.buttonBox.setLayout(self.buttonBoxLayout)

        self.layout = QtGui.QGridLayout()
        self.layout.addWidget(self.searchEdit , 0, 0)
        # self.layout.addWidget(self.searchBtn , 0, 1)
        self.layout.addWidget(self.resultGb , 1, 0)
        self.layout.addWidget(self.buttonBox , 2, 0, QtCore.Qt.AlignBottom |  QtCore.Qt.AlignRight)

        self.setFixedWidth(800)
        self.setFixedHeight(480)
        self.mainWidget.setLayout(self.layout)

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(self.mainWidget , 0, 0, QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)
    def handleOkay(self):
        if len(self.results) ==0:
            self.reject()
            return
        for b in self.radioBtnArray:
            if b.isChecked():
                ind = self.radioBtnArray.index(b)
                # print ind
                # print self.results[ind]
        self.selectedValue = self.results[ind]
        self.accept()

    def handleSearch(self):

        r = libreHTTP('/api/ERP/service/?name__startswith=' + self.searchEdit.text())
        self.results = r.json()

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
        vendors = []
        for v in self.results:
            add = v['address']
            addStr = add['street'] + '\n' + add['city'] + '\n' + add['state'] + '\n' + str(add['pincode'])
            v['address'] = addStr
            vendors.append({'name' : v['name'] , 'pk' : v['pk'] , 'address' : v['address']})

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
