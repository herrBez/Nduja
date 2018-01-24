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
    printf "$p\n"
    
    local readonly OUTPUT_FILE="$BASE_OUTPUT_FILE-$SYMBOL-$p.json"
    local readonly RESULT_FILE="$BASE_RESULT_FILE-$SYMBOL-$p.json"
    local readonly FINAL_RESULT_FILE="$BASE_FINAL_RESULT_FILE-$SYMBOL-$p.json"

    rm -f $OUTPUT_FILE
    rm -f $RESULT_FILE
    rm -f $FINAL_RESULT_FILE
    
    touch $OUTPUT_FILE
    touch $RESULT_FILE
    touch $FINAL_RESULT_FILE
    

    # Download the json file containing the infos
    echo "https://searchcode.com/api/codesearch_I/?q=${SEARCH_STRING}&p=${p}&per_page=100&loc=0"
    until $(curl -s -o $OUTPUT_FILE https://searchcode.com/api/codesearch_I/?q=$SEARCH_STRING&p=p&per_page=100&loc=0); do
        sleep 0.1
    done
    
    
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
            
            local WALLET_LIST=$(
                for wallet in $MATCH; do
                    printf "\"$wallet\","
                done
            )
            WALLET_LIST=$(echo $WALLET_LIST | sed 's/.$//')
            

            local readonly HOST=$(printf "$REPOSITORY" | egrep -o "https?://[^/]*" | sed -r "s/https?:\/\///")
            local readonly USERNAME=$(printf "$REPOSITORY" | sed -r "s/https?:\/\/[^/]*\/([^/]*)\/.*/\1/")
            printf ",\n" >> $FINAL_RESULT_FILE
            printf "{\
            \"username\": \"$USERNAME\",\
            \"host\": \"$HOST\", \
            \"symbol\" : \"$SYMBOL\", \
            \"url\": \"$URL\",\
            \"known_raw_url\": \"$RAW_URL\",\
            \"pathToFile\": \"$DIRECTORY/$FILENAME\",\
            \"wallet\": [$WALLET_LIST]\
            }\n" >> $FINAL_RESULT_FILE
            counter=$((counter+1))
        fi
    done
}




codesearch_search() {

    export -f codesearch_for_each_page
    parallel codesearch_for_each_page ::: "$1" ::: "$2" ::: "$3" ::: "$4" ::: $(seq 0 49)

}

unite() {
    
    local readonly TMP_SEARCH_RESULT_FILE=/tmp/search-result.json
    local readonly SEARCH_RESULT_FILE=/tmp/search-result-def.json
    
    rm -f $TMP_SEARCH_RESULT_FILE
    rm -f $SEARCH_RESULT_FILE
    
    
    cat /tmp/final-*.json >> $TMP_SEARCH_RESULT_FILE
    #~ sed -i "$d" /tmp/search-result.json
    echo "]}" >> $TMP_SEARCH_RESULT_FILE
    sed -i '1 s/^.*$/{\"results\" : [/' $TMP_SEARCH_RESULT_FILE
    
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
        local readonly SEARCH_STRING="$SYMBOL"
        
        codesearch_search "$NAME" "$SYMBOL" "$REGEXP" "$SEARCH_STRING" 
        
    done
    echo "Done"
    unite
    echo "Done"
}


main
