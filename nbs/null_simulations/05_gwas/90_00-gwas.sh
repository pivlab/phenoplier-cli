#!/bin/bash
source ../common/utils.sh

start_pheno=700
end_pheno=899

pheno_file_name="random_phenotypes_df.phe"
pheno_file="/phenoplier/null_sim/data/${pheno_file_name}"
pheno_names=$(generate_pheno_names ${start_pheno} ${end_pheno})
covar_names="sex,age,pc1,pc2,pc3,pc4,pc5,pc6,pc7,pc8,pc9,pc10"
bgen_path="/Bulk/Imputation/Imputation from genotype (GEL)"
bgen_name="ukb21008_c2_b0_v1.bgen"
sample_path="/Bulk-DRL/GEL_imputed_sample_files_fixed" # Path to the fixed sample file
data_field="ukb21008"
output_dir="phenoplier/null_sim/output/${start_pheno}-${end_pheno}/"
instance_type="mem1_ssd1_v2_x36"
priority="low"
tag="${start_pheno}-${end_pheno}"


# Declare long options
bgen_arg=""
sample_arg=""
extra_options="\""
extra_options+="hide-covar --maf 0.01 --mac 50 --covar-name sex,age,pc1,pc2,pc3,pc4,pc5,pc6,pc7,pc8,pc9,pc10 "
extra_options+="--pheno-name ${pheno_names}"
extra_options+="\""

# Run on 22 chromosomes
for i in {1..22}; do
    bgen_arg+="-igenotypes_bgens=\"${bgen_path}/${data_field}_c${i}_b0_v1.bgen\" "
    sample_arg+="-isample_ids_sample=\"${sample_path}/${data_field}_c${i}_b0_v1.sample\" "
done

command="dx run 
    --instance-type ${instance_type} \
    --tag ${tag} \
    --priority ${priority} \
    --destination=${output_dir}
    plink_gwas ${bgen_arg} ${sample_arg} \
    -iphenotypes_pheno=${pheno_file} \
    -icovariates_cov=${pheno_file} \
    -iextra_options=${extra_options}"
echo $command
eval $command