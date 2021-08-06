#!/bin/bash
#================================================================================
# File:         dx_api_delete_bookmarks.sh
# Type:         bash-shell script
# Date:         21-Oct 2020
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
# 	Script to be used to cleanup Bookmarks older than X days but NOT listed in a Control File...
#
#================================================================================
#
# Please set the following variables to suit your purposes.
##Inputs:
##vDB name
##pre masking script
##masking script - with jobs details
##post masking script
##replication profile name

##1.-Refresh vDB
##2.-Execute a pre masking
##3.-Mask
##4.-Post masking
##5.-Take snapshot
##6.-Remove old snaps
##7.-Start SDD
# Set this to the Delphix admin user name
DELPHIX_ADMIN=$1
# Set this to the password for the Delphix admin user
DELPHIX_PASS=$2
# Delphix Engine name
DelphixEngine=$3
# vDB name
DXVDB=$4
# PreMasking script
DX_PRE_MSK_SCRIPT=$5
# Masking engine
DX_MSK_ENGINE=$6
# Masking jobs
DX_MSK_SCRIPT=$7
# Masking jobs
DX_MSK_JOBS=$8
# PostMasking script
DX_POST_MSK_SCRIPT=$9
# SDD Replication profile
DX_SDD_REP_PROF=${10}

#
JOBID=""
dx_vdb_ref=""
dx_rep_ref_val=""

TODAYDATE=`date +"%m-%d-%Y"`
echo "Starting script to refresh a Masking vDB, run pre masking scripts, run masking process, run post masking scripts and  replicate to NonProd Delphix engine  from ${DelphixEngine}..."

# Create API session
create_api_session () {
echo "*******************************************************************************************"
echo "Creating session to connect to Delphix Engine ${DelphixEngine}..."
curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/session \
    -c ~/cookies.txt -H "Content-Type: application/json" > /dev/null  <<EOF
{
    "type": "APISession",
    "version": {
        "type": "APIVersion",
        "major": 1,
        "minor": 10,
        "micro": 0
    }
}
EOF
echo
}


# Authenticate to the DelphixEngine
authenticate_api_session () {
echo "Logging in to Delphix Engine ${DelphixEngine}..."
curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/login \
   	-b ~/cookies.txt -c ~/cookies.txt -H "Content-Type: application/json" > /dev/null <<EOF1
{
    	"type": "LoginRequest",
    	"username": "${DELPHIX_ADMIN}",
    	"password": "${DELPHIX_PASS}"
}
EOF1
echo
}


get_vdb_reference () {
export vdbreference=`curl --silent -X GET -k http://${DelphixEngine}/resources/json/delphix/database -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a vdbreferencearray <<< "${vdbreference}"
counter=0
countertemp=0
for j in "${vdbreferencearray[@]}"
do
  export js_col=`echo $j|awk -F":" '{ print $1}'`
      export js_val=`echo $j|awk -F\":\" '{ print $2}'`
      if [ "$js_col" == "\"name\"" ]||[ "$js_col" == "\"reference\"" ]; then
        export js_val_f=`echo $js_val|sed 's/"//g'`
            if [ "$js_val_f" == "$DXVDB" ]; then
                pointertemp=`expr $countertemp - 2`
                dx_vdb_ref=${vdbreferencearray[${pointertemp}]}
                export dx_vdb_ref_val_temp=`echo $dx_vdb_ref|awk -F\":\" '{ print $2}'|sed 's/\"//'`
		export dx_vdb_ref_val=`echo $dx_vdb_ref_val_temp|sed -e 's/^[[:space:]]*//'`
                echo   "VDB reference is: $dx_vdb_ref_val"
            fi
      fi
countertemp=`expr $countertemp + 1`
done
echo
}



refresh_vdb () {
export vdb_refresh=`curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/database/${dx_vdb_ref_val}/refresh  -b ~/cookies.txt -H "Content-Type: application/json" <<EOF1
{
	"type": "OracleRefreshParameters",
	"timeflowPointParameters": {
		"type": "TimeflowPointSemantic"
	}
}
EOF1`
export JOBID=`echo $vdb_refresh|awk -F, '{print $4}'|awk -F: '{print $2}'|sed 's/"//g'`
echo "Refresh job is: $JOBID"
echo "Checking job status..."
check_job_id $JOBID

}

check_job_id () {
export JID=$1
export dx_job=`curl --silent -X GET -k http://${DelphixEngine}/resources/json/delphix/job/${JID} -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a dx_jobarray <<< "${dx_job}"
counter=0
countertemp=0
export job_is_finished=0
while [ "$job_is_finished" == "0" ]
do
	for j in "${dx_jobarray[@]}"
	do
		export js_col=`echo $j|awk -F":" '{ print $1}'`
		export js_val=`echo $j|awk -F\":\" '{ print $2}'`
		if [ "$js_col" == "\"jobState\"" ]; then
			export js_val_f=`echo $js_val|sed 's/"//g'`
			echo "Job ID is $JID"
			echo "Job status is $js_val_f"
			if [ "$js_val_f" == "COMPLETED" ]; then
				job_is_finished=2
			elif [ "$js_val_f" == "FAILED" ]; then
				echo "Job failed!"
				exit 1
			else
				sleep 10
				export dx_job=`curl --silent -X GET -k http://${DelphixEngine}/resources/json/delphix/job/${JID} -b ~/cookies.txt -H "Content-Type: application/json"`
				IFS=',' read -a dx_jobarray <<< "${dx_job}"
            		fi
		fi
	done
done
}

