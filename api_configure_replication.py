#================================================================================
# File:         api_start_replication.py
# Type:         python script
# Date:         03-June 2020
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
#   python api_start_replication.py <DELPHIX USER> <DELPHIX USER PASSWORD> <DELPHIX ENGINE> <DELPHIX REPLICATION>
#
#
# Example
#   python api_start_replication.py admin delphix delphixengine replication_profile
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
#print (r.text)
#
# Login ...
#
formdata = '{ "type": "LoginRequest", "username": "' + DMUSER + '", "password": "' + DMPASS + '" }'
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False)
#print (r.text)
#
# Get Delphix Database and Action data ... Please note that we are passing some clauses to action to only look for actions run in the last 5 mins and that contain the keyword "settings"
#
repspec = session.get(BASEURL+'/replication/spec', headers=req_headers, allow_redirects=False)

#
# JSON Parsing ...
#
repsepc_j = json.loads(repspec.text)


for dbobj in repsepc_j['result']:
    repspecname = dbobj['name']
    if repspecname == DX_REP:
        repspecref = dbobj['reference']

print ('Starting Delphix Replication script...')
#
#   Starting replication process
#
start_replication = session.post(BASEURL+'/replication/spec/'+repspecref+'/execute', headers=req_headers, allow_redirects=False)
#
# JSON Parsing ...
#
#print(start_replication.text)
start_replicationjs = json.loads(start_replication.text)
##print (refreshcontainer.text)
print ("Waiting for 5 seconds.")
time.sleep (5)
replica_job = start_replicationjs['job']
#Get Delphix Self Service Bookmark details
#
rjob = session.get(BASEURL+'/job/'+ replica_job, headers=req_headers, allow_redirects=False, verify=False)
#
# JSON Parsing ...
#
rjobj = json.loads(rjob.text)
#
reset_created = 0
res_time = 1
print ("Monitoring Job progress (Up to 4 hrs and 10 mins).")
while reset_created == 0:
    if res_time < 1000:
        JOB_STATUS = rjobj['result']['jobState']
        if JOB_STATUS == "COMPLETED":
            reset_created = 1
        elif JOB_STATUS == "FAILED":
            sys.exit("Replication job failed. Please check Delphix logs.")
        else:
            JOB_PERCENTAGE = str(rjobj['result']['percentComplete'])
            print ( 'Reset operation  progress at ' + JOB_PERCENTAGE + '%')
            time.sleep(15)
            res_time += 1
            rjob = session.get(BASEURL+'/job/'+ replica_job, headers=req_headers, allow_redirects=False, verify=False)
            rjobj = json.loads(rjob.text)
    else:
        reset_created = 2
        sys.exit("Replication job could not complete in 15000 seconds- 250 mins - 4 hrs 10 mins . ")
print ('Replication of ' + DX_REP  + ' from Delphix engine ' + DX_ENGINE + ' completed!')
sys.exit(0)
