#!/bin/bash

# Input and output file paths
# input_file="/mnt/data/proj_data/phenoplier-cli/nullsimi-millton/plink_gwas.plink2.pheno100.glm.linear.assoc.txt"
# output_file="/mnt/data/proj_data/phenoplier-cli/nullsimi-millton/random.pheno100.glm.linear.txt"
input_file="/mnt/data/proj_data/phenoplier-cli/ukb-nullsim/random.pheno100.glm.linear.txt"
output_file="/mnt/data/proj_data/phenoplier-cli/ukb-nullsim/r_random.pheno100.glm.linear.txt"

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
}' "$input_file" > "$output_file"

echo "Filtered data has been saved to $output_file"
