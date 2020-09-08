#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 09:25:34 2020

@author: Nic
"""
#THIS IS UNFINISHED
#MOSTLY TRANSLATED FROM https://github.com/connertennery/Notion-to-Obsidian-Converter

# from notion_exporter import export
import yaml
import os
import zipfile
# import tempfile
# from mdtable import MDTable
import re
import glob

config = yaml.safe_load(open("./config.yaml"))
EXPORT_DIR = config["EXPORT_DIR"]
EXPORT_FILENAME = config["EXPORT_FILENAME"]

EXTRACT_DIR = config["EXTRACT_DIR"]
if EXTRACT_DIR[-1] != "/":
    EXTRACT_DIR += "/"
if not os.path.isdir(EXTRACT_DIR):
    os.mkdir(EXTRACT_DIR)

def main():
    exports = [_ for _ in os.listdir(EXPORT_DIR) if EXPORT_FILENAME.split(".")[0] in _ and ".zip" in _]
    latest_export = max(exports, key=os.path.getctime)
 
    with zipfile.ZipFile(EXPORT_DIR+latest_export, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)
        parse_files()

def parse_files():
    #TODO: rewrite this recursively
    path = EXTRACT_DIR + '**'
    
    subdirs = [_ for _ in glob.iglob(path, recursive=True) \
               if os.path.isdir(_)]
    subdirs.reverse()
    # subdirs.sort(key=lambda x: len(x))
    for subdir in subdirs:
        os.rename(subdir, truncate_dir(subdir))
    
    files = [_ for _ in glob.iglob(path, recursive=True) if ".md" in _ or ".csv" in _]
    for file in files:
        # fullpath = os.path.join(EXTRACT_DIR, file)
        newpath = truncate_filename(file)
        os.rename(file, newpath)
        if file[-3:] == ".md":
            processMD(newpath)
        elif file[-4:] == ".csv":
            processCSV(newpath)
            

def processMD(fpath):
    with open(fpath, mode="r") as file:
        text = file.read()
        text = convert_relative_path(text)
    with open(fpath, mode="w") as file:
        file.write(text)
        

def processCSV(fpath):
    # markdown = MDTable(fpath)
    # markdown_string_table = markdown.get_table()
    with open(fpath, mode="r") as file:
        text = file.read()
        text = convert_relative_path(text)
        
        #convert the csv to a markdown table
        #TODO: remove the " " after conversion
        text = re.sub("(\,)(?=(\S)|(\n)|($))", r"|", text)
        lines = text.split("\n")
        lines.insert(1, "|-"*lines[0].count("|"))
    with open(fpath[:-4]+".md", mode="w") as file:
        file.write("\n".join(lines))

def truncate_dir(filename):
    if "DS_Store" in filename:
        return filename
    parts = filename.split("/")
    file = parts[-1]
    file = re.sub(" [a-z0-9]{25,}(?=/|.|$)", "", file)
    return "/".join(parts[:-1]+[file])

def truncate_filename(filename):
    if "DS_Store" in filename:
        return filename
    return re.sub(" [a-z0-9]{25,}(?=/|.|$)", "", filename)


def convert_relative_path(text):
    # removes the uuid from the links
    text = re.sub("%20[a-z0-9]{25,}(?=/|\.csv|\.md|$)", "", text)
    # changes links to csvs into links to the md generated in processCSV
    return re.sub("(\[.*?\]\(.*?).csv\)", r"\1.md)", text)
    # return re.sub("%20[a-z0-9]{25,}(?=/|\.csv|\.md|$)", "", path.group())
    # return "[[" + " ".join(path.group().split('/').pop().split('%20')[:-1]) + "]]"

if __name__ == "__main__":
    main()