pre_mask () {
echo ""
}

mask () {
echo "Starting Masking processes..."
${DX_MSK_SCRIPT} -h ${DX_MSK_ENGINE}  -p 4 -d 5 -j ${DX_MSK_JOBS}
##./MaskJobExecution_APIv5_v1.bash -h ${DX_MASKING_ENGINE}  -p 4 -d 10 -j ${DX_MSK_JOBS}
}

post_mask () {
echo ""
}

vdb_snapshot () {
export vdb_snapshot=`curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/database/${dx_vdb_ref_val}/sync  -b ~/cookies.txt -H "Content-Type: application/json" <<EOF1
{
        "type": "OracleSyncFromExternalParameters"
}
EOF1`
export JOBID=`echo $vdb_snapshot|awk -F, '{print $4}'|awk -F: '{print $2}'|sed 's/"//g'`
echo "Snapshot job is: $JOBID"
echo "Checking job status..."
check_job_id $JOBID
delete_old_snaps
}

delete_old_snaps () {
echo
export dx_snaps=`curl --silent -X GET -k http://${DelphixEngine}/resources/json/delphix/snapshot?database=${dx_vdb_ref_val} -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a dx_snapsarray <<< "${dx_snaps}"
counter=0
countertemp=0
for j in "${dx_snapsarray[@]}"
do
  export js_col=`echo $j|awk -F":" '{ print $1}'`
  export js_val=`echo $j|awk -F\":\" '{ print $2}'`
  if [ "$js_col" == "\"reference\"" ]; then
  	export js_val_f=`echo $js_val|sed 's/"//g'`
	echo $js_val_f >> /tmp/snaplst.lst
  fi
done
cat /tmp/snaplst.lst|sort -r > /tmp/snaplst2.lst
echo "Full list of snapshots:"
cat /tmp/snaplst2.lst
tail -n +2 /tmp/snaplst2.lst > /tmp/snaplst3.lst
echo "Snapshots to remove are:"
cat /tmp/snaplst3.lst
rm -f /tmp/snaplst.lst
echo
echo "Deleting old snapshots..."
del_snapshots="/tmp/snaplst3.lst"
while IFS= read -r dx_snapshot
do
curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/snapshot/${dx_snapshot}/delete  -b ~/cookies.txt -H "Content-Type: application/json" > /dev/null <<EOF1
{
}
EOF1
done < "$del_snapshots"

}

get_rep_reference () {
echo
export vrepreference=`curl --silent -X GET -k http://${DelphixEngine}/resources/json/delphix/replication/spec -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a vrepreferencearray <<< "${vrepreference}"
counter=0
countertemp=0
for j in "${vrepreferencearray[@]}"
do
  export js_col=`echo $j|awk -F":" '{ print $1}'`
      export js_val=`echo $j|awk -F\":\" '{ print $2}'`
      if [ "$js_col" == "\"name\"" ]; then
        export js_val_f=`echo $js_val|sed 's/"//g'`
            if [ "$js_val_f" == "$DX_SDD_REP_PROF" ]; then
                pointertemp=`expr $countertemp - 2`
                dx_rep_ref=${vrepreferencearray[${pointertemp}]}
                export dx_rep_ref_val_temp=`echo $dx_rep_ref|awk -F\":\" '{ print $2}'|sed 's/\"//'`
                export dx_rep_ref_val=`echo $dx_rep_ref_val_temp|sed -e 's/^[[:space:]]*//'`
                echo   "Replication profile reference is: $dx_rep_ref_val"
            fi
      fi
countertemp=`expr $countertemp + 1`
done
echo
}

sdd_replication () {
DX_SDD_REF=$1
export dx_rep_api=`curl -s -X POST -k --data @- http://${DelphixEngine}/resources/json/delphix/replication/spec/${DX_SDD_REF}/execute  -b ~/cookies.txt -H "Content-Type: application/json" <<EOF1
{
}
EOF1`
export JOBID=`echo $dx_rep_api|awk -F, '{print $4}'|awk -F: '{print $2}'|sed 's/"//g'`
echo "Replication job is: $JOBID"
echo "Checking job status..."
check_job_id $JOBID
echo ""
}


#######
create_api_session
authenticate_api_session
get_vdb_reference
refresh_vdb
pre_mask
mask
post_mask
vdb_snapshot
get_rep_reference
sdd_replication $dx_rep_ref_val
#######
