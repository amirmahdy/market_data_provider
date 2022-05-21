import csv
import os


def create_csv(path, content, fieldnames=None, frmt="w"):
    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    with open(path, frmt, encoding='UTF8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames) if fieldnames is not None else csv.writer(f)
        writer.writerows(content)
    return True


def read_csv(path, fieldnames=None):
    if not os.path.exists(path):
        return False

    with open(path, "r", encoding='UTF8', newline='') as f:
        reader = csv.DictReader(f, fieldnames=fieldnames) if fieldnames is not None else csv.reader(f)
        return [read for read in reader]


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path
