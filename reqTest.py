from libreerp.ui import libreHTTP , getLibreUser

u = getLibreUser()
print u

d = {
    'service' : 1,
    'amount' : 1000,
    'currency' : 'INR',
    'dated' : '2017-01-02',
    'sheet' : 1,
    'description' : 'a desc text from python'

}

files = {'attachment': open('scan.jpg', 'rb')}

res = libreHTTP(url = '/api/finance/invoice/' , method = 'post' , data = d , files = files )

print res.text
