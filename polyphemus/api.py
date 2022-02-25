# -*- coding: UTF-8 -*-

"""Functions to request and process information from Odysee APIs
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import json
from urllib.parse import quote

import requests

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

#TODO Figure out how to reverse-engineer this
AUTH_TOKEN = 'BseGAiye641UqUsv4g31ZcUCRiLasv3U'

# API endpoints for Odysee data
#-----------------------------------------------------------------------------#

BACKEND_API_URL = 'https://api.na-backend.odysee.com/api/v1/proxy'
SUBSCRIBER_API_URL = 'https://api.odysee.com/subscription/sub_count'
VIEW_API_URL = 'https://api.odysee.com/file/view_count'
REACTION_API_URL = 'https://api.odysee.com/reaction/list'
COMMENT_API_URL = 'https://comments.odysee.com/api/v2'
RECOMMENDATION_API_URL = 'https://recsys.odysee.com/search'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_channel_info(channel_name):

    """Get the channel information and ID from the channel name. 
    """

    channel_url = f'lbry://@{channel_name}'

    post_json = {
        "jsonrpc":"2.0",
        "method":"resolve",
        "params":{
            "urls":[channel_url]}}

    response = requests.post(
        url = BACKEND_API_URL, 
        json = post_json)

    result = json.loads(response.text)
    
    info = result['result'][channel_url]
    
    info = {
        'channel_id' : info['claim_id'],
        'title' : info['value'].get('title'),
        'created': info['timestamp'],
        'description': info['value'].get('description'),
        'cover_image': info['value'].get('cover',{}).get('url'),
        'thumbnail_image': info['value'].get('thumbnail',{}).get('url'),
        'raw' : response.text}

    return info 

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_subscribers(claim_id):

    """Get the number of subscribers for a channel.  
    """

    json_data = {
        'auth_token': AUTH_TOKEN,
        'claim_id': claim_id }

    response = requests.post(url = SUBSCRIBER_API_URL, data = json_data)
    result = json.loads(response.text)
    subscribers = result['data'][0]

    return subscribers

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_all_videos(channel_id):

    """Get a list of all videos posted by a specified channel name. 

    Returns
    -------
    all_videos: list<dict>
        List of dictionaries, with each dict corresponding to a JSON response 
        containing data about a single video.

    """

    all_videos = []

    page = 1

    while True:

        json_data = {
            "jsonrpc":"2.0",
            "method":"claim_search",
            "params":{
                "page_size":30,
                "page":page,
                "order_by":["release_time"],
                "channel_ids":[channel_id]}}

        response = requests.post(
            url = BACKEND_API_URL, 
            json = json_data)

        result = json.loads(response.text)

        videos = result['result']['items']

        if not videos:
            break
        else:
            all_videos.extend(videos)
            page += 1

    return all_videos

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_views(claim_id):

    """Get the number of views for a given video.
    """

    params = {
        'auth_token': AUTH_TOKEN,
        'claim_id': claim_id }

    response = requests.get(url = VIEW_API_URL, params = params)
    views = json.loads(response.text)['data'][0]

    return views
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_video_reactions(claim_id):

    """Get all reactions for a given video.  
    """

    post_data = {
        'auth_token': AUTH_TOKEN,
        'claim_ids': claim_id }

    response = requests.post(url = REACTION_API_URL, data = post_data)
    result = json.loads(response.text)

    if result['success']:
        reactions = result['data']['others_reactions'][claim_id ]
        return reactions['like'], reactions['dislike']
    else:
        return None, None

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_all_comments(claim_id):

    """Get a list of all comments for a single video. 

    Parameters
    ----------
    claim_id: str
        Claim ID for the video whose comments are to be scraped
        e.g. ``'84d2a91e910bee523af5422439a639f677b9c78f'`` 

    Returns
    -------
    all_comments: list<dict>
        List of dictionaries, with each dict corresponding to a JSON response 
        containing data about a single comment for the specified video.
    """

    all_comments = []

    page = 1

    while True:

        json_data = {
            "jsonrpc":"2.0",
            "id":1,
            "method":"comment.List",
            "params":{
                "page":page,
                "claim_id":claim_id,
                "page_size":10,
                "top_level":False,
                "sort_by":3}}

        response = requests.post(
            url = COMMENT_API_URL, 
            json = json_data)

        result = json.loads(response.text)

        if 'items' not in result['result']:
            break
        else:
            _comments = result['result']['items']
            comments = append_comment_reactions(comments = _comments)
            all_comments.extend(comments)
            page += 1

    return all_comments

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def append_comment_reactions(comments):
    
    """Get reaction data for each comment and insert ``'reactions'`` key into 
    dict for each comment.

    Parameters
    ----------
    comments: list<dict>
        List of dictionaries, with each dict corresponding to a JSON response 
        containing data about a single comment for the specified video.

    Returns
    -------
    comments: list<dict>
        List of dictionaries, with each dict corresponding to a JSON response 
        containing data about a single comment for the specified video, with 
        additional ``'reactions'`` field containing reaction information for 
        each comment.

    """
    
    comment_ids = ','.join([c['comment_id'] for c in comments])

    json_data = {
        "jsonrpc":"2.0",
        "id":1,
        "method":"reaction.List",
        "params":{
            "comment_ids":comment_ids}}

    response = requests.post(url = COMMENT_API_URL, json = json_data)
    result = json.loads(response.text)

    reactions = result['result']['others_reactions']
    
    for comment in comments:
        comment['likes'] = reactions[comment['comment_id']]['like']
        comment['dislikes'] = reactions[comment['comment_id']]['dislike']
        
    return comments

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_recommended(title, claim_id):
    
    name = quote(title)

    params = {
        's':name,
        'size':'20',
        'from':'0',
        'related_to':claim_id}
    
    response = requests.get(url = RECOMMENDATION_API_URL, params = params)
    result = json.loads(response.text)
    
    recommended_video_info = [ name_to_video_info(r['name']) for r in result]
    recommended_video_info = [vi for vi in recommended_video_info if ((vi.get('value_type') == 'stream') & any(key in vi.get('value', []) for key in ('video', 'audio')))]

    return recommended_video_info

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def name_to_video_info(name):

    video_url = f"lbry://{name}"
    
    json_data = {
        "jsonrpc":"2.0",
        "method":"resolve",
        "params":{
            "urls":[video_url]}}

    response = requests.post(url = BACKEND_API_URL, json = json_data)
    result = json.loads(response.text)
    
    return result['result'][video_url]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#