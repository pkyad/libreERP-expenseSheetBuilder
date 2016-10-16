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

from PyQt4 import QtCore, QtGui, QtOpenGL

def getLogoLabel():
    logoLabel = QtGui.QLabel()
    logoLabel.setFixedWidth(200)
    image = QtGui.QImage('libreERP-logo-cropped.png')
    myPixmap = QtGui.QPixmap.fromImage(image)
    myScaledPixmap = myPixmap.scaled(logoLabel.size(), QtCore.Qt.KeepAspectRatio)
    logoLabel.setPixmap(myScaledPixmap)
    return logoLabel

class aboutDetailsDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(aboutDetailsDialog, self).__init__(parent)
        self.setWindowTitle('About')
        self.logoLabel = getLogoLabel()

        aboutTextLabel = QtGui.QLabel(" (c) 2016 Pradeep Kumar Yadav\n\ne-mail: pkyisky@gmail.com \n\n License : GPL2")
        aboutTextLabel.setFixedWidth(500)

        desclaimerTextLabel = QtGui.QLabel("This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; version 2 of the License. \n\nThis program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. \n\nYou should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.")

        desclaimerTextLabel.setFixedWidth(500)
        desclaimerTextLabel.setWordWrap(True)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(self.logoLabel, 0, 0)
        mainLayout.addWidget(aboutTextLabel, 0, 1)
        mainLayout.addWidget(desclaimerTextLabel, 1, 1)
        mainLayout.addWidget(buttonBox, 2, 1)
        self.setLayout(mainLayout)

        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
