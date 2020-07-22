"""Deprecated. Download images from collface from a json file."""

import urllib.request
import json


with open('all_princeton_new.json') as js:
    js = json.loads(js.read())
    data = js['data']
    for student in data:
        img = 'https://collface.deptcpanel.princeton.edu/img/' + student['img']
        print(img)
        urllib.request.urlretrieve(img, 'img/' + student['img'])
