import subprocess

def run_swiss_army_knife(data_file_dir, filename, run_plink_qc, *args, **kwargs):
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
    tag = kwargs.get('tag', 'Array QC')
    output_dir = kwargs.get('output_dir', '/default/output/dir')

    # Prepare base command with input files
    command = [
        "dx", "run", "swiss-army-knife",
        f"-iin={data_file_dir}/{filename}.bed",
        f"-iin={data_file_dir}/{filename}.bim",
        f"-iin={data_file_dir}/{filename}.fam",
        f"-iin=/Data/ischemia_df.phe",
        f"-icmd={run_plink_qc}",
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

# Example usage
data_file_dir = "/my/data/files"
filename = "sample"
run_plink_qc = "plink --bfile sample --qc"
additional_input_files = ["/my/data/extra1.txt", "/my/data/extra2.txt"]

result = run_swiss_army_knife(
    data_file_dir=data_file_dir, 
    filename=filename, 
    run_plink_qc=run_plink_qc,
    *additional_input_files,  # Passing additional input files
    output_dir="/my/output/dir",  # Using **kwargs to specify output_dir
    instance_type="mem1_ssd1_v2_x36",  # Custom instance type
    tag="Custom Tag"  # Custom tag
)

print(result)
