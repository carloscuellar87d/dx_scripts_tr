#================================================================================
# File:         dx_api_upl_map_alg.py
# Type:         python script
# Date:         September 16th 2020
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
# Copyright (c) 2020 by Delphix. All rights reserved.
#
# Description:
#
#       Script to be used to kick off replication profiles where a vDB is part of and then monitor its status.
#
# Prerequisites:
#   Python 2/3 installed
#   Requests, json, time, os, socker, urllib3 python modules should be installed
#
# Usage
#   python dlpx_api_upl_map_alg.py <DELPHIX_MASKING_USER> <DELPHIX_MASKING_USER_PASSWORD> <DELPHIX_MASKING_HOSTNAME> <MAPPLETS_LOCATION> <BINARY_LOOKUPS_LOCATION>
#
#
# Example
#   python dlpx_api_upl_map_alg.py admin Admin-12 carlosmskbrd.dlpxdc.co "/Users/carlos.cuellar/Documents/Scripts_Delphix/NEW_MAPPLETS" "/Users/carlos.cuellar/Documents/Scripts_Delphix/NEW_BIN_LOOKUPS"
#================================================================================
#
#Libraries
import sys
import requests
import json
import time
import os
import socket
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from os import listdir
from os.path import isfile, join

#Input Values
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
DX_NEW_MAPPS=sys.argv[4]
DX_NEW_BIN_LOOKUPS=sys.argv[5]

#Variables
BASEURL='http://' + DX_ENGINE + '/masking/api'
a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Starting script
print ("*******************************************************************************************")
print ("Starting Delphix Masking script...")
print ("Connecting to " + DX_ENGINE)
#
#Validate if mapplets/binary lookups paths exist
#
CHK_MAPPS=os.path.isdir(DX_NEW_MAPPS)
CHK_BINLOOKUP=os.path.isdir(DX_NEW_BIN_LOOKUPS)
#
if CHK_MAPPS is False:
    sys.exit ('Directory ' + DX_NEW_MAPPS + ' does not exist!')
#
if CHK_BINLOOKUP is False:
    sys.exit ('Directory ' + DX_NEW_BIN_LOOKUPS + ' does not exist!')
#
# Check if port 80 is open, otherwise we will use 443
#
DX_ENGINE_PORT = (DX_ENGINE, 80)
result_of_check = a_socket.connect_ex(DX_ENGINE_PORT)

print ("Checking which API port is open...")
if result_of_check == 0:
   print("Port 80 is open")
else:
   print("Port 80 is not open. Switching to 443.")
   BASEURL='https://' + DX_ENGINE + '/masking/api'
a_socket.close()
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
# Login ...
#
formdata = '{ "type": "LoginRequest", "username": "' + DMUSER + '", "password": "' + DMPASS + '" }'
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False, verify=False )
#print (r.text)

#
# JSON Parsing and store Authorization key...
#
j = json.loads(r.text)
authapi = j['Authorization']

#
# Update Request Headers  with authorization key...
#
req_headers = {
   'Content-Type': 'application/json',
   'Authorization':  authapi
}


