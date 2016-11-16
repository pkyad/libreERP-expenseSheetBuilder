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
import json
import requests
import os
import sys
baseFolder = os.path.expanduser('~/.libreerp')
tokenFilePath = os.path.expanduser('~/.libreerp/token.key')


# for r in conf.readlines():
#     val = r.split('=')[1].replace('\n' , '')
#     if r.startswith('proxy'):
#         prx = val
#     elif r.startswith('domain'):
#         domain = val
#
#
# proxies = {
#   'http': prx,
#   'https': prx,
# }

def getConfigs():
    configs = {}
    conf = open(os.path.expanduser('~/.libreerp/config.txt'))
    for r in conf.readlines():
        if r.startswith('#'):
            r = r.replace('#' , '')
            parts = r.split('=')
            configs[parts[0]] = None
            continue
        val = r.split('=')[1].replace('\n' , '')
        if r.startswith('proxy'):
            proxies = {
              'http': val,
              'https': val,
            }
            configs['proxy'] = proxies
        elif r.startswith('domain'):
            configs['domain'] = val
    return configs

configs = getConfigs()

if not os.path.isdir(baseFolder):
    os.mkdir(baseFolder)

class User():
    def __init__(self , usr):
        self.first_name = usr['first_name']
        self.last_name = usr['last_name']
        self.dp = usr['profile']['displayPicture']
    def __repr__(self):
        return ('%s %s' %(self.first_name , self.last_name))

class loginScreen(QtGui.QDialog):
    def __init__(self, parent=None):
        super(loginScreen, self).__init__()

        self.usernameEdit = QtGui.QLineEdit('admin')
        self.passwordEdit = QtGui.QLineEdit('123')
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        loginBtn = QtGui.QPushButton('Login')
        loginBtn.clicked.connect(self.login)

        hbox = QtGui.QHBoxLayout()

        vbox = QtGui.QVBoxLayout()

        loginForm = QtGui.QFormLayout()
        loginForm.addRow(QtGui.QLabel('Username') , self.usernameEdit)
        loginForm.addRow(QtGui.QLabel('Password') , self.passwordEdit)
        loginForm.addRow(loginBtn)
        vbox.setAlignment(QtCore.Qt.AlignCenter)
        vbox.addLayout(loginForm)

        hbox.addStretch(1)
        hbox.addLayout(vbox)

        self.setLayout(hbox)

        self.setWindowTitle("libreRPA - Welcome")
        # self.showMaximized()
        self.setFixedWidth(800)
        self.setFixedHeight(500)
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
        # self.login()

    def login(self):
        uName = self.usernameEdit.text()
        passwrd = self.passwordEdit.text()

        session = requests.Session()
        if configs['proxy'] is None:
            r = session.get( configs['domain'] + '/login/' )
        else:
            r = session.get( configs['domain'] + '/login/' , proxies = configs['proxy'])
        r = session.post( configs['domain'] + '/login/' , {'username' : str(uName) ,'password': str(passwrd), 'csrfmiddlewaretoken': session.cookies['csrftoken'] })
        print r.text

        if r.status_code == 200:
            sessionID = session.cookies['sessionid']
            csrfToken = session.cookies['csrftoken']
            f = open(tokenFilePath , 'w')
            f.writelines([ 'session=' + sessionID + '\n' , 'csrf=' + csrfToken])
            f.close()
            print 'completed writing the tokens to the file'
            r = session.get( configs['domain'] + '/api/HR/users/?mode=mySelf')
            urs = r.json()
            self.user = User(urs[0])
            print self.user
            self.accept()
        else:
            print 'error loging in'
            print r.status_code
            print r.text

def openLoginDialog():

    app = QtGui.QApplication(sys.argv)
    welcomeScreen = loginScreen()
    if welcomeScreen.exec_() == QtGui.QDialog.Accepted:
        return welcomeScreen

def getCookiedSession():
    session = requests.Session()
    try:
        f = open(tokenFilePath , 'r')
    except:
        openLoginDialog()
        f = open(tokenFilePath , 'r')
    for r in f.readlines():
        if r.startswith('csrf='):
            csrfToken = r.replace('csrf=' , '').replace('\n' , '')
        if r.startswith('session='):
            sessionID = r.replace('session=' , '').replace('\n' , '')
    session.cookies.update({'sessionid' : sessionID})
    session.cookies.update({'csrftoken' : csrfToken})
    return session

def getLibreUser():
    mySelfLink = configs['domain'] + '/api/HR/users/?mode=mySelf&format=json'
    if os.path.isfile(tokenFilePath):
        try:
            session = getCookiedSession()
        except:
            print 'error getting the existing tokens, opening the login dialog window'
            openLoginDialog()
            session = getCookiedSession()
        r = session.get( mySelfLink, proxies = configs['proxy'])
        if r.status_code != 200:
            print 'existing tokens incorrect'
            openLoginDialog()
            session = getCookiedSession()
            r = session.get(mySelfLink , proxies = configs['proxy'])

    else:
        print 'token file missing , will show login window now'
        openLoginDialog()
        session = getCookiedSession()
        r = session.get(mySelfLink , proxies = configs['proxy'])

    urs = r.json()
    user = User(urs[0])
    return user

def libreHTTP(url ,method = 'get'):
    ses = getCookiedSession()
    configs = getConfigs()
    r = ses.get( configs['domain'] + url , proxies = configs['proxy'])
    if r.status_code!= 200:
        getLibreUser()
        libreHTTP(url = url , method = method)
    return r

if __name__ == '__main__':
    getLibreUser()
