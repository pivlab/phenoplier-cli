import os
import numpy as np
import filecmp
from pathlib import Path


def compare_metadata_npz_files(dir1, dir2):
    """
    Special handling for 'metadata.npz' files to compare case-insensitively.
    New results are saved with upper-case keys while old results are saved with lower-case keys.
    This function servers as an ad-hoc solution.
    """
    # Special handling for 'metadata.npz'
    file1 = Path(dir1) / 'metadata.npz'
    file2 = Path(dir2) / 'metadata.npz'
    if not file1.exists() or not file2.exists():
        return False, "metadata.npz file not found in both directories."
    # Load the .npz files
    npz1 = np.load(file1)
    npz2 = np.load(file2)
    print(f"Comparing metadata.npz files...")
    for key in npz1.files:
        if key not in npz2.files:
            return False, f"Key {key} not found in both metadata.npz files."
        array1 = npz1[key]
        array2 = npz2[key]

        if array1.dtype.kind in {'U', 'S'} and array2.dtype.kind in {'U', 'S'}:
            if not np.array_equal(np.char.lower(array1), np.char.lower(array2)):
                return False, f"Arrays under key {key} in metadata.npz are not case-insensitively equal."
        else:
            if not np.array_equal(array1, array2):
                return False, f"Arrays under key {key} in metadata.npz are not equal."
    return True, "All metadata.npz files are equal."


def compare_npz_files(dir1, dir2, rtol=1e-5, atol=1e-8, ignore_files=None):
    if ignore_files is None:
        ignore_files = []

    # Get list of .npz files in both directories, excluding ignored files
    files1 = sorted([f for f in os.listdir(dir1) if f.endswith('.npz') and f not in ignore_files])
    files2 = sorted([f for f in os.listdir(dir2) if f.endswith('.npz') and f not in ignore_files])

    # Check if the number of files is the same
    if len(files1) != len(files2):
        return False, "Number of files in the directories are not the same."

    # Compare files
    for file1, file2 in zip(files1, files2):
        if file1 != file2:
            return False, f"File names do not match: {file1} vs {file2}"

        print(f"Comparing {file1}...")
        # Load the .npz files
        npz1 = np.load(os.path.join(dir1, file1))
        npz2 = np.load(os.path.join(dir2, file2))

        # Check if all arrays in the .npz files are close
        for key in npz1.files:
            if key not in npz2.files:
                return False, f"Key {key} not found in both .npz files."
            array1 = npz1[key]
            array2 = npz2[key]

            # Handle different data types
            if array1.dtype != array2.dtype:
                return False, f"Arrays under key {key} in file {file1} have different data types: {array1.dtype} vs {array2.dtype}"

            if np.issubdtype(array1.dtype, np.number) and np.issubdtype(array2.dtype, np.number):
                if not np.allclose(array1, array2, rtol=rtol, atol=atol):
                    return False, f"Arrays under key {key} in file {file1} are not close."
            else:
                if not np.array_equal(array1, array2):
                    return False, f"Non-numeric arrays under key {key} in file {file1} are not equal."

    return True, "All files are equal or close in value."


def inspect_metadata():
    dir1 = '/media/haoyu/extradrive1/proj_data/phenoplier-cli/rapid_gwas_cli_run/6-generate/mashr/gene_corrs-symbols-within_distance_5mb.per_lv'
    dir2 = '/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv'
    md1 = dir1 + '/metadata.npz'
    md2 = dir2 + '/metadata.npz'
    npz1 = np.load(md1)
    npz2 = np.load(md2)
    print(npz1['data'])
    print()
    print(npz2.files)
    print(filecmp.cmp(md1, md2))


def test2():
    # Create directories
    Path('dir1').mkdir(exist_ok=True)
    Path('dir2').mkdir(exist_ok=True)

    # Create the first .npz file in dir1
    np.savez('dir1/metadata.npz', key1=np.array(['value1', 'value2']), key2=np.array([1, 2, 3]))

    # Create the second .npz file in dir2 with different values
    np.savez('dir2/metadata.npz', key1=np.array(['VALUE1', 'value2']), key2=np.array([1, 2, 3, 4]))
    # Run the test
    result, message = compare_metadata_npz_files('dir1', 'dir2')
    print(result, message)
    # Clean up
    os.remove('dir1/metadata.npz')
    os.remove('dir2/metadata.npz')


if __name__ == "__main__":
    dir1 = '/media/haoyu/extradrive1/proj_data/phenoplier-cli/rapid_gwas_cli_run/6-generate/mashr/gene_corrs-symbols-within_distance_5mb.per_lv'
    dir2 = '/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_rapid_gwas/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv'
    # dir2 = "/media/haoyu/extradrive1/alpine_data/pivlab/data/phenoplier/results/gls/gene_corrs/cohorts/phenomexcan_other/gtex_v8/mashr/gene_corrs-symbols-within_distance_5mb.per_lv"
    ignore_files = ['metadata.npz']
    result, message = compare_npz_files(dir1, dir2, ignore_files=ignore_files)
    print(message)
    # Check metadata.npz files
    result, message = compare_metadata_npz_files(dir1, dir2)
    print(message)
    test2()