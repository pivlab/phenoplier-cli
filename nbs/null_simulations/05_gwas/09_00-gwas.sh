#!/bin/bash
source ../common/utils.sh

# Parameters to specify the range and batch size
start_pheno=0
end_pheno=199
batch_size=200

# Other constants
job_name="\"PhenoPLIER Null Simulation GWAS\""
pheno_file_name="random_phenotypes_df.phe"
pheno_file="/phenoplier/null_sim/00-data/${pheno_file_name}"
covar_names="sex,age,pc1,pc2,pc3,pc4,pc5,pc6,pc7,pc8,pc9,pc10"
bgen_path="/Bulk/Imputation/Imputation from genotype (GEL)"
sample_path="/Bulk-DRL/GEL_imputed_sample_files_fixed"
data_field="ukb21008"
instance_type="mem2_ssd1_v2_x64"
priority="low"
bgen_name="ukb21008_c2_b0_v1.bgen"
output_dir_base="phenoplier/null_sim/01-output"
tag_base=""
plink_app_id="app-GZZ4vB008Qyk3644pZfjbxP2" # Plink v1.0.8

# Function to split phenotypes into batches and run the GWAS command for each batch
run_gwas_batch() {
    local batch_start=$1
    local batch_end=$2

    # Create a tag and output dir based on the batch
    local output_dir="${output_dir_base}/${batch_start}-${batch_end}/"
    local tag="${batch_start}-${batch_end}"

    # Generate phenotype names for this batch
    pheno_names=$(generate_pheno_names ${batch_start} ${batch_end})

    # Declare long options for the command
    bgen_arg=""
    sample_arg=""
    extra_options="\""
    extra_options+="hide-covar --maf 0.01 --mac 50 "
    extra_options+="--pheno-name ${pheno_names} "
    extra_options+="--covar-name ${covar_names}"
    extra_options+="\""

    # Run on 22 chromosomes
    for i in {1..22}; do
        bgen_arg+="-igenotypes_bgens=\"${bgen_path}/${data_field}_c${i}_b0_v1.bgen\" "
        sample_arg+="-isample_ids_sample=\"${sample_path}/${data_field}_c${i}_b0_v1.sample\" "
    done

    # Build the command
    command="dx run ${plink_app_id} \
        --name ${job_name} \
        --instance-type ${instance_type} \
        --tag ${tag} \
        --priority ${priority} \
        --destination=${output_dir} \
        ${bgen_arg} ${sample_arg} \
        -iphenotypes_pheno=${pheno_file} \
        -icovariates_cov=${pheno_file} \
        -iextra_options=${extra_options}"

    # Print the command for debugging
    echo "Running GWAS for phenotypes ${batch_start} to ${batch_end}:"
    echo "${command}"

    # Run the command
    eval "${command}"
}

# Main loop to split the phenotypes into batches and run the GWAS command for each batch
# For example:
# With start_pheno=0, end_pheno=999, and batch_size=200, the script will create 5 batches:
# Batch 1: Phenotypes 0 to 199
# Batch 2: Phenotypes 200 to 399
# Batch 3: Phenotypes 400 to 599
# Batch 4: Phenotypes 600 to 799
# Batch 5: Phenotypes 800 to 999

for ((batch_start=${start_pheno}; batch_start<=${end_pheno}; batch_start+=${batch_size})); do
    batch_end=$((batch_start + batch_size - 1))

    # Ensure batch_end does not exceed end_pheno
    if [[ ${batch_end} -gt ${end_pheno} ]]; then
        batch_end=${end_pheno}
    fi

    # Call the function to run GWAS for this batch
    run_gwas_batch ${batch_start} ${batch_end}
done