import os
import sys
import hashlib
import asyncio
import aiofiles
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
        complete_file_name = os.path.join(dir_path, file_name)
        if os.path.isdir(complete_file_name):
            result.extend(search_files(complete_file_name))
        if os.path.isfile(complete_file_name):
            result.append(complete_file_name)
    return result


async def get_repeat(file_list) -> dict:
    database = {}
    for file in file_list:
        async with aiofiles.open(file, "rb") as f:
            data = await f.read()
            md5 = hashlib.md5(data).hexdigest()
            if md5 not in database:
                database[md5] = []
                database[md5].append(file)
            else:
                database[md5].append(file)
    with open(OUTFILE, "a") as out:
        json.dump(database, out, indent=4)
    return database


async def main(dir_name):
    if os.path.exists(OUTFILE):
        os.remove(OUTFILE)
    file_list = search_files(dir_name)
    database = await get_repeat(file_list)
    print(len(file_list))
    print(len(database))


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


if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[1] == "scan":
            asyncio.run(main(sys.argv[2]))
        elif sys.argv[1] == "remove":
            remove_repeat(sys.argv[2])
    else:
        print("scan and remove repeat files")
        print("scan: python main.py scan <dir_path>")
        print("remove: python main.py remove <output.json>")
