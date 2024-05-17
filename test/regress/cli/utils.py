import csv
from math import isclose


def diff_tsv(file1, file2, epsilon=1e-6) -> bool:
    """
    Compare if two tsv files contain the same contents. A threshold can be provided to tolerate floating
    point errors. Return true if there's any difference, ture otherwise.
    """

    def read_tsv(filename):
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            return {row[reader.fieldnames[0]]: row for row in reader}

    def are_rows_equal(row1, row2, epsilon):
        for key in row1:
            if key in row2:
                try:
                    # Try to compare as floats
                    if not isclose(float(row1[key]), float(row2[key]), abs_tol=epsilon):
                        return False
                except ValueError:
                    # If conversion to float fails, compare as strings
                    if row1[key] != row2[key]:
                        return False
            else:
                return False
        return True

    data1 = read_tsv(file1)
    data2 = read_tsv(file2)

    keys1 = set(data1.keys())
    keys2 = set(data2.keys())

    diff = {}
    # Check for differences in entries
    for key in keys1.union(keys2):
        if key not in data2:
            diff[key] = {'status': 'Missing in file2', 'data': data1[key]}
        elif key not in data1:
            diff[key] = {'status': 'Missing in file1', 'data': data2[key]}
        elif not are_rows_equal(data1[key], data2[key], epsilon):
            diff[key] = {'status': 'Different', 'file1_data': data1[key], 'file2_data': data2[key]}

    if diff:
        for key, value in diff.items():
            print(f"Key: {key}, Status: {value['status']}")
            if value['status'] == 'Different':
                print(f"File1 Data: {value['file1_data']}")
                print(f"File2 Data: {value['file2_data']}")
            else:
                print(f"Data: {value['data']}")
        return True
    else:
        print(f"Both files are identical given an acceptable floating point error threshold: {epsilon}")
        return False
