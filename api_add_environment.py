DMUSER='admin'
DMPASS='delphix'
DELAYTIMESEC=10
BASEURL='http://172.16.126.156/resources/json/delphix'
DX_ENV_NAME='singlenode_stby'
DX_ENV_IP='172.16.126.129'
DX_NFS_ENV_IP='172.16.126.129'


import requests
import json

#
# Request Headers ...
#
req_headers = {
   'Content-Type': 'application/json'
}

#
# Python session, also handles the cookies ...
#
session = requests.session()

#
# Create session ...
#
formdata = '{ "type": "APISession", "version": { "type": "APIVersion", "major": 1, "minor": 10, "micro": 0 } }'
r = session.post(BASEURL+'/session', data=formdata, headers=req_headers, allow_redirects=False)

#
# Login ...
#
formdata = '{ "type": "LoginRequest", "username": "' + DMUSER + '", "password": "' + DMPASS + '" }'
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False)

#
# Get system details ...
#
r = session.get(BASEURL+'/database', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
j = json.loads(r.text)

r = session.get(BASEURL+'/environment', data=formdata, headers=req_headers, allow_redirects=False)
print (r.text)
#
#Print all Environments
#
j = json.loads(r.text)
print ('List of Environments:')
for dbobj in j['result']:
	print (dbobj['name'])

#
#Add an environment
#
formdata = '{ "type": "HostEnvironmentCreateParameters", "primaryUser": { "type": "EnvironmentUser", "name": "" , "credential": { "type": "KerberosCredential" } }, "hostEnvironment": { "type": "UnixHostEnvironment", "name" : "' + DX_ENV_NAME + '" }, "hostParameters": { "type": "UnixHostCreateParameters" , "host": { "type": "UnixHost", "address": "' + DX_ENV_IP + '" , "nfsAddressList ": [ "' + DX_NFS_ENV_IP + '" ] , "toolkitPath": "/home/delphix" } } }'
r = session.post(BASEURL+'/environment', data=formdata, headers=req_headers, allow_redirects=False)
print (r.text)



print ('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')


