#================================================================================
# File:         dx_api_create_replication_profile.py
# Type:         python script
# Date:         01-Aug 2021
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
#       Script to create Replication profiles
#
# Prerequisites:
#   Python 2/3 installed
#   This script works on OBJECTS only(dSources and vDBs)
#   This script requires a control file with the list of objects. This control file is called dxrepctl.ctl and needs to be placed in same script location
#
#
# dxrepctl.ctl sample:
#   vDBs1,carlosvdb
#   vDBs1,maskedvdb
#   vDBs,maskedvdb
#
#
# Usage
#   python dx_api_create_replication_profile.py <DELPHIX SOURCE ENGINE USER> <DELPHIX SOURCE ENGINE USER PASSWORD> <DELPHIX SOURCE ENGINE> <DELPHIX REPLICATION PROFILE NAME> <DELPHIX REPLICATION PROFILE TYPE> <DELPHIX TARGET ENGINE USER> <DELPHIX TARGET ENGINE USER PASSWORD>
#
#
# Example
#   python dx_api_create_replication_profile.py admin delphix dlpxcarlos.dlpxdc.co testrep ReplicationSecureList  DLPXTARGET.COM admin delphix
#================================================================================
import sys
import requests
import json
import time


#Input values
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
DX_REP_NAME=sys.argv[4]
DX_REP_TYPE=sys.argv[5]
 ##"ReplicationList" or "ReplicationSecureList" only!
DX_ENGINE_TGT=sys.argv[6]
DX_ENGINE_TGT_USR=sys.argv[7]
DX_ENGINE_TGT_USR_PASSWD=sys.argv[8]
BASEURL='http://' + DX_ENGINE + '/resources/json/delphix'

#Check
if str(DX_REP_TYPE) != "ReplicationList":
    if str(DX_REP_TYPE) != "ReplicationSecureList":
        sys.exit('Specify ReplicationList or ReplicationSecureList as Replication type ONLY! Exiting now...')
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
print('')
print('Starting script to create Delphix replication...')
print('')
#
# Create session ...
#
formdata = '{ "type": "APISession", "version": { "type": "APIVersion", "major": 1, "minor": 10, "micro": 0 } }'
r = session.post(BASEURL+'/session', data=formdata, headers=req_headers, allow_redirects=False, verify=False)
#
# Login ...
#
formdata = '{ "type": "LoginRequest", "username": "' + DMUSER + '", "password": "' + DMPASS + '" }'
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False, verify=False)
authj = json.loads(r.text)
if authj['type'] == "ErrorResult":
    print ('Please provide correct user name and password! Error details: ' + str(authj))
    sys.exit(1)
elif authj['type'] == "OKResult":
    print('Authentication successful!')


#
#  ...
#
num_lines = sum(1 for line in open('dxrepctl.ctl'))
file = open("dxrepctl.ctl", "r")
dx_obj_array = [''] * int(num_lines)
##print (dx_obj_array)
##print (num_lines)
i=0
for line2 in file:
    DX_GROUP,DX_OBJECT_TEMP=line2.split(',')
    DX_OBJECT=DX_OBJECT_TEMP.strip()
    #print (DX_GROUP)
    #print (DX_OBJECT)
    r = session.get(BASEURL+'/group',  headers=req_headers, allow_redirects=False, verify=False)
    dx_list_group = json.loads(r.text)
    for dbobj in dx_list_group['result']:
        ##print (dbobj)
        if dbobj['namespace'] == None:
            if str(dbobj['name']) == str(DX_GROUP):
                ##print (str(dbobj['name']) + ' , ' +str(dbobj['reference']))
                DX_GRP_2=str(dbobj['reference'])
                s = session.get(BASEURL+'/database',  headers=req_headers, allow_redirects=False, verify=False)
                dx_list_db_containers = json.loads(s.text)
                for dbobj2 in dx_list_db_containers['result']:
                    if dbobj2['group'] == str(DX_GRP_2):

                        if dbobj2['name'] == str(DX_OBJECT):
                            ##print (str(dbobj2['name']) + ' , ' +str(dbobj2['reference']))
                            DX_OBJ_REP=str(dbobj2['reference'])
                            DX_OBJ_REP_MSK=str(dbobj2['masked'])
                            dx_obj_array[i]=str(dbobj2['reference'])
                            if DX_REP_TYPE == 'ReplicationSecureList':
                                if str(DX_OBJ_REP_MSK) == "False" :
                                    sys.exit('Found a unMasked vDB for a SDD replication profile!Exiting now...')
                            i=i+1
                            ##print (DX_OBJ_REP_MSK)

file.close


#Create OBJ array to add to Replication profile
##print (dx_obj_array)
k=1
DXOBTEMP_ARRAY=' "' + dx_obj_array[0] + '" ,'
while k < num_lines:
    ##print (k)
    DXOBTEMP_ARRAY= DXOBTEMP_ARRAY + ' "' + dx_obj_array[k] + '" ,'
    k = k + 1
##print (DXOBTEMP_ARRAY)
DXOBTEMP_ARRAY = DXOBTEMP_ARRAY[:-2]
print ('Objects to be added to replication profile are: ' + str(DXOBTEMP_ARRAY))
##[ "MSSQL_DB_CONTAINER-54", "MSSQL_DB_CONTAINER-57", "MSSQL_DB_CONTAINER-25" ]



##=== POST /resources/json/delphix/replication/spec ===
#Build up API payload to create replication profile
if DX_REP_TYPE == 'ReplicationList' :
    formdata= '{ "type": "ReplicationSpec", "name": "'+ DX_REP_NAME + '", "targetHost": "' + DX_ENGINE_TGT +'", "targetPrincipal": "' + DX_ENGINE_TGT_USR +'", "targetCredential": { "type": "PasswordCredential", "password": "' + DX_ENGINE_TGT_USR_PASSWD +'" }, "objectSpecification": { "type": "' + DX_REP_TYPE + '", "objects": [ ' + DXOBTEMP_ARRAY + ' ] } }'
elif DX_REP_TYPE == 'ReplicationSecureList' :
    formdata= '{ "type": "ReplicationSpec", "name": "'+ DX_REP_NAME + '", "targetHost": "' + DX_ENGINE_TGT +'", "targetPrincipal": "' + DX_ENGINE_TGT_USR +'", "targetCredential": { "type": "PasswordCredential", "password": "' + DX_ENGINE_TGT_USR_PASSWD +'" }, "objectSpecification": { "type": "' + DX_REP_TYPE + '", "containers": [ ' + DXOBTEMP_ARRAY + ' ] } }'


##print(formdata)
#Create replication profile
r = session.post(BASEURL+'/replication/spec',  data=formdata, headers=req_headers, allow_redirects=False, verify=False)
result = json.loads(r.text)
if str(result['status']) == "OK":
    print('Replication profile was created successfully!')
    sys.exit(0)
else:
    print(result['error'])
    sys.exit('Replication profile was NOT created successfully. Exiting now...')
