"""
General utility functions.
"""
import re
import hashlib
import subprocess
import logging
import pyreadr
import pandas as pd

from pathlib import Path
from subprocess import run
from typing import Dict


logger = logging.getLogger(__name__)


def is_number(s):
    """
    Checks whether s is a number or not.

    Args:
        s (object): the object to check whether is a number or not.

    Returns:
        bool: Either True (s is a number) or False (s is not a number).
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def chunker(seq, size):
    """
    Divides a sequence in chunks according to the given size. For example, if
    given a list

        [0,1,2,3,4,5,6,7]

    and size is 3, it will return

        [[0, 1, 2], [3, 4, 5], [6, 7]]
    """
    return (seq[pos : pos + size] for pos in range(0, len(seq), size))


def curl(url: str, output_file: str, md5hash: str = None, logger=None):
    """Downloads a file from an URL. If the md5hash option is specified, it checks
    if the file was successfully downloaded (whether MD5 matches).

    Before starting the download, it checks if output_file exists. If so, and md5hash
    is None, it quits without downloading again. If md5hash is not None, it checks if
    it matches the file.

    Args:
        url: URL of file to download.
        output_file: path of file to store content.
        md5hash: expected MD5 hash of file to download.
        logger: Logger instance.
    """

    Path(output_file).resolve().parent.mkdir(parents=True, exist_ok=True)

    if Path(output_file).exists() and (
        md5hash is None or md5_matches(md5hash, output_file)
    ):
        logger.info(f"File already downloaded: {output_file}")
        return

    logger.info(f"Downloading {output_file}")
    run(["curl", "-s", "-L", url, "-o", output_file])

    if md5hash is not None and not md5_matches(md5hash, output_file):
        msg = "MD5 does not match"
        logger.error(msg)
        raise AssertionError(msg)


def md5_matches(expected_md5: str, filepath: str) -> bool:
    """Checks the MD5 hash for a given filename and compares with the expected value.

    Args:
        expected_md5: expected MD5 hash.
        filepath: file for which MD5 will be computed.

    Returns:
        True if MD5 matches, False otherwise.
    """
    with open(filepath, "rb") as f:
        current_md5 = hashlib.md5(f.read()).hexdigest()
        return expected_md5 == current_md5


def generate_result_set_name(
    method_options: Dict, options_sep: str = "-", prefix: str = None, suffix: str = None
) -> str:
    """Generates a filename for a result set with the method's options given.

    When a method is run with several options (like a clustering/classification
    algorithm) and its results need to be saved to a file, this method generates a
    descriptive filename using the given options.

    Args:
        method_options: dictionary with parameter names and their values.
        options_sep: options separator.
        prefix: optional prefix for the filename.
        suffix: optional suffix (like a filename extension).
    Returns:
        A filename as a str object.
    """

    def simplify_option_name(s: str) -> str:
        # s = s.lower()

        # remove any non-allowed character
        s = re.sub(r"[^\w\s\-_]", "", s)

        s = re.sub(r"-", "_", s)

        return s

    def simplify_option_value(s) -> str:
        if isinstance(s, str):
            return simplify_option_name(s)
        elif isinstance(s, (list, tuple, set)):
            return "_".join(simplify_option_name(str(x)) for x in s)
        else:
            return simplify_option_name(str(s))

    output_file_suffix = options_sep.join(
        [
            f"{simplify_option_name(k)}_{simplify_option_value(v)}"
            for k, v in sorted(method_options.items(), reverse=False)
        ]
    )

    filename = output_file_suffix

    if prefix is not None:
        filename = f"{prefix}{filename}"

    if suffix is not None:
        filename = f"{filename}{suffix}"

    return filename


def get_git_repository_path():
    """
    Returns the Git repository path. If for any reason running git fails, it
    returns the operating system temporary folder.
    """
    try:
        results = run(["git", "rev-parse", "--show-toplevel"], stdout=subprocess.PIPE)

        return Path(results.stdout.decode("utf-8").strip())
    except Exception:
        import tempfile

        return Path(tempfile.gettempdir())


def remove_all_file_extensions(filepath: Path, extensions: list = None):
    """
    Removes all the extensions/suffices from a Path object (file).
    """

    def _remove_next_suffix(f):
        if extensions is not None and len(extensions) > 0:
            return f.suffix in extensions
        return len(f.suffix) > 0

    while _remove_next_suffix(filepath):
        filepath = filepath.with_suffix("")

    return filepath


def read_log_file_and_check_line_exists(log_file: str, expected_prefixes: list):
    """
    Reads a log file and checks whether at least one line in the log file starts with all the expected lines prefixes
    (strings) given.

    Args:
        log_file: path to the log file.
        expected_prefixes: list of expected lines prefixes (str).

    Returns:
        Always None. If an expected line prefix is not found in the log file, an exception will be raised.
    """
    with open(log_file, "r") as f:
        lines = f.readlines()

    def _line_exists(line):
        return any([l.startswith(line) for l in lines])

    for expected_l in expected_prefixes:
        if not _line_exists(expected_l):
            raise ValueError(f"Line '{expected_l}' not found in {str(log_file)}")


def get_sha1(filepath, blocksize=65536):
    hasher = hashlib.sha1()
    with open(filepath, 'rb') as afile:
        buf = afile.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(blocksize)
    return hasher.hexdigest()


def run_command(command, raise_on_error=True):
    r = run(command, shell=True)

    if raise_on_error and r.returncode != 0:
        raise Exception(f'Command "{command}" failed with code {r.returncode}')

    return r


def read_rds(rds_path: Path) -> pd.DataFrame:
    """Reads an RDS file and converts it to a pandas DataFrame.

    Args:
        rds_path (Path): Path to the RDS file.

    Returns:
        pd.DataFrame: DataFrame containing the data from the RDS file.
    """
    result = pyreadr.read_r(str(rds_path))
    return result[None]
