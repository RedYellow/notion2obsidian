#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 31 13:33:33 2020

@author: Nic

Copied from https://gitlab.com/aburtsev/notion-backup-script/-/raw/master/.gitlab-ci.yml
"""
import json
import time
import urllib

from datetime import datetime
import yaml

# config_loc = os.path.realpath(os.path.join(os.getcwd(),"config.yaml"))
config = yaml.safe_load(open("./config.yaml"))

OVERWRITE = config["OVERWRITE"]
timestamp = "" if OVERWRITE else datetime.now().strftime("%d-%m-%Y (%I.%M.%S %p)")

TZ = config["TZ"]
NOTION_API = config["NOTION_API"]
EXPORT_DIR = config["EXPORT_DIR"]
EXPORT_FILENAME = EXPORT_DIR+config["EXPORT_FILENAME"][:-4]+" "+timestamp+".zip"
NOTION_TOKEN_V2 = config["NOTION_TOKEN_V2"]
NOTION_SPACE_ID = config["NOTION_SPACE_ID"]


ENQUEUE_TASK_PARAM = {
    "task": {
        "eventName": "exportSpace", "request": {
            "spaceId": NOTION_SPACE_ID,
            "exportOptions": {"exportType": "markdown", "timeZone": TZ, "locale": "en"}
        }
    }
}


def request(endpoint: str, params: object):
    req = urllib.request.Request(
        f'{NOTION_API}/{endpoint}',
        data=json.dumps(params).encode('utf8'),
        headers={
            'content-type': 'application/json',
            'cookie': f'token_v2={NOTION_TOKEN_V2}; '
        },
    )
    response = urllib.request.urlopen(req)
    return json.loads(response.read().decode('utf8'))


def export():
    task_id = request('enqueueTask', ENQUEUE_TASK_PARAM).get('taskId')
    print(f'Enqueued task {task_id}')

    while True:
        time.sleep(2)
        tasks = request("getTasks", {"taskIds": [task_id]}).get('results')
        task = next(t for t in tasks if t.get('id') == task_id)
        print(f'\rPages exported: {task.get("status").get("pagesExported")}', end="")

        if task.get('state') == 'success':
            break

    export_url = task.get('status').get('exportURL')
    print(f'\nExport created, downloading: {export_url}')

    urllib.request.urlretrieve(
        export_url, EXPORT_FILENAME,
        reporthook=lambda c, bs, ts: print(f"\r{int(c * bs * 100 / ts)}%", end="")
    )
    print(f'\nDownload complete: {EXPORT_FILENAME}')

if __name__ == "__main__":
    export()
