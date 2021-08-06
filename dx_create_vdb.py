#================================================================================
# File:         dx_create_vdb.py
# Type:         python script
# Date:         07-June 2019
# Author:       v1- Carlos Cuellar - Delphix Professional Services
# Ownership:    This script is owned and maintained by the user, not by Delphix
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Copyright (c) 2019 by Delphix. All rights reserved.
#
# Description:
#
#       Script to stop all Oracle and MS SQL Server vDBs from a Delphix Engine
#
#Prerequisites:
#
#       Need to have python installed
#
#Usage:
#
#       python dx_stop_all_vdbs.py
#
#================================================================================
#
#Please update the following variables with your Delphix Admin credentials and Delphix Engine URL
DMUSER='admin'
DMPASS='delphix'
BASEURL='http://172.16.126.180/resources/json/delphix'


import requests
import json
import time


print ('Starting script to shut down all vDBs in engine ...')

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
# Get database reference for timeflow
#

contname="maskcontaner1"
tmplname="JS_DATA_TEMPLATE-41"
contref="ORACLE_DB_CONTAINER-104"
sourceref="ORACLE_DB_CONTAINER-61"
userref="USER-52"


formdata = {
"container": {
"group": "GROUP-3",
"name": "MASKVDB1",
"type": "OracleDatabaseContainer"
},
"source": {
"type": "OracleVirtualSource",
"mountBase": "/mnt/provision",
"config": "ORACLE_SINGLE_CONFIG-1",
"allowAutoVDBRestartOnHostReboot": True
},
"sourceConfig": {
"type": "OracleSIConfig",
"databaseName": "MASKVDB1",
"uniqueName": "MASKVDB1_x039db06",
"repository": "ORACLE_INSTALL-2",
"instance": {
"type": "OracleInstance",
"instanceName": "MASKVDB1",
"instanceNumber": 1
}
},
"timeflowPointParameters": {
"type": "TimeflowPointSemantic",
"container": "ORACLE_DB_CONTAINER-1"
},
"type": "OracleProvisionParameters"
}

print (formdata)

r = session.post(BASEURL+'/database/provision', data=json.dumps(formdata), headers=req_headers, allow_redirects=False)
print (r.text)
