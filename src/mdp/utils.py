import csv
import os
import zipfile
import fsutil


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


def create_zip_on_csv(path, zip_filename, csv_filename, rows):
    zip_file_path = path + zip_filename
    csv_file_path = path + csv_filename
    if fsutil.exists(zip_file_path):
        zipfile.ZipFile(zip_file_path, "r").extractall(path)
        fsutil.remove_file(zip_file_path)
    create_csv(csv_file_path, rows, fieldnames=None, frmt="a")
    zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED). \
        write(csv_file_path, arcname=csv_filename)
    fsutil.remove_file(csv_file_path)
    return True
