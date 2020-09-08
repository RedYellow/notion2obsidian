# Purpose

Notion and Obsidian are two different notes apps; these scripts will download an export of the notes from your Notion account and set them up locally in your Obsidian folder. The scripts may be run consecutively (notion_exporter first), or separately if you just want to make sure you have a backup (set up a cron job running notion_exporter).

# Before running, fill out the config.yaml file. This will not work otherwise.

# Use

notion_exporter.py will download the backup of files from your Notion account as a zip file. The folder it downloads to and the name of the file can be set in the config file.

obsidian_converter.py will extract the file from the zip directly into the Obsidian vault that is set in the config file, and do some cleanup with regard to filenames and links between pages.
