#!/bin/bash
# Delphix Engine name
DelphixEngine=$1
# Set this to the Delphix admin user name
DELPHIX_ADMIN=$2
# Set this to the password for the Delphix admin user
DELPHIX_PASS=$3
#Delphix SelfService Template
DX_TEMPLATE_NAME=$4
#Delphix Self Service Data source order
DX_PRIORITY=1
#Delphix Data source name for Self Service Template
#DX_DSRC_NAME=$5
#Delphix dSource/vDB to be added as a source in Self Service Template
DX_DATASRC=$5


# Create API session
create_api_session () {
curl -s --output /dev/null -X POST -k --data @- https://${DelphixEngine}/resources/json/delphix/session \
    -c ~/cookies.txt -H "Content-Type: application/json" <<EOF
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
curl -s --output /dev/null -X POST -k --data @- https://${DelphixEngine}/resources/json/delphix/login \
   	-b ~/cookies.txt -c ~/cookies.txt -H "Content-Type: application/json" <<EOF1
{
    	"type": "LoginRequest",
    	"username": "${DELPHIX_ADMIN}",
    	"password": "${DELPHIX_PASS}"
}
EOF1
echo
}

get_api_info () {
export ddb=`curl --silent -X GET -k https://${DelphixEngine}/resources/json/delphix/database -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a delphixdbarray <<< "${ddb}"

export counter=0
for i in "${delphixdbarray[@]}"
do
        export js_col=`echo $i|awk -F":" '{ print $1}'`
        export js_val=`echo $i|awk -F\": '{ print $2}'`
        if [ "$js_col" == "\"name\"" ]||[ "$js_col" == "\"reference\"" ]; then
                export js_val_f1=`echo $js_val|sed 's/"//g'`
                reference_db[$counter]="$js_val_f1"
                counter=`expr $counter + 1`
        fi
done

export counter=0
for j in "${reference_db[@]}"
do
        if [ "$j" == "${DX_DATASRC}" ]; then
                pointer=`expr $counter - 1`
                DX_CONTAINER_REF=${reference_db[${pointer}]}
                #echo "Reference name is : " ${DX_CONTAINER_REF}
        fi
        counter=`expr $counter + 1`
done


}


create_template () {
echo " Creating Self Service template ${DX_TEMPLATE_NAME} with source ${DX_DATASRC}..."
curl -s -X POST -k --data @- https://${DelphixEngine}/resources/json/delphix/selfservice/template \
        -b ~/cookies.txt -c ~/cookies.txt -H "Content-Type: application/json" <<EOF1 
{
    "type": "JSDataTemplateCreateParameters",
    "name": "${DX_TEMPLATE_NAME}",
    "dataSources": [
        {
            "type": "JSDataSourceCreateParameters",
            "source": {
                "type": "JSDataSource",
                "priority": ${DX_PRIORITY},
                "name": "${DX_DATASRC}"
	    },
            "container": "${DX_CONTAINER_REF}"
        }
    ]
}
EOF1
echo 
}



create_api_session
authenticate_api_session
get_api_info
create_template
exit 0
