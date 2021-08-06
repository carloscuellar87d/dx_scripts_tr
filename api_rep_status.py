#================================================================================
# File:         api_rep_status.py
# Type:         python script
# Date:         19-March 2020
# Author:       Carlos Cuellar
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
#       Script to check last completed replication status
#
# Prerequisites:
#   Python 2/3 installed
#
#
# Usage
#   python api_rep_status.py <DELPHIX USER> <DELPHIX USER PASSWORD> <DELPHIX ENGINE> <DELPHIX REPLICATION>
#
#
# Example
#   python api_rep_status.py admin delphix delphixengine replication_profile
#================================================================================
#
import sys
import requests
import json
import time
import os

##print datetime_api
#Variables/Parameters
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
DX_REP=sys.argv[4]
BASEURL='http://' + DX_ENGINE + '/resources/json/delphix'
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
# Get Delphix Database and Action data ... Please note that we are passing some clauses to action to only look for actions run in the last 5 mins and that contain the keyword "settings"
#
repspec = session.get(BASEURL+'/replication/spec', headers=req_headers, allow_redirects=False)
sourcestate = session.get(BASEURL+'/replication/sourcestate', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
repsepc_j = json.loads(repspec.text)
sourcestate_j = json.loads(sourcestate.text)


for dbobj in repsepc_j['result']:
    repspecname = dbobj['name']
    if repspecname == DX_REP:
        repspecref = dbobj['reference']



for dbobj in sourcestate_j['result']:
      repspecn2 = dbobj['spec']
      if repspecn2 == repspecref:
        repstaref = dbobj['reference']
#print (repstaref)

sourcestate_2 = session.get(BASEURL+'/replication/sourcestate/'+repstaref, headers=req_headers, allow_redirects=False)
#
# JSON Parsing ...
#
sourcestate_2_j = json.loads(sourcestate_2.text)

repserpoint = sourcestate_2_j['result']['lastPoint']

#
serialpointapi = session.get(BASEURL+'/replication/serializationpoint/'+repserpoint, headers=req_headers, allow_redirects=False)
#
# JSON Parsing ...
#
serialpointapi_j = json.loads(serialpointapi.text)
spj = serialpointapi_j['result']
serialpointapi_fin = json.dumps(serialpointapi.json(), indent=4)
print ('Last Completed Replication status:')
print (serialpointapi_fin)
