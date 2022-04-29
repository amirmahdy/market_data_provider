import csv
import os


def create_csv(path, content, frmt="w"):
    path_dir = os.path.dirname(path)
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

    with open(path, frmt, encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(content)
    return True


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path