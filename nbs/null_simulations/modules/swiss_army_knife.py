import subprocess
from plink import build_plink_nullsim_command, generate_pheno_names

def run_swiss_army_knife(plink_cmd, *args, **kwargs):
    """
    Python wrapper for the 'dx run swiss-army-knife' command using *args and **kwargs.
    
    :param data_file_dir: Directory path where the .bed, .bim, and .fam files are located.
    :param filename: Prefix for the input file (.bed, .bim, .fam).
    :param run_plink_qc: Plink QC command to run.
    :param *args: Additional input files to be added dynamically.
    :param **kwargs: Keyword arguments like instance_type, tag, destination.
                     Accepts 'instance_type', 'tag', and 'output_dir' as optional arguments.
    :return: The output of the command execution.
    """
    # Set default keyword argument values
    instance_type = kwargs.get('instance_type', 'mem1_ssd1_v2_x36')
    tag = kwargs.get('tag', 'NA')
    output_dir = kwargs.get('output_dir', '/default/output/')

    # Prepare base command with input files
    command = [
        "dx", "run", "swiss-army-knife",
        f"-icmd={plink_cmd}",
        f"--tag={tag}",
        f"--instance-type={instance_type}",
        f"--destination={output_dir}",
        "--brief", "--yes"
    ]

    # Add additional input files passed through *args
    for additional_input in args:
        command.insert(1, f"-iin={additional_input}")

    try:
        # Run the command
        result = subprocess.run(command, text=True, check=True, capture_output=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return e.stdout if e.stdout else e.stderr


def run_plink_nullsim(bgen_file,
                      pheno_file,
                      start_pheno,
                      end_pheno,
                      sample_file,
                      covariate_file,
                      output_dir,
                      filename,
                      *args,
                      **kwargs):
    pheno_names = generate_pheno_names(start_pheno, end_pheno)
    plink_cmd = build_plink_nullsim_command(bgen_file, pheno_file, pheno_names, sample_file, covariate_file, args, output_dir=output_dir)
    run_swiss_army_knife(plink_cmd)
