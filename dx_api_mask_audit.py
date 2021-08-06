#================================================================================
# File:         dx_api_maskaudit.py
# Type:         python script
# Date:         01-May 2020
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
#   python dx_api_mask_audit.py <DELPHIX USER> <DELPHIX USER PASSWORD> <DELPHIX ENGINE>
#
#
# Example
#   python dx_api_mask_audit.py admin Admin-12 carlosdlp5381msk.dlpxdc.co
#================================================================================
#
import sys
import requests
import json
import time
import os
import filecmp
import difflib
import math
from datetime import datetime, date, timedelta
from os import path

#
DMUSER=sys.argv[1]
DMPASS=sys.argv[2]
DX_ENGINE=sys.argv[3]
BASEURL='http://'+ DX_ENGINE + '/masking/api'
today_date = datetime.today().strftime('%Y-%m-%d')
yesterday = datetime.today() - timedelta(days=1)
dbyest = datetime.today() - timedelta(days=2)
yesterday = yesterday.strftime('%Y-%m-%d')
dbyest = dbyest.strftime('%Y-%m-%d')

print("**********************************************************************************************************************************")
print("******************************************Starting Masking Audit script...********************************************************")

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
r = session.post(BASEURL+'/login', data=formdata, headers=req_headers, allow_redirects=False)
#print (r.text)

#
# JSON Parsing ...
#
j = json.loads(r.text)

#print (j['Authorization'])
authapi = j['Authorization']

#
# Update Request Headers  with authorization key...
#
req_headers = {
   'Content-Type': 'application/json',
   'Authorization':  authapi
}

#
# Add a Masking admin user
#

#formdata = '{ "userName": "' + MSK_USER + '" ,  "password": "' + MSK_PASSWORD + '" ,  "firstName": "First", "lastName": "Last", "email": "user@delphix.com", "isAdmin": "true" , "isLocked": "false" }'
#
r = session.get(BASEURL+'/environments?page_size=1000', headers=req_headers, allow_redirects=False)
environments = json.loads(r.text)
#
#
#
r = session.get(BASEURL+'/applications?page_size=1000', headers=req_headers, allow_redirects=False)
applications = json.loads(r.text)

#
#
#
r = session.get(BASEURL+'/database-connectors?page_size=1000', headers=req_headers, allow_redirects=False)
dbconnectors = json.loads(r.text)

#
#
#
r = session.get(BASEURL+'/database-rulesets', headers=req_headers, allow_redirects=False)
dbrulesets = json.loads(r.text)
#
#
#
r = session.get(BASEURL+'/table-metadata?page_size=1000', headers=req_headers, allow_redirects=False)
tablemetadata = json.loads(r.text)


r = session.get(BASEURL+'/column-metadata?is_masked=true&page_size=1000', headers=req_headers, allow_redirects=False)
colmetadata = json.loads(r.text)



r = session.get(BASEURL+'/masking-jobs?page_size=1000', headers=req_headers, allow_redirects=False)
maskjob = json.loads(r.text)






