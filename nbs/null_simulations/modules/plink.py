from utils import trim_spaces, remove_newline


def generate_pheno_names(start, end):
    return ",".join([f"pheno{i}" for i in range(start, end+1)])


def build_plink_nullsim_command(
    bgen_filename,
    pheno,
    pheno_name,
    sample,
    covar,
    covar_name = "sex,age,pc1,pc2,pc3,pc4,pc5,pc6,pc7,pc8,pc9,pc10",
    mac=50,
    maf=0.01,
):
    command = f"""plink2 \
        --bgen {bgen_filename} \
        --covar {covar} \
        --covar-name {covar_name} \
        --mac {mac} --maf {maf} \
        --pheno {pheno} \
        --pheno-name {pheno_name} \
        --sample {sample} \
        --threads $(nproc --all)
        """
    
    return trim_spaces(remove_newline(command))

