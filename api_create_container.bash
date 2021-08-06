#!/bin/bash
# Delphix Engine name
DelphixEngine=$1
# Set this to the Delphix admin user name
DELPHIX_ADMIN=$2
# Set this to the password for the Delphix admin user
DELPHIX_PASS=$3
#Delphix Container name
DX_CONTAINER=$4
#Delphix SelfService Template
DX_TEMPLATE=$5
#Delphix Self Service Data source order
DX_PRIORITY=1
#Delphix Data source name for Self Service Template
#DX_DSRC_NAME=$6
#Delphix dSource/vDB to be added as a source in Self Service Container
DX_DATASRC=$6


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
#                echo "Reference name is : " ${DX_CONTAINER_REF}
        fi
        counter=`expr $counter + 1`
done

export dtemplate=`curl --silent -X GET -k https://${DelphixEngine}/resources/json/delphix/selfservice/template -b ~/cookies.txt -H "Content-Type: application/json"`
IFS=',' read -a delphixdtemplatearray <<< "${dtemplate}"



export counter=0
for i in "${delphixdtemplatearray[@]}"
do
        export js_col=`echo $i|awk -F":" '{ print $1}'`
        export js_val=`echo $i|awk -F\": '{ print $2}'`
        if [ "$js_col" == "\"name\"" ]||[ "$js_col" == "\"reference\"" ]; then
                export js_val_f2=`echo $js_val|sed 's/"//g'`
                reference_template[$counter]="$js_val_f2"
                counter=`expr $counter + 1`
        fi
done

export counter=0
for j in "${reference_template[@]}"
do
        if [ "$j" == "${DX_TEMPLATE}" ]; then
                pointer=`expr $counter - 1`
                DX_TEMPLATE_REF=${reference_template[${pointer}]}
#                echo "Reference name is : " ${DX_TEMPLATE_REF}
        fi
        counter=`expr $counter + 1`
done

}


create_container () {
echo " Creating Self Service container ${DX_CONTAINER} from template ${DX_TEMPLATE} with source ${DX_DATASRC}..."
curl -s -X POST -k --data @- https://${DelphixEngine}/resources/json/delphix/selfservice/container \
        -b ~/cookies.txt -c ~/cookies.txt -H "Content-Type: application/json" <<EOF1
{
    "type": "JSDataContainerCreateWithoutRefreshParameters",
    "name": "${DX_CONTAINER}",
    "dataSources": [
        {
            "type": "JSDataSourceCreateParameters",
            "source": {
                "type": "JSDataSource",
                "priority": 1,
                "name": "${DX_DATASRC}"
            },
            "container": "${DX_CONTAINER_REF}"
        }
    ],
    "template": "${DX_TEMPLATE_REF}"
}
EOF1
}


###MAIN SCRIPT###
create_api_session
authenticate_api_session
get_api_info
create_container
exit 0
###END MAIN SCRIPT###
