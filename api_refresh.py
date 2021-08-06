#Input values
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
DX_VDB_NAME=sys.argv[4]
BASEURL='http://' + str(DX_ENGINE) + '/resources/json/delphix'



#Python modules
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



r = session.get(BASEURL+'/database', data=formdata, headers=req_headers, allow_redirects=False)
k = json.loads(r.text)

#Get vDB reference
for dbobj in k['result']:
    if DX_VDB_NAME == dbobj['name']:
        DX_VDB_REF = dbobj['reference']
        DX_VDB_REF_PARENT = dbobj['provisionContainer']
#print (DX_VDB_NAME)
#print (DX_VDB_REF)
#print (DX_VDB_REF_PARENT)
#
#Refresh a vDB
#
formdata = '{ "type": "OracleRefreshParameters", "timeflowPointParameters": { "type": "TimeflowPointSemantic", "container": "' + DX_VDB_REF_PARENT + '" } }'
r = session.post(BASEURL+'/database/' + DX_VDB_REF + '/refresh', data=formdata, headers=req_headers, allow_redirects=False)

print ('------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
