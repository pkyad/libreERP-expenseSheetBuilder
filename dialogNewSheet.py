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
from libreerp.ui import getCookiedSession , getConfigs , libreHTTP



class NewSheetDialog(QtGui.QDialog):
    def __init__(self, parent = None , full = False , sheet = None):
        super(NewSheetDialog, self).__init__(parent)
        self.setWindowTitle('Create new sheet')
        self.setFixedWidth(500)
        # self.setFixedHeight(500)
        lbl = QtGui.QLabel('Name')
        self.results = []
        self.mode = 'new'
        self.radioBtnArray = []
        self.nameEdit = QtGui.QLineEdit()
        if sheet is not None:
            self.mode = 'edit'
            self.nameEdit.setText(sheet['notes'])
            projectLabel = QtGui.QLabel(QtCore.QString('<span style=" font-size:8pt; font-weight:600; color:black;">Title : </span>' + sheet['project']['title'] + '<br/><span style=" font-size:8pt; font-weight:600; color:black;"> ID : </span>' + str(sheet['project']['pk'])))

        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.setPlaceholderText('Search for Project using name')
        self.searchEdit.returnPressed.connect(self.handleSearch)
        self.resultGb = QtGui.QGroupBox('')
        self.resultGbLayout = QtGui.QGridLayout()
        noResultLabel = QtGui.QLabel('No results')
        noResultLabel.setFixedHeight(370)

        self.resultGbLayout.addWidget(noResultLabel, 0,0 , QtCore.Qt.AlignTop)
        self.resultGb.setLayout(self.resultGbLayout)

        self.okayBtn = QtGui.QPushButton('Ok')
        self.okayBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.okayBtn.setFixedWidth(70)
        self.cancelBtn = QtGui.QPushButton('Cancel')
        self.cancelBtn.setFocusPolicy(QtCore.Qt.NoFocus)
        self.cancelBtn.setFixedWidth(70)

        self.okayBtn.clicked.connect(self.okayHandler)
        self.cancelBtn.clicked.connect(self.cancelHandler)

        self.buttonBox = QtGui.QWidget()
        self.buttonBoxLayout = QtGui.QGridLayout()
        self.buttonBoxLayout.addWidget(self.okayBtn , 0,0 , QtCore.Qt.AlignRight)
        self.buttonBoxLayout.addWidget(self.cancelBtn , 0,1)
        self.buttonBoxLayout.setMargin(0)
        self.buttonBox.setLayout(self.buttonBoxLayout)

        self.lyt = QtGui.QGridLayout()
        self.lyt.addWidget(lbl,0,0)
        self.lyt.addWidget(self.nameEdit, 0,1)
        self.lyt.addWidget(QtGui.QLabel('Project'), 1,0)
        self.lyt.addWidget(self.searchEdit , 1, 1)

        if self.mode == 'new':
            ind = 0
        else:
            ind = 1
            self.lyt.addWidget(projectLabel , 2 , 1, 1, 2)
        self.lyt.addWidget(self.resultGb , ind+2, 1 , 1, 2)
        self.lyt.addWidget(self.buttonBox , ind+3, 1)

        self.setLayout(self.lyt)

    def handleSearch(self):

        r = libreHTTP('/api/projects/projectSearch/?title__startswith=' + self.searchEdit.text())
        self.results = r.json()

        self.resultGb.deleteLater()
        self.resultGb = None

        self.resultGb = QtGui.QGroupBox('')

        self.resultGbLayout = QtGui.QGridLayout()
        self.resultGbLayout.setMargin(0)


        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(QtCore.QString(";Name;ID;Description").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0,20)
        self.table.setColumnWidth(1,230)
        self.table.setFixedHeight(370)
        vendors = []
        for v in self.results:
            vendors.append({'title' : v['title'] , 'pk' : v['pk'] , 'description' : v['description']})

        self.table.setRowCount(len(vendors))

        self.radioBtnArray = []
        for v in vendors:
            i = vendors.index(v)
            self.radioBtnArray.append(QtGui.QRadioButton())
            self.table.setCellWidget(i,0, self.radioBtnArray[i])
            self.table.setItem(i,1, QtGui.QTableWidgetItem(str(v['title'])))
            self.table.setItem(i,2, QtGui.QTableWidgetItem(str(v['pk'])))
            self.table.setItem(i,3, QtGui.QTableWidgetItem(str(v['description'])))

        self.resultGbLayout.addWidget(self.table)
        self.resultGb.setLayout(self.resultGbLayout)
        if self.mode == 'edit':
            ind = 1
        else:
            ind = 0
        self.lyt.addWidget(self.resultGb , ind+2, 0, 1, 2)

    def cancelHandler(self):
        self.reject()

    def okayHandler(self):
        self.sheetName = self.nameEdit.text()
        if len(self.results) ==0:
            self.project = None
            self.reject()
        ind = None
        for b in self.radioBtnArray:
            if b.isChecked():
                ind = self.radioBtnArray.index(b)
        if ind is None:
            self.project = None
        else:
            self.project = self.results[ind]
        self.accept()


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    screen = NewSheetDialog()
    if screen.exec_() == QtGui.QDialog.Accepted:
        print screen.sheetName
        sys.exit()
    sys.exit()
