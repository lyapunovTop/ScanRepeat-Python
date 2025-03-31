import os
import sys
import hashlib
import json

"""
{
    "md5-value1": [file1_path, file2_path],
    "md5-value2": [file3_path, file4_path],
}
"""

OUTFILE = "outfile.json"


def search_files(dir_path):
    result = []
    file_list = os.listdir(dir_path)
    for file_name in file_list:
        try:
            complete_file_name = os.path.join(dir_path, file_name)
            print("search: " + complete_file_name)
            if os.path.isdir(complete_file_name):
                result.extend(search_files(complete_file_name))
            if os.path.isfile(complete_file_name):
                result.append(complete_file_name)
        except:
            print("find the file cannot be decoded, skip") 
            continue
    return result


#block 500MB
def calc_file_md5(f, block_size=(2 ** 20) * 500):
    md5_hash = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5_hash.update(data)
    return md5_hash.hexdigest()


def get_repeat(file_list) -> dict:
    database = {}
    for file in file_list:
        with open(file, "rb") as f:
            file_size = os.stat(file).st_size
            print("read file[size:{:,d}]: {:s}".format(file_size, file))
            md5 = calc_file_md5(f)
            if md5 not in database:
                database[md5] = []
                database[md5].append(file)
            else:
                database[md5].append(file)
    with open(OUTFILE, "a") as out:
        json.dump(database, out, indent=4)
    return database


def main(dir_name):
    if os.path.exists(OUTFILE):
        os.remove(OUTFILE)
    file_list = search_files(dir_name)
    database = get_repeat(file_list)
    print("list len: " + len(file_list))
    print("database len: " + len(database))


def remove_repeat(database_file):
    with open(database_file, "r") as f:
        database = json.load(f)
    for md5 in database:
        count = len(database[md5])
        for file in database[md5]:
            if count > 1:
                os.remove(file)
                count -= 1
            else:
                break

def print_result(database_file):
    with open(database_file, "r") as f:
        database = json.load(f)
    for md5 in database:
        count = len(database[md5])
        print("md5[{:s}], find [{:d}] files".format(md5,count))
        for file in database[md5]:
            if(count) > 1:
                print("duplicated file: " + file)
#            else:
#                print("file: " + file)
            


if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[1] == "scan":
            main(sys.argv[2])
        elif sys.argv[1] == "result":
            print_result(sys.argv[2])
        elif sys.argv[1] == "remove":
            remove_repeat(sys.argv[2])
    else:
        print("scan and remove repeat files")
        print("scan: python main.py scan <dir_path>")
        print("result: python main.py result <output.json>")
        print("remove: python main.py remove <output.json>")

