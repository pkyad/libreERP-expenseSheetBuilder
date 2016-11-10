import os
import requests


if not os.path.isdir(os.path.expanduser('~/.libreerp')):
    os.mkdir(os.path.expanduser('~/.libreerp'))

f = open(os.path.expanduser('~/.libreerp/testfile.txt') , 'w')

uName = 'admin'
passwrd = 'indiaerp'

# print uName, passwrd
prx = open(os.path.expanduser('~/.libreerp/proxy.txt')).read()

session = requests.Session()
proxies = {
  'http': prx,
  'https': prx,
}

r = session.get('http://pradeepyadav.net/login/' , proxies = proxies)
r = session.post('http://pradeepyadav.net/login/' , {'username' : str(uName) ,'password': str(passwrd), 'csrfmiddlewaretoken': session.cookies['csrftoken'] })

print r.status_code

print(dir(f))
sessionID = session.cookies['sessionid']
csrfToken = session.cookies['csrftoken']

f.writelines([ 'session=' + sessionID + '\n' , 'csrf=' + csrfToken])
f.close()

print r.status_code
