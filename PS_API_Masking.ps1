#Declare our named parameters here...
param(
   [string] $ApplName,
   [string] $jobID,
   [string] $DMIP,
   [string] $userID,
   [string] $password
)
echo '#########################Delphix Masking APICall ################################'
# File:		DelphixMasking_APICall_Posershell.ps1
# Type:		Powershell script
# Author:	Delphix Professional Services
# Date:		30-Jun 2016
#
# Copyright and license:
#
#       Licensed under the Apache License, Version 2.0 (the "License"); you may
#       not use this file except in compliance with the License.
#
#       You may obtain a copy of the License at
#     
#               http://www.apache.org/licenses/LICENSE-2.0
#
#       Unless required by applicable law or agreed to in writing, software
#       distributed under the License is distributed on an "AS IS" basis,
#       WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#
#       See the License for the specific language governing permissions and
#       limitations under the License.
#     
#       Copyright (c) 2016 by Delphix.  All rights reserved.
#
# Description:
#
#	Powershell script to automate the call to the Delphix Masking Engine.
#   
#   Required parameters:  Application and JobID
#   
#
#
#   
#   Notes: This script will call masking API via standard ME port; see URL below
#          Status code 200 reflects successful execution                                  
#________________________________________________________________________________________
$result=""
$reader=""
$responseBody=""
$resultStatus=""
$status=""
$sleepTimer="10"
########################################################################################
# Masking job parameters - Application and JobID
#
$portNumber="80"
$baseURL="http://"+$DMIP+"/masking"
$apiUrl=$baseURL+"/api"





$login = @"
{
    "username": "${userID}",
    "password": "${password}"
}
"@

#################### Authenticate ######################

$authToken = Invoke-RestMethod -Method POST -ContentType "application/json" -Uri "$apiUrl/login" -Body $login 

$myAuthToken = $authToken.Authorization
echo "myAuthToken ConvertFrom-Json = $myAuthToken"

$authHeader = New-Object "System.Collections.Generic.Dictionary[[String],[String]]"
$authHeader.add("Authorization",$myAuthToken)

############ END AUTHENTICATE ##########################


########################################################################################
echo '##################      Executing Job                         ####################'

write-host "Executing Job : "  $jobID  " in Application : "  $ApplName 
$uri=$apiUrl+"/executions" 

$execparams = @"
{
    "jobId": "${jobID}"
}
"@

$resultRun = Invoke-WebRequest -Header $authHeader -ContentType 'Application/json' -METHOD POST -BODY $execparams -Uri $uri
$execid = echo $resultRun.Content|Out-String|ConvertFrom-Json
$maskexecid = $execid.executionId

########################################################################################
echo '##################      Checking Job Status                   ####################'
#Start-Sleep $sleepTimer
$uri=$apiUrl+"/executions/"+$maskexecid
$resultStatus = Invoke-WebRequest -Header $authHeader -ContentType 'application/json' -METHOD GET  -Uri $uri
$resultStat = echo $resultStatus.Content|Out-String|ConvertFrom-Json
$status = $resultStat.status
write-host 'status is : ' $status

########################################################################################
echo '##################      Polling for Job Status                ####################'
DO {
	Start-Sleep $sleepTimer
    $resultStatus = Invoke-WebRequest -Header $authHeader -ContentType 'application/json' -METHOD GET  -Uri $uri
    $resultStat = echo $resultStatus.Content|Out-String|ConvertFrom-Json
    $status = $resultStat.status
    write-host 'status is : ' $status
} WHILE ($status -eq'RUNNING')
########################################################################################
echo '##################      End Of File                           ####################'