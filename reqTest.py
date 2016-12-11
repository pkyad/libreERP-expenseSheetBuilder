from libreerp.ui import libreHTTP , getLibreUser

u = getLibreUser()
print u

d = {
    'user' : 3,
    'service' : 1,
    'amount' : 000,
    'currency' : 'INR',
    'dated' : '2017-01-01',
    'sheet' : 2,

}

files = {'attachment': open('scan.jpg', 'rb')}

res = libreHTTP(url = '/api/finance/invoice/' , method = 'post' , data = d , files = files )

print res.text
