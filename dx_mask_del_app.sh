#!/bin/bash
host=$1
DMPORT=80
DMUSER=$2
DMPASS=$3
APPNAME=$4



myLoginToken=""
API_PATH="masking/api/"
########### base url

API_URL="http://${host}:${DMPORT}/${API_PATH}"

#################### Authenticate

authenticate () {
echo "Authenticating on $API_URL"
#DMUSER="\"$DMUSER\""
#DMPASS="\"$DMPASS\""
#getToken=$(curl -sX POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "{"\"username\"": "${DMUSER}", "\"password\"": "${DMPASS}"}" $API_URL"login")

getToken=$(curl -sX POST --header 'Content-Type: application/json'  -d "{"\"username\"": "\"${DMUSER}\"", "\"password\"": "\"${DMPASS}\""}" $API_URL"login")
##echo $getToken
echo "API Login Request = curl -sX POST --header 'Content-Type: application/json' --header 'Accept: application/json' -d "{"username": "$DMUSER", "password": "***"}" $API_URL"login""
##echo "getToken = :  ${getToken}"

     if ( echo ${getToken} | grep 'errorMessage' ); then
        echo "Login failed. Please try again. "
        echo "${getToken}"
        exit 1
     fi
myLoginToken=$( echo "'$getToken'" | grep Authorization | cut -f2 -d':' | tr -d '{,},", ' | sed "s/'//g" )
   if [[ -z ${myLoginToken} ]]; then
      echo "Error: Authentication Failed! "
      echo "${getToken}"
      exit 1
   else
      echo "Authentication successful! "
      echo "Token: ${myLoginToken}"
   fi
}

#################### Find App to delete
get_apps () {
echo "Searching Delphix Masking application to delete..."
APP_STATUS=$(curl -sX GET --header 'Accept: application/json' --header "Authorization:${myLoginToken}" $API_URL"applications")
##echo $APP_STATUS
IFS=',' read -a APP_STATUS_array <<< "${APP_STATUS}"
counter=0
countertemp=0
for j in "${APP_STATUS_array[@]}"
do
  export js_col=`echo $j|awk -F":" '{ print $1}'`
  export js_val=`echo $j|awk -F\":\" '{ print $2}'`
  if [ "$js_col" == "\"applicationName\"" ]; then
    export js_val_2=`echo $js_val|awk -F\" '{ print $1}'`
    ##echo $js_val_2
    if [ "$js_val_2" == "$APPNAME" ]; then
      pointertemp=`expr $countertemp - 1`
      dx_msk_app_ref=${APP_STATUS_array[${pointertemp}]}
  	  export js_val_f_1=`echo $dx_msk_app_ref|sed 's/"//g'`
      export js_val_f_2=`echo $js_val_f_1|awk -F\: '{ print $2}'`
	    echo "Application ID is :" $js_val_f_2
    fi
  fi
countertemp=`expr $countertemp + 1`
done
}

#################### Delete App
delete_app () {
echo "Deleting Delphix Masking application..."
DEL_APP=$(curl -sX DELETE --header 'Accept: application/json' --header "Authorization:${myLoginToken}" $API_URL"applications/"$js_val_f_2)
if [ -z "$DEL_APP" ]
then
      echo "Delphix Masking application $APPNAME has been deleted successfully!"
else
      echo $DEL_APP
      echo "Delphix Masking application $APPNAME has NOT been deleted!"
      exit 1
fi

}

#################### Main Script
authenticate
get_apps
delete_app
####################
