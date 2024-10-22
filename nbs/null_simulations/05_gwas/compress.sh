#!/bin/bash

# Function to process the input file and compress the output to a specified directory
process_and_compress() {
    local in_fname="$1"
    local out_dirpath="$2"
    
    # Extract the base name of the input file (without directory and extension)
    local base_name=$(basename "$in_fname" .txt)
    local out_fname="${out_dirpath}/${base_name}.tsv.gz"
    local temp_out="${out_dirpath}/${base_name}.tsv"  # Temporary file before compression

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
    }' "$in_fname" > "$temp_out"

    # Compress the output file into .tsv.gz format
    gzip -c "$temp_out" > "$out_fname"

    echo "Filtered and compressed data has been saved to $out_fname"

    # Clean up the temporary file
    rm "$temp_out"
}

# Example usage
# process_and_compress "/path/to/input_file.txt" "/path/to/output_directory"
