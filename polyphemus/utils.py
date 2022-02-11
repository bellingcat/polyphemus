# -*- coding: UTF-8 -*-

"""Utility functions for scraping video data from Odysee video platform.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import json

import requests 

from .base import OdyseeVideo

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def name_to_video_info(name):

    url = f"lbry://{name}"
    
    post_data = {
        "jsonrpc":"2.0",
        "method":"resolve",
        "params":{
            "urls":[url]}}

    api_url = 'https://api.na-backend.odysee.com/api/v1/proxy'

    response = requests.post(url = api_url, json = post_data)
    result = json.loads(response.text)
    
    return result['result'][url]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def name_to_video(name):

    video_info = name_to_video_info(name)
    video = OdyseeVideo(video_info)

    return video

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

