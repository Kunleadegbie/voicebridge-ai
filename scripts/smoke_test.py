import json, urllib.request
url='http://127.0.0.1:8000/api/v1/text/test'
data=json.dumps({'text':'Someone called me and asked for my OTP. Should I give it to them?','language':'en-NG','session_id':'smoke-test'}).encode()
req=urllib.request.Request(url,data=data,headers={'Content-Type':'application/json'})
print(urllib.request.urlopen(req).read().decode())
