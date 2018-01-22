#!/bin/bash


readonly BASE_OUTPUT_FILE=/tmp/output
readonly BASE_RESULT_FILE=/tmp/result
readonly FORMAT_FILE=format.json

main() {
    local readonly FORMAT_INDEX=$(cat $FORMAT_FILE | jq 'keys' | jq '.[]')
    
    for f in $FORMAT_INDEX; do
        cat $FORMAT_FILE | jq ".[$f].name"
        local readonly REGEXP=$(cat $FORMAT_FILE | jq ".[$f].wallet_regexp")
        local readonly SYMBOL=$(cat $FORMAT_FILE | jq --raw-output ".[$f].symbol")
        
        local readonly RESULT_FILE="$BASE_RESULT_FILE-$SYMBOL.json"
        local readonly SEARCH_STRING="$SYMBOL+donation"
        
        # 0..49 are the allowed result page for the searchcode api
        for p in {0..49}; do
            local readonly OUTPUT_FILE="$BASE_OUTPUT_FILE-$SYMBOL-$p.json"
            local readonly RESULT_FILE="$BASE_RESULT_FILE-$SYMBOL-$p.json"
            
            # Download the json file containing the infos
            curl -s -o $OUTPUT_FILE https://searchcode.com/api/codesearch_I/?q=$SEARCH_STRING&p=$p&per_page=100&loc=5
            
            #~ # Extract the "result" key from the json file and store it in $TMP_RESULT_FILE
            cat $OUTPUT_FILE | jq '.' |  jq '.["results"]' > $RESULT_FILE
            
            #~ # Extract the indices of the result_file
            local readonly KEYS=$(cat $RESULT_FILE | jq 'keys' | jq '.[]')
            
            for k in $KEYS; do
                local readonly TMP=$(cat $RESULT_FILE | jq ".[$k]")
                
                
                
                local readonly MATCH=$(echo $TMP | jq '.' | egrep -o "$REGEXP")
                #~ echo $TMP | jq '.' | egrep -o "$REGEXP"
                if [ "$MATCH" != "" ]; then # a match is found
                    echo "==="
                    echo $TMP | jq "."
                    echo $MATCH
                    local readonly REPOSITORY=$(echo $TMP | jq --raw-output ".repo" | sed 's/\.[^.]*$//')
                    local readonly RAW_REPOSITORY=$(echo $REPOSITORY | sed 's/github.com/raw.githubusercontent.com/')
                    local readonly DIRECTORY=$(echo $TMP | jq --raw-output ".location")
                    local readonly FILENAME=$(echo $TMP | jq --raw-output ".filename")
                    local URL=""
                    if [ "$DIRECTORY" == "" ]; then
                        URL=$RAW_REPOSITORY/master/$FILENAME
                    else
                        URL=$RAW_REPOSITORY/master/$DIRECTORY/$FILENAME
                    fi
                    echo $URL
                    echo "==="
                fi
            done
        done
    done
}


main
