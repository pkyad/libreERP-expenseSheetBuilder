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
import datetime
from PyQt4 import QtCore, QtGui
from libreerp.ui import getCookiedSession , getConfigs , libreHTTP
import pytz

class searchSheetDialog(QtGui.QDialog):
    def __init__(self, parent = None):
        super(searchSheetDialog, self).__init__(parent)
        self.results = []
        self.setWindowTitle('Search expense sheets')

        self.mainWidget = QtGui.QWidget()

        self.searchEdit = QtGui.QLineEdit()
        self.searchEdit.setPlaceholderText('Search for name / description')
        self.searchEdit.returnPressed.connect(self.handleSearch)

        self.searchInputGb = QtGui.QGroupBox('')
        self.searchInputGbLayout = QtGui.QGridLayout()
        self.searchInputGbLayout.setMargin(0)

        self.cal = QtGui.QCalendarWidget()
        self.cal.setGridVisible(True)
        self.cal.clicked[QtCore.QDate].connect(self.searchDateSelected)
        self.cal.setVerticalHeaderFormat(QtGui.QCalendarWidget.NoVerticalHeader)
        # self.cal.setSelectionMode(QtGui.QCalendarWidget.NoSelection)

        self.selectedDateLbl = QtGui.QLabel('No date selected')


        self.searchBtn = QtGui.QPushButton('Search')
        self.searchBtn.clicked.connect(self.handleSearch)
        self.searchBtn.setFixedWidth(60)

        helpLbl = QtGui.QLabel('Search with just the name / description or with the date combination to narrow down the results.')
        helpLbl.setWordWrap(True)


        self.searchInputGbLayout.addWidget(self.searchEdit ,0,0)
        self.searchInputGbLayout.addWidget(helpLbl ,1,0)
        self.searchInputGbLayout.addWidget(self.cal ,2,0)
        self.searchInputGbLayout.addWidget(self.selectedDateLbl ,3,0)
        self.searchInputGbLayout.addWidget(self.searchBtn ,4,0)

        self.searchInputGb.setLayout(self.searchInputGbLayout)
        self.searchInputGb.setFixedWidth(300)

        self.resultGb = QtGui.QGroupBox('')
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
        self.layout.addWidget(self.searchInputGb , 0, 0)
        # self.layout.addWidget(self.searchBtn , 0, 1)
        self.layout.addWidget(self.resultGb , 0, 1)
        self.layout.addWidget(self.buttonBox , 1, 1, QtCore.Qt.AlignBottom |  QtCore.Qt.AlignRight)

        self.setFixedWidth(800)
        self.setFixedHeight(450)
        self.mainWidget.setLayout(self.layout)

        self.mainLayout = QtGui.QGridLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.addWidget(self.mainWidget , 0, 0, QtCore.Qt.AlignTop)
        self.setLayout(self.mainLayout)

    def searchDateSelected(self, date):
        # self.cal.setSelectionMode(QtGui.QCalendarWidget.SingleSelection)
        self.selectedDateLbl.setText('Selected : %s' %  date.toString('dd-MMM-yyyy'))

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
        params = {'notes__contains' : str(self.searchEdit.text()),
            'created' : str(self.cal.selectedDate().toString('dd-MM-yyyy'))}
        r = libreHTTP('/api/finance/expenseSheet/', params=params)
        self.results = r.json()

        utc=pytz.UTC
        vendors = []
        for v in self.results:
            d = datetime.datetime.strptime(v['created'], '%Y-%m-%dT%H:%M:%S.%fZ')
            d = d.replace(tzinfo=utc)
            vendors.append({'notes' : v['notes'] , 'ID' : v['pk'] , 'project': v['project'], 'created' : d})

        print d
        print dir(d)


        if len(vendors)==0:
            return

        self.resultGb.deleteLater()
        self.resultGb = None

        self.resultGb = QtGui.QGroupBox('')

        self.resultGbLayout = QtGui.QGridLayout()
        self.resultGbLayout.setMargin(0)


        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(QtCore.QString(";Notes;ID;Project;Created").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0,20)
        self.table.setColumnWidth(1,200)
        self.table.setColumnWidth(2,50)
        self.table.setColumnWidth(3,90)
        self.table.setFixedHeight(370)


        self.table.setRowCount(len(vendors))

        self.radioBtnArray = []
        for v in vendors:
            i = vendors.index(v)
            self.radioBtnArray.append(QtGui.QRadioButton())
            self.table.setCellWidget(i,0, self.radioBtnArray[i])
            self.table.setItem(i,1, QtGui.QTableWidgetItem(str(v['notes'])))
            self.table.setItem(i,2, QtGui.QTableWidgetItem(str(v['ID'])))
            self.table.setItem(i,3, QtGui.QTableWidgetItem(str(v['project'])))
            self.table.setItem(i,4, QtGui.QTableWidgetItem(str(v['created'])))

        self.resultGbLayout.addWidget(self.table)
        self.resultGb.setLayout(self.resultGbLayout)
        self.layout.addWidget(self.resultGb , 0, 1)


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    screen = searchSheetDialog()
    if screen.exec_() == QtGui.QDialog.Accepted:
        print screen.selectedValue
        sys.exit()
    sys.exit()