##environments
##dbconnectors
##dbrulesets
##colmedatada
##tablemetadata
print ('')
print ("Masking inventory (ONLY Masked columns)")
print ("AuditDate,LastMaskingJobExecution,ApplicationName,EnvName,MaskingJob,ConnectorName,RulesetName,TableName,ColumnName,Domain,Algorithm,ColumnDataType,ColumnLength")
if path.exists("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ dbyest + ".out") == True:
    os.remove("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ dbyest + ".out")
    ##print("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ dbyest + ".out removed!")
    #print (test)
if path.exists("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ today_date + ".out") == True:
    os.remove("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ today_date + ".out")
    ##print("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ today_date + ".out removed!")
    #print (test)
file = open("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ today_date + ".out" ,"a+")
#file.write ("Masking inventory (ONLY Masked columns)")
file.write("AuditDate,LastMaskingJobExecution,ApplicationName,EnvName,MaskingJob,ConnectorName,RulesetName,TableName,ColumnName,Domain,Algorithm,ColumnDataType,ColumnLength\n")
for dbobj in environments['responseList']:
    dx_env_name = dbobj['environmentName']
    dx_env_id = dbobj['environmentId']
    dx_app_id = dbobj['applicationId']
    for dbobj2 in dbconnectors['responseList']:
        if dx_env_id == dbobj2['environmentId']:
            dx_connector_name = dbobj2['connectorName']
            dx_connector_id = dbobj2['databaseConnectorId']
            for dbobj3 in dbrulesets['responseList']:
                if dbobj3['databaseConnectorId'] == dx_connector_id:
                    dx_rs_name = dbobj3['rulesetName']
                    dx_rs_id = dbobj3['databaseRulesetId']
                    for dbobj4 in tablemetadata['responseList']:
                        if  dbobj4['rulesetId'] == dx_rs_id:
                            dx_table_name = dbobj4['tableName']
                            dx_table_id = dbobj4['tableMetadataId']
                            for dbobj5 in colmetadata['responseList']:
                                if dbobj5['tableMetadataId'] == dx_table_id:
                                    for dbobj6 in maskjob['responseList']:
                                        dx_mask_job_id = dbobj6['maskingJobId']
                                        if dbobj6['rulesetId'] == dx_rs_id:
                                            r = session.get(BASEURL+'/executions?page_size=5&job_id=' + str(dx_mask_job_id), headers=req_headers, allow_redirects=False)
                                            #print (r.text)
                                            maskjob_execution = json.loads(r.text)
                                            #print (maskjob_execution['_pageInfo']['numberOnPage'])
                                            #print (maskjob_execution['_pageInfo']['total'])
                                            dx_msk_job_page = maskjob_execution['_pageInfo']['numberOnPage']
                                            dx_msk_job_exec = maskjob_execution['_pageInfo']['total']
                                            #print ('---------------------------------------------')
                                            if dx_msk_job_exec == 0:
                                                dx_exec_end_f = 'N/A'
                                            else:
                                                dx_page_cal = float(dx_msk_job_exec) / float(dx_msk_job_page)
                                                dx_page_cal_t = math.ceil(dx_page_cal)
                                                if dx_page_cal > 1:
                                                    dx_chk_page = int(dx_page_cal_t)
                                                    r = session.get(BASEURL+'/executions?page_size=5&page_number=' + str(dx_chk_page) + '&job_id=' + str(dx_mask_job_id), headers=req_headers, allow_redirects=False)
                                                    maskjob_execution = json.loads(r.text)
                                                dx_exec_status = maskjob_execution['responseList'][-1]['status']
                                                if dx_exec_status == 'SUCCEEDED':
                                                    dx_exec_start = maskjob_execution['responseList'][-1]['startTime']
                                                    dx_exec_end = maskjob_execution['responseList'][-1]['endTime']
                                                else:
                                                    for dbobjfinal in maskjob_execution['responseList']:
                                                        if dbobjfinal['status'] == 'SUCCEEDED':
                                                            #print (maskjob_execution['responseList'][-1]['endTime'])
                                                            dx_exec_start = maskjob_execution['responseList'][-1]['startTime']
                                                            dx_exec_end = maskjob_execution['responseList'][-1]['endTime']
                                                            print(dx_exec_end)
                                                dx_dt_temp, dx_dt_temp2 = dx_exec_end.split('T')
                                                dx_exec_end_ft = datetime.strptime(dx_dt_temp, '%Y-%m-%d')
                                                dx_exec_end_f = dx_exec_end_ft.strftime('%Y-%m-%d')
                                                #dx_exec_end_f = dx_exec_end.strftime('%Y-%m-%d')

                                            dx_mask_job = dbobj6['jobName']
                                            dx_col_name = dbobj5['columnName']
                                            dx_col_id = dbobj5['columnMetadataId']
                                            dx_col_domain = dbobj5['domainName']
                                            dx_col_alg = dbobj5['algorithmName']
                                            dx_col_datatype = dbobj5['dataType']
                                            dx_col_length  = dbobj5['columnLength']
                                            #file = open("dx_masking_inventory_" + str(DX_ENGINE) +"_"+ today_date + ".out" ,"a+")
                                            for dbobj6 in applications['responseList']:
                                                if dx_app_id == dbobj6['applicationId']:
                                                    dx_app_name = dbobj6['applicationName']
                                                    print (str(today_date) + ',' + str(dx_exec_end_f)+ ',' + dx_app_name + ',' + dx_env_name + ',' + dx_mask_job + ',' + dx_connector_name + ',' + dx_rs_name + ',' + dx_table_name + ',' + dx_col_name + ',' + dx_col_domain + ',' + dx_col_alg + ',' + dx_col_datatype + ',' + str(dx_col_length))
                                                    file.write (str(today_date) + ',' + str(dx_exec_end_f) + ',' + dx_app_name + ',' + dx_env_name + ',' + dx_mask_job + ',' + dx_connector_name + ',' + dx_rs_name + ',' + dx_table_name + ',' + dx_col_name + ',' + dx_col_domain + ',' + dx_col_alg + ',' + dx_col_datatype + ',' + str(dx_col_length) + '\n')
                                        #dx_exec_start = ''
                                        #dx_exec_end = ''
                                        #dx_exec_end_f =''

file.close()
print ('')
