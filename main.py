#!/usr/bin/python3
# Author: Michal Kodad, David Kolář

import requests
import sys
import re
import os


def print_help():
    print("Call me with `-ini` param", file=sys.stderr)
    sys.exit(1)


hash_map = {}


def process_content(root_url, path):
    global hash_map
    response = requests.get(f"{root_url}/{path}")
    if response.status_code != 200:
        print("----- Skipped ----- ", response.url, file=sys.stderr)
        return
    print("Processing page: ", response.url, file=sys.stderr)

    # odstranění všeho kromě tag div s hlavním obsahem (content)
    content = re.sub(r"^.*<div id='content'>", '', response.text, flags=re.DOTALL)
    content = re.sub(r"<div id='sidebar-wrapper'>.*", '', content, flags=re.DOTALL)

    # odstranění HTML entit
    content = re.sub(r'&.*?;', ' ', content, flags=re.DOTALL)

    # odstranění tagů
    content = re.sub(r'<.*?>', ' ', content, flags=re.DOTALL)

    content = content.lower()

    for word in re.findall(r'\w+', content):
        if (word in hash_map):
            if (f"/{path}" not in hash_map[word]):
                hash_map[word].append(f"/{path}")
        else:
            hash_map[word] = [f"/{path}"]


def preprocess():
    root_url = "http://ksp.mff.cuni.cz"
    root_nodes = ['h/ulohy', 'z/ulohy']
    pages = ['zadani', 'reseni', 'komentare']

    for node in root_nodes:
        for year in range(35):
            for series in range(1, 6):
                for page in pages:
                    process_content(root_url, f"{node}/{year}/{page}{series}.html")


PREPROCESSED_FILE = "preprocessed.txt"

if len(sys.argv) >= 2:
    if sys.argv[1] == '-ini':
        preprocess()

        with open(PREPROCESSED_FILE, "w") as db:
            for words in sorted(list(hash_map.keys())):
                for word in hash_map[words]:
                    db.write(f"{words} {word}\n")
        print("Success", file=sys.stderr)
        sys.exit(0)

    print_help()

try:
    with open(PREPROCESSED_FILE, "r") as file:
        for line in file.readlines():
            key, value = line.split()
            if (key in hash_map):
                hash_map[key].append(value)
                continue
            hash_map[key] = [value]
except FileNotFoundError:
    print_help()

while(True):
    word_to_find = input()
    word_to_find = word_to_find.lower()
    if (word_to_find not in hash_map):
        print(f"Word `{word_to_find}`not found in {PREPROCESSED_FILE}")
        continue
    for word in hash_map[word_to_find]:
        print("https://ksp.mff.cuni.cz"+word)