print ("*******************************************************************************************")
print ("Looking for Mapplet JSON list file...")
files_list = [ ]
onlyfiles_map_count = 0
onlyfiles_map_list_count = 0
onlyfiles_map = [f for f in listdir(DX_NEW_MAPPS) if isfile(join(DX_NEW_MAPPS, f))]
for j in onlyfiles_map:
    #print (j)
    if str(j) == 'mapplets_list.json':
        onlyfiles_map_count = 1
        print ("Mapplet JSON list file exists! --> mapplets_list.json")
        with open(DX_NEW_MAPPS+'/mapplets_list.json', 'r') as myfile:
            data=myfile.read()
        # parse file
        obj = json.loads(data)
        onlyfiles_map_list = [f for f in listdir(DX_NEW_MAPPS) if isfile(join(DX_NEW_MAPPS, f))]
        for k in onlyfiles_map_list:
            for l in obj['DelphixCustAlg']:
                if str(l['FileName']) == str(k):
                    print (" ")
                    print ("Found file " + str(l['FileName']) + " used by Algorithm "+str(l['AlgName']))
                    files_list.append(l['FileName'])
                    ##onlyfiles_map_list_count = onlyfiles_map_list_count + 1
                    check_alg = session.get(BASEURL+'/algorithms/'+l['AlgName'], headers=req_headers, allow_redirects=False, verify=False )
                    check_alg_code = check_alg.status_code
                    ##print (check_alg_code)
                    if check_alg_code == 404:
                        print(' ')
                        print ("Algorithm: " + str(l['AlgName']) + ' does not exist yet! So this script will create a new custom algorithm.')
                        ##print ("Algorithm: " + str(l['AlgName']))
                        req_headers = {
                           'Accept': 'application/json',
                           'Authorization':  authapi
                        }
                        filePath = DX_NEW_MAPPS+"/"+str(k)
                        filePathOpen = open(filePath)
                        fileInfoDict = {
                            "file": filePathOpen,
                        }
                        upl_mapplet = session.post(BASEURL+'/file-uploads',  headers=req_headers, files=fileInfoDict, verify=False )
                        ##print (upl_mapplet.text)
                        upl_mappletj = json.loads(upl_mapplet.text)
                        ##BASEURL+'/algorithms'
                        print(' ')
                        print ("XML mapplet file uploaded with following ID: " + upl_mappletj['fileReferenceId'])
                        alg_parameters = '{ "algorithmName": "'+  str(l['AlgName']) + '", "algorithmType": "CUSTOM_ALGORITHM","description" : "' + str(l['Description']) + '", "algorithmExtension": { "mappletInput": "' + str(l['mappletInput']) + '", "mappletOutput": "' + str(l['mappletOutput']) + '", "fileReferenceId": "' + str(upl_mappletj['fileReferenceId']) + '" } }'
                        ##print(' ')
                        ##print('File name: '+str(k) + ' Parameters: ' + alg_parameters)
                        req_headers = {
                           'Content-Type': 'application/json',
                           'Authorization':  authapi
                        }
                        create_dx_alg = session.post(BASEURL+'/algorithms',  headers=req_headers, data=alg_parameters, verify=False )
                        create_dx_algj = json.loads(create_dx_alg.text)
                        check_create_dx_alg = create_dx_alg.status_code
                        if check_create_dx_alg == 200:
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has been created with latest ' + str(filePath) + ' successfully!')
                        else:
                            create_dx_alg_error=create_dx_algj['errorMessage']
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has NOT been created with latest ' + str(filePath) + 'and got the following error:'+ create_dx_alg_error + ' .')

                    elif check_alg_code == 200:
                        print(' ')
                        print ("Algorithm: " + str(l['AlgName']) + ' already exists! So this script will replace the mapplet xml file.')
                        req_headers = {
                           'Accept': 'application/json',
                           'Authorization':  authapi
                        }
                        filePath = DX_NEW_MAPPS+"/"+str(k)
                        filePathOpen = open(filePath)
                        fileInfoDict = {
                            "file": filePathOpen,
                        }
                        upl_mapplet = session.post(BASEURL+'/file-uploads',  headers=req_headers, files=fileInfoDict, verify=False )
                        ##print (upl_mapplet.text)
                        upl_mappletj = json.loads(upl_mapplet.text)
                        print(' ')
                        print ("XML mapplet file uploaded with following ID: " + upl_mappletj['fileReferenceId'])
                        alg_parameters = '{ "algorithmName": "'+  str(l['AlgName']) + '", "algorithmType": "CUSTOM_ALGORITHM","description" : "' + str(l['Description']) + '", "algorithmExtension": { "mappletInput": "' + str(l['mappletInput']) + '", "mappletOutput": "' + str(l['mappletOutput']) + '", "fileReferenceId": "' + str(upl_mappletj['fileReferenceId']) + '" } }'
                        ##print(' ')
                        ##print('File name: '+str(k) + ' Parameters: ' + alg_parameters)
                        req_headers = {
                           'Content-Type': 'application/json',
                           'Authorization':  authapi
                        }
                        update_dx_alg = session.put(BASEURL+'/algorithms/'+str(l['AlgName']),  headers=req_headers, data=alg_parameters, verify=False )
                        update_dx_algj = json.loads(update_dx_alg.text)
                        check_update_dx_alg = update_dx_alg.status_code
                        if check_update_dx_alg == 200:
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has been updated with latest ' + str(filePath) + ' successfully!')
                        else:
                            update_dx_alg_error=update_dx_algj['errorMessage']
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has NOT been uploaded with latest ' + str(filePath) + 'and got the following error:'+ update_dx_alg_error + ' .')
                    else:
                        sys.exit("Operation failed pulling the algorithm list from the Delphix  Masking engine.")


