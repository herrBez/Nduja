#!/bin/bash



readonly FORMAT_FILE=format.json


codesearch_for_each_page() {
    local readonly BASE_OUTPUT_FILE=/tmp/output
    local readonly BASE_RESULT_FILE=/tmp/result
    local readonly BASE_FINAL_RESULT_FILE=/tmp/final
    local readonly NAME=$1
    local readonly SYMBOL=$2
    local readonly REGEXP=$3
    local readonly SEARCH_STRING=$4
    local readonly p=$5
    
    local readonly OUTPUT_FILE="$BASE_OUTPUT_FILE-$SYMBOL-$p.json"
    local readonly RESULT_FILE="$BASE_RESULT_FILE-$SYMBOL-$p.json"
    local readonly FINAL_RESULT_FILE="$BASE_FINAL_RESULT_FILE-$SYMBOL-$p.json"

    touch $OUTPUT_FILE
    touch $RESULT_FILE

    # Download the json file containing the infos
    curl -s -o $OUTPUT_FILE https://searchcode.com/api/codesearch_I/?q=${SEARCH_STRING}&p=${p}&per_page=100&loc=0
    # Extract the "result" key from the json file and store it in $TMP_RESULT_FILE
    cat $OUTPUT_FILE | jq '.' |  jq '.["results"]' > $RESULT_FILE
    
    # Extract the indices of the result_file
    local readonly KEYS=$(cat $RESULT_FILE | jq 'keys' | jq '.[]')
    for k in $KEYS; do
        local readonly TMP=$(cat $RESULT_FILE | jq ".[$k]")
        local readonly MATCH=$(echo $TMP | jq "." | jq --raw-output ".lines" | egrep -o "$REGEXP")

        if [ "$MATCH" != "" ]; then # at least a match is found
            local readonly REPOSITORY=$(echo $TMP | jq --raw-output ".repo" | sed 's/\.[^.]*$//')
            local readonly RAW_REPOSITORY=$(echo $REPOSITORY | sed 's/github.com/raw.githubusercontent.com/')
            local readonly DIRECTORY=$(echo $TMP | jq --raw-output ".location")
            local readonly FILENAME=$(echo $TMP | jq --raw-output ".filename")
            local URL=""
            if [ "$DIRECTORY" == "" ] || [ "$DIRECTORY" == "/" ]; then
                URL=$REPOSITORY/$FILENAME
                RAW_URL=$RAW_REPOSITORY/master/$FILENAME
            else
                URL=$REPOSITORY/$DIRECTORY/$FILENAME
                RAW_URL=$RAW_REPOSITORY/master/$DIRECTORY/$FILENAME
            fi

            local readonly WALLETS=$(printf "[$MATCH]" | tr '\n' ',')
            local readonly HOST=$(printf "$REPOSITORY" | egrep -o "https?://[^/]*" | sed -r "s/https?:\/\///")
            local readonly USERNAME=$(printf "$REPOSITORY" | sed -r "s/https?:\/\/[^/]*\/([^/]*)\/.*/\1/")
            echo "{\
            \"username\": \"$USERNAME\",\
            \"host\": \"$HOST\", \
            \"symbol\" : \"$SYMBOL\", \
            \"url\": \"$URL\",\
            \"known_raw_url\": \"RAW_URL\",\
            \"pathToFile\": \"$DIRECTORY/$FILENAME\",\
            \"wallet\": \"$WALLETS\"\
            }" | jq "." >> $BASE_FINAL_RESULT_FILE-$p.json
            counter=$((counter+1))
        fi
    done
}


codesearch_search() {

    export -f codesearch_for_each_page
    parallel codesearch_for_each_page ::: "$1" ::: "$2" ::: "$3" ::: "$4" ::: $(seq 0 49)

}


main() {

    local counter=0
    local readonly FORMAT_INDEX=$(cat $FORMAT_FILE | jq 'keys' | jq '.[]')

    for f in $FORMAT_INDEX; do
        cat $FORMAT_FILE | jq ".[$f].name"
        
        local readonly FORMAT_ENTRY=$(cat $FORMAT_FILE | jq --raw-output ".[$f]")
        local readonly REGEXP=$(echo "$FORMAT_ENTRY"  | jq --raw-output ".wallet_regexp")
        local readonly NAME=$(echo "$FORMAT_ENTRY"   | jq --raw-output ".name")
        local readonly SYMBOL=$(echo "$FORMAT_ENTRY" | jq --raw-output ".symbol")
        local readonly SEARCH_STRING="$NAME+$SYMBOL+Donation"
        
        codesearch_search "$NAME" "$SYMBOL" "$REGEXP" "$SEARCH_STRING" 
        
    done
}


main
