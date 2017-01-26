#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2017 Pradeep Kumar Yadav.
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
import json
from libreerp.ui import libreHTTP
from PyQt4 import QtCore, QtGui
from datetime import datetime
import pytz
from reportBuild import buildPDF

class resultDialog(QtGui.QDialog):
    def __init__(self, parent , data , usr):
        super(resultDialog, self).__init__(parent)
        self.usr = usr
        self.data = data
        self.setWindowTitle('Review and submit')

        buttonBox = QtGui.QWidget()
        buttonBoxLayout = QtGui.QGridLayout()
        backBtn = QtGui.QPushButton('Cancel')
        printBtn = QtGui.QPushButton('Print')
        saveBtn = QtGui.QPushButton('Save')
        submitBtn = QtGui.QPushButton('Submit')

        backBtn.setFixedWidth(70)
        printBtn.setFixedWidth(55)
        saveBtn.setFixedWidth(70)
        submitBtn.setFixedWidth(80)


        backBtn.clicked.connect(self.reject)
        printBtn.clicked.connect(self._print)
        saveBtn.clicked.connect(self.save)
        submitBtn.clicked.connect(self.submit)

        reportLbl = QtGui.QLabel('Report')
        reportLbl.setFixedWidth(50)

        buttonBoxLayout.addWidget(QtGui.QLabel(),0,0)
        buttonBoxLayout.addWidget(backBtn,0,1)
        buttonBoxLayout.addWidget(submitBtn,0,2)
        buttonBoxLayout.addWidget(reportLbl,0,3)
        # buttonBoxLayout.addWidget(printBtn,0,4)
        buttonBoxLayout.addWidget(saveBtn,0,4)
        buttonBoxLayout.setMargin(0)

        buttonBox.setLayout(buttonBoxLayout)


        self.table = QtGui.QTableWidget()
        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels(QtCore.QString("Page;Vendor Name;Amount;Dated;Description").split(";"))
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().hide()
        self.table.setColumnWidth(0,50)
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.table.setRowCount(len(self.data['invoices']))
        self.resize(700,300)

        for i, r in enumerate(self.data['invoices']):
            self.table.setItem(i,0, QtGui.QTableWidgetItem(str(i)))
            self.table.setItem(i,1, QtGui.QTableWidgetItem(str(r['service']['name'])))
            self.table.setItem(i,2, QtGui.QTableWidgetItem(str(r['amount'])))
            self.table.setItem(i,3, QtGui.QTableWidgetItem(str(r['dated'])))
            self.table.setItem(i,4, QtGui.QTableWidgetItem(str(r['description'])))

        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.table , 0, 0)
        mainLayout.addWidget(buttonBox, 1, 0, 1, 1)
        self.setLayout(mainLayout)
    def export(self):
        wb = Workbook()
        ws = wb.active
        ws.append(['Page', 'Name', 'Value'])
        for r in self.data:
            ws.append([r['page'] , r['name'] , r['value']])
        fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        wb.save(str(fileName))

    def _print(self):
        pass

    def save(self):
        filePath = QtGui.QFileDialog.getSaveFileName(self , 'Save consolidated report',QtCore.QDir.homePath(), selectedFilter='*.pdf')
        if filePath:
            filePath = str(filePath)
            if not filePath.endswith('.pdf'):
                filePath += '.pdf'

            buildPDF(filePath , self.data, self.usr)
    def submit(self):
        libreHTTP(method = 'patch' , url = '/api/finance/expenseSheet/%s/'%(self.data['pk']), data = {'submitted': True})


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)

    sheetJSONStr = """{"pk":1,"user":2,"created":"2016-12-02T10:04:34.203000Z","approved":false,"approvalMatrix":3,"approvalStage":1,"dispensed":false,"notes":"first sheet","project":{"pk":3,"title":"proj1","description":"sdas"},"transaction":1,"invoices":[{"pk":1,"user":2,"created":"2016-12-09T06:43:29.158000Z","service":{"pk":1,"created":"2016-11-16T14:12:41.235000Z","name":"Service 1","user":2,"cin":"CIN123","tin":"TIN123","address":{"pk":1,"street":"street1","city":"city1","state":"state1","pincode":201301,"lat":"12","lon":"13"},"mobile":9876543210,"telephone":"9876543210","logo":"gitlab.com","about":"test","doc":null},"amount":123,"currency":"INR","dated":"2001-01-01","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481265809_16_pradeep.yadav_New_Doc_6_1.jpg","sheet":1,"description":"a desc text","approved":false},{"pk":3,"user":72,"created":"2016-12-16T18:12:05.248555Z","service":{"pk":3,"created":"2016-11-16T14:16:38.984000Z","name":"service 2","user":2,"cin":"CIN1234","tin":"CIN1234","address":{"pk":3,"street":"Street 2","city":"City 2","state":"State 2","pincode":201301,"lat":"13","lon":"14"},"mobile":9876543210,"telephone":"123456789","logo":"gitlab.com","about":"another service","doc":null},"amount":1000,"currency":"INR","dated":"2017-01-01","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481911925_25_admin_scan.jpg","sheet":1,"description":"a desc text from python","approved":false},{"pk":4,"user":72,"created":"2016-12-16T18:16:04.244139Z","service":{"pk":1,"created":"2016-11-16T14:12:41.235000Z","name":"Service 1","user":2,"cin":"CIN123","tin":"TIN123","address":{"pk":1,"street":"street1","city":"city1","state":"state1","pincode":201301,"lat":"12","lon":"13"},"mobile":9876543210,"telephone":"9876543210","logo":"gitlab.com","about":"test","doc":null},"amount":1000,"currency":"INR","dated":"2017-01-02","attachment":"http://127.0.0.1:8000/media/finance/invoices/1481912164_24_admin_scan.jpg","sheet":1,"description":"a desc text from python","approved":false}]}"""

    sheet = json.loads(sheetJSONStr)
    from libreerp.ui import getLibreUser

    usr = getLibreUser()
    screen = resultDialog(None , sheet, usr)
    if screen.exec_() == QtGui.QDialog.Accepted:
        sys.exit()
    sys.exit()
