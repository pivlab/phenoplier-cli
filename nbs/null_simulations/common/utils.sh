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

# Function to process the input GWAS results and compress the output to a specified directory
# Example usage:
# compress_gwas "/path/to/input_file.txt" "/path/to/output_directory"
# Arguments:
#   1: Input file name
#   2: Output directory path (optional)
#   3: Apply zero-padding to phenotype ID (true/false, defaults to false)
compress_gwas() {
    local in_fpath="$1"
    local out_dpath="$2"
    local padding="${3:-no-phenoid-padding}"
    
    # If out_dpath is not provided, use the directory of the input file
    if [[ -z "$out_dpath" ]]; then
        out_dpath=$(dirname "$in_fpath")
    fi
    
    # Extract the base name of the input file (without directory)
    local base_name=$(basename "$in_fpath")
    echo "Processing file: $base_name"
    
    # Use regex to extract the three-digit phenotype ID (xxx in "phenoXXX")
    if [[ $base_name =~ pheno([0-9]+) ]]; then
        local pheno_id="${BASH_REMATCH[1]}"
        # Decide whether to pad the phenotype ID
        local padded_pheno_id
        if [[ "$padding" == "add-phenoid-padding" ]]; then
            padded_pheno_id=$(printf "%04d" "$pheno_id")  # Zero pad to 4 digits
        else
            padded_pheno_id="$pheno_id"  # No padding
        fi

        local out_fname="${out_dpath}/random.pheno${padded_pheno_id}.glm.linear.tsv.gz"
        local temp_out="${out_dpath}/random.pheno${padded_pheno_id}.glm.linear.tsv"  # Temporary file before compression

        # Debugging: print the extracted and padded phenotype ID
        echo "Extracted phenotype ID: $pheno_id"
        echo "Padded phenotype ID: $padded_pheno_id"

        # Use awk to match column names and extract the desired columns
        awk 'BEGIN { OFS="\t" }
        {
            if (NR == 1) {
                # Get the header and find the indices of the desired columns
                for (i = 1; i <= NF; i++) {
                    if ($i == "#CHROM") chrom_idx = i
                    if ($i == "POS") pos_idx = i
                    if ($i == "ID") id_idx = i
                    if ($i == "REF") ref_idx = i
                    if ($i == "A1") a1_idx = i
                    if ($i == "BETA") beta_idx = i
                    if ($i == "SE") se_idx = i
                    if ($i == "P") p_idx = i
                }
                # Print header for the selected columns
                print "#CHROM", "POS", "ID", "REF", "A1", "BETA", "SE", "P"
            } else {
                # Print selected columns based on their indices
                printf "%s\t%s\t%s\t%s\t%s\t%.7f\t%.7f\t%.6f\n", $chrom_idx, $pos_idx, $id_idx, $ref_idx, $a1_idx, $beta_idx, $se_idx, $p_idx
            }
        }' "$in_fpath" > "$temp_out"

        # Compress the output file into .tsv.gz format
        gzip -c "$temp_out" > "$out_fname"

        echo "Filtered and compressed data has been saved to $out_fname"

        # Clean up the temporary file
        rm "$temp_out"
    else
        echo "Error: Failed to extract phenotype ID from filename."
    fi
}

