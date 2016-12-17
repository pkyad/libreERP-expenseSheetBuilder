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
    def __init__(self, parent = None):
        super(NewSheetDialog, self).__init__(parent)
        self.setWindowTitle('Create new sheet')
        self.setFixedWidth(500)
        # self.setFixedHeight(500)
        lbl = QtGui.QLabel('Name')
        self.lineEdit = QtGui.QLineEdit()

        lyt = QtGui.QGridLayout()
        lyt.addWidget(lbl,0,0)
        lyt.addWidget(self.lineEdit, 0,1)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)

        self.buttonBox.accepted.connect(self.okayHandler)
        self.buttonBox.rejected.connect(self.cancelHandler)

        lyt.addWidget(self.buttonBox , 1, 1)

        self.setLayout(lyt)

    def cancelHandler(self):
        self.reject()

    def okayHandler(self):
        self.sheetID = self.lineEdit.text()
        self.accept()


if __name__ == '__main__':

    import sys
    app = QtGui.QApplication(sys.argv)
    screen = NewSheetDialog()
    if screen.exec_() == QtGui.QDialog.Accepted:
        print screen.sheetID
        sys.exit()
    sys.exit()