#
#
#
count_missing_files=0
print("")
print("Missing mapplet files...")
for chk_file in obj['DelphixCustAlg']:
    if str(chk_file['FileName']) not in files_list:
        print ("File " + str(chk_file['FileName']) + " was not found in " + DX_NEW_MAPPS )
        count_missing_files=count_missing_files+1

if count_missing_files == 0:
    print("None.")

if onlyfiles_map_count < 1:
    print ("Mapplet JSON list was not found!")
#
# Closing all opened files
#
filePathOpen.close()
myfile.close()
#
#
#

print ("*******************************************************************************************")
print ("Looking for Lookup JSON list file...")
files_list = [ ]
onlyfiles_look_count = 0
onlyfiles_look_list_count = 0
onlyfiles_look = [f for f in listdir(DX_NEW_BIN_LOOKUPS) if isfile(join(DX_NEW_BIN_LOOKUPS, f))]
for j in onlyfiles_look:
    #print (j)
    if str(j) == 'bin_lookups_list.json':
        onlyfiles_look_count = 1
        print ("Lookup JSON list file exists! --> bin_lookups_list.json")
        with open(DX_NEW_BIN_LOOKUPS+'/bin_lookups_list.json', 'r') as myfile2:
            data2=myfile2.read()
        # parse file
        obj = json.loads(data2)
        onlyfiles_look_list = [f for f in listdir(DX_NEW_BIN_LOOKUPS) if isfile(join(DX_NEW_BIN_LOOKUPS, f))]
        for k in onlyfiles_look_list:
            for l in obj['DelphixCustAlg']:
                if str(l['FileName']) == str(k):
                    print (" ")
                    print ("Found file " + str(l['FileName']) + " used by Algorithm "+str(l['AlgName']))
                    files_list.append(l['FileName'])
                    ##onlyfiles_look_list_count = 1
                    check_alg = session.get(BASEURL+'/algorithms/'+l['AlgName'], headers=req_headers, allow_redirects=False, verify=False )
                    check_alg_code = check_alg.status_code
                    if check_alg_code == 404:
                        print(' ')
                        print ("Algorithm: " + str(l['AlgName']) + ' does not exist yet! So this script will create a new binary lookup algorithm.')
                        ##print ("Algorithm: " + str(l['AlgName']))
                        req_headers = {
                           'Accept': 'application/json',
                           'Authorization':  authapi
                        }
                        filePath = DX_NEW_BIN_LOOKUPS+"/"+str(k)
                        filePathOpen = open(filePath, 'rb')
                        fileInfoDict = {
                            "file": filePathOpen,
                        }
                        upl_binlook = session.post(BASEURL+'/file-uploads',  headers=req_headers, files=fileInfoDict, verify=False )
                        ##print (upl_mapplet.text)
                        upl_binlookj = json.loads(upl_binlook.text)
                        print(' ')
                        print ("Binary Lookup file uploaded with following ID: " + upl_binlookj['fileReferenceId'])
                        alg_parameters = '{ "algorithmName": "'+  str(l['AlgName']) + '", "algorithmType": "BINARY_LOOKUP", "description" : "' + str(l['Description']) + '",  "algorithmExtension": { "fileReferenceIds": [ "' + str(upl_binlookj['fileReferenceId']) + '"  ] } }'
                        ##print(' ')
                        ##print('File name: '+str(k) + ' Parameters: ' + alg_parameters)
                        req_headers = {
                           'Content-Type': 'application/json',
                           'Authorization':  authapi
                        }
                        create_dx_alg = session.post(BASEURL+'/algorithms',  headers=req_headers, data=alg_parameters, verify=False )
                        create_dx_algj = json.loads(create_dx_alg.text)
                        check_create_dx_alg = create_dx_alg.status_code
                        if check_create_dx_alg == 200:
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has been created with latest ' + str(filePath) + ' successfully!')
                        else:
                            create_dx_alg_error=create_dx_algj['errorMessage']
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has NOT been created with latest ' + str(filePath) + 'and got the following error:'+ create_dx_alg_error + ' .')
                        ##BASEURL+'/algorithms'
                    elif check_alg_code == 200:
                        print(' ')
                        print ("Algorithm: " + str(l['AlgName']) + ' already exists! So this script will replace the binary lookup file.')
                        req_headers = {
                           'Accept': 'application/json',
                           'Authorization':  authapi
                        }
                        filePath = DX_NEW_BIN_LOOKUPS+"/"+str(k)
                        filePathOpen = open(filePath, 'rb')
                        fileInfoDict = {
                            "file": filePathOpen,
                        }
                        upl_binlook = session.post(BASEURL+'/file-uploads',  headers=req_headers, files=fileInfoDict, verify=False )
                        ##print (upl_mapplet.text)
                        upl_binlookj = json.loads(upl_binlook.text)
                        print(' ')
                        print ("Binary Lookup file uploaded with following ID: " + upl_binlookj['fileReferenceId'])
                        alg_parameters = '{ "algorithmName": "'+  str(l['AlgName']) + '", "algorithmType": "BINARY_LOOKUP", "description" : "' + str(l['Description']) + '", "algorithmExtension": { "fileReferenceIds": [ "' + str(upl_binlookj['fileReferenceId']) + '"  ] } }'
                        ##print(' ')
                        ##print('File name: '+str(k) + ' Parameters: ' + alg_parameters)
                        req_headers = {
                           'Content-Type': 'application/json',
                           'Authorization':  authapi
                        }
                        update_dx_alg = session.put(BASEURL+'/algorithms/'+str(l['AlgName']),  headers=req_headers, data=alg_parameters, verify=False )
                        update_dx_algj = json.loads(update_dx_alg.text)
                        check_update_dx_alg = update_dx_alg.status_code
                        if check_update_dx_alg == 200:
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has been updated with latest ' + str(filePath) + ' successfully!')
                        else:
                            update_dx_alg_error=update_dx_algj['errorMessage']
                            print(' ')
                            print ("Algorithm " + str(l['AlgName']) + ' has NOT been uploaded with latest ' + str(filePath) + 'and got the following error:'+ update_dx_alg_error + ' .')
                    else:
                        sys.exit("Operation failed pulling the algorithm list from the Delphix  Masking engine.")

#
count_missing_files=0
print("")
print("Missing lookup files...")
for chk_file in obj['DelphixCustAlg']:
    if str(chk_file['FileName']) not in files_list:
        print ("File " + str(chk_file['FileName']) + " was not found in " + DX_NEW_BIN_LOOKUPS )
        count_missing_files=count_missing_files+1

if count_missing_files == 0:
    print("None.")

if onlyfiles_look_count < 1:
    print ("Binary lookup JSON list was not found!")
#
# Closing all opened files
#
filePathOpen.close()
myfile.close()
#
#
#


sys.exit(0)
