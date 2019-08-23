#!/usr/bin/python
# -*- coding: utf-8 -*-
# Author: bboysoul
import requests
import json
import sys
import os
 
headers = {'Content-Type': 'application/json;charset=utf-8'}
api_url = "https://oapi.dingtalk.com/robot/send?access_token=92bfa50db10658ee1c37f9ab6b7a000e14ce94a901002170762e472af3754fbf"
 
def msg(text):
    json_text= {
     "msgtype": "text",
        "at": {
            "atMobiles": [
                "user"
            ],
            "isAtAll": False
        },
        "text": {
            "content": text
        }
    }
    print requests.post(api_url,json.dumps(json_text),headers=headers).content
     
if __name__ == '__main__':
    text = sys.argv[1]
    msg(text)
