#!/bin/bash

# Generate a string with the names of the phenotypes
# Example: generate_pheno_names 1 3
# Output: pheno1,pheno2,pheno3
generate_pheno_names() {
    local start=$1
    local end=$2
    local result=""

    for (( i=start; i<=end; i++ )); do
        if [[ $i -eq $start ]]; then
            result="pheno$i"
        else
            result="$result,pheno$i"
        fi
    done

    echo "$result"
}

