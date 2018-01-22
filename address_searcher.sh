#!/bin/bash


readonly search_term=(BTC LTC NMC DOGE XMR ETH)

main() {
    local readonly TMP_OUTPUT_FILE=/tmp/output.json
    local readonly TMP_RESULT_FILE=/tmp/result.json
    
    # 0..49 are the allowed result page for the searchcode api
    for p in {0..49}; do
        # Download the json file containing the infos
        curl -s -o $TMP_OUTPUT_FILE https://searchcode.com/api/codesearch_I/?q=BTC+donation&p=$p&per_page=100&lan=122&lan=118&lan=184&loc=5
        
        # Extract the "result" key from the json file and store it in $TMP_RESULT_FILE
        cat $TMP_OUTPUT_FILE | jq '.' |  jq '.["results"]' > $TMP_RESULT_FILE
            
        # Extract the indices of the result_file
        local readonly KEYS=$(cat $TMP_RESULT_FILE | jq 'keys' | jq '.[]')
        
        
        for k in $KEYS; do
            local readonly TMP=$(cat $TMP_RESULT_FILE | jq ".[$k]")
            
            echo $TMP | jq '.' | egrep -o '[13][0-9A-Za-z]{24,35}'
            if [ "$?" == "0" ]; then # a match is found
                local readonly REPO=$(echo $TMP | jq ".repo")
                local readonly FILENAME=$(echo $TMP | jq ".filename")
                local readonly URL=$REPO\/$FILENAME
                echo $URL
            fi
            echo "==="
        done
    done
}


main
