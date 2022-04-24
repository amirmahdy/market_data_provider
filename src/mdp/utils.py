import csv
import os


def create_csv(header, path, content):
    with open(path, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for item in content:
            data = [item["t"], item["q"], item["p"]]
            writer.writerow(data)
    return True


def check_path(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return path
