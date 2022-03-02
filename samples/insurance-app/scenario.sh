#!/bin/bash

URL="http://localhost:3000"
TIME_SLEEP=3

USER1="qwe@qwe.com"
USER2="asd@asd.com"

buyBikeAndClaimFile() {
    local USERNAME=$1
    local THEFT=$2

    # BUY BIKE
    local RES=$(curl $URL/shop/api/enter-contract \
        -H 'content-type: application/json' \
        --data-binary '{"user":{"username":"'$USERNAME'","firstName":"John","lastName":"Doe"}, "contractTypeUuid":"1d640cf7-9808-4c78-b7f0-55aaad02e9e5","additionalInfo":{"item":{"id":0,"brand":"Canyon","model":"Spectral AL 6.0","price":3420,"serialNo":"P8VEWM"},"startDate":"2020-07-06T22:00:00.000Z","endDate":"2020-07-13T22:00:00.000Z"}}' \
        --compressed)

    echo $RES
    sleep $TIME_SLEEP

    UUID=$(jq '.loginInfo.uuid' <<< "$RES")
    local PASS=$(jq '.loginInfo.password' <<< "$RES")

    # CLAIM A FILE
    local RES=$(curl $URL'/insurance/api/file-claim' \
        -H 'content-type: application/json' \
        --data-binary '{"user":{"username":"'$USERNAME'","password":'$PASS'},"contractUuid":'$UUID', "claim":{"isTheft":'$THEFT',"description":"test"}}' \
        --compressed)

    echo $RES
    sleep $TIME_SLEEP

    CLAIM_UUID=$(jq '.uuid' <<< "$RES")
}

repairBike() {
    # ORDER REPAIR
    curl $URL/insurance/api/process-claim \
        -H 'content-type: application/json' \
        --data-binary '{"contractUuid":'$UUID',"uuid":'$CLAIM_UUID',"status":"R","reimbursable":0}' \
        --compressed

    sleep $TIME_SLEEP

    local ORDERS=$(curl $URL/repair-shop/api/repair-orders -X 'POST')
    sleep $TIME_SLEEP
    local ORDER_UUID=$(jq -c ".[] | select(.claimUuid == $CLAIM_UUID) | .uuid" <<< "$ORDERS")

    # COMPLETE REPAIR
    curl $URL/repair-shop/api/complete-repair-order \
        -H 'content-type: application/json' \
        --data-binary '{"uuid":'$ORDER_UUID'}' \
        --compressed
    
    sleep $TIME_SLEEP
}

policeReport() {
    local THEFT=$1

    curl $URL/police/api/process-claim \
        -H 'content-type: application/json' \
        --data-binary '{"contractUuid":'$UUID',"uuid":'$CLAIM_UUID',"isTheft":'$THEFT',"fileReference":"test"}' \
        --compressed

    sleep $TIME_SLEEP
}

rejectClaim() {
    # REJECT CLAIM
    curl $URL/insurance/api/process-claim \
        -H 'content-type: application/json' \
        --data-binary '{"contractUuid":'$UUID',"uuid":'$CLAIM_UUID',"status":"J","reimbursable":0}' \
        --compressed

    sleep $TIME_SLEEP
}

reimburse() {
    # REJECT CLAIM
    curl $URL/insurance/api/process-claim \
        -H 'content-type: application/json' \
        --data-binary '{"contractUuid":'$UUID',"uuid":'$CLAIM_UUID',"status":"F","reimbursable":'$1'}' \
        --compressed

    sleep $TIME_SLEEP
}

# SCENARIO 1 - broken, repair completed
buyBikeAndClaimFile $USER1 "false"
repairBike
# reimburse 234

# SCENARIO 2 - broken, rejected
buyBikeAndClaimFile $USER2 "false"
rejectClaim

# SCENARIO 3 - broken, reimbursed
buyBikeAndClaimFile $USER1 "false"
reimburse 234

# SCENARIO 4 - stolen, police ack, reimbursed
buyBikeAndClaimFile $USER2 "true"
policeReport "true"
reimburse 123

# SCENARIO 5 - stolen, police dec, reimbursed !!!
buyBikeAndClaimFile $USER1 "true"
policeReport "false"
reimburse 123

# SCENARIO 6 - stolen, police dec, rejected
buyBikeAndClaimFile $USER2 "true"
policeReport "false"
rejectClaim

# SCENARIO 7 - stolen, police ack, rejected
buyBikeAndClaimFile $USER1 "true"
policeReport "true"
rejectClaim
