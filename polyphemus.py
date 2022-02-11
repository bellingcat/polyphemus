# -*- coding: UTF-8 -*-

"""Functions and classes for scraping video data from Odysee video platform.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import json
import csv
from pathlib import Path 
import os 

import requests
import pandas as pd

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

#TODO Figure out how to reverse-engineer this
AUTH_TOKEN = 'BseGAiye641UqUsv4g31ZcUCRiLasv3U'

CHANNEL_NAME = 'PatriotFront'
OUTPUT_DIR = Path('.').resolve().parent/'data'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeChannel:

    #-------------------------------------------------------------------------#
    
    def __init__(self, channel_name):
        
        self._channel_name = channel_name
        self.get_channel_info()
    
    #-------------------------------------------------------------------------#

    def get_channel_info(self):
    
        """Get the channel information and ID from the channel name. 
        """

        channel_url = f'lbry://@{self._channel_name}'

        api_url = 'https://api.na-backend.odysee.com/api/v1/proxy'

        post_json = {
            "jsonrpc":"2.0",
            "method":"resolve",
            "params":{
                "urls":[channel_url]}}

        response = requests.post(
            url = api_url, 
            json = post_json)

        result = json.loads(response.text)
        
        info = result['result'][channel_url]
        
        channel_info = {
            'channel_id' : info['claim_id'],
            'title' : info['value']['title'],
            'created': info['timestamp'],
            'description': info['value']['description'],
            'cover_image': info['value']['cover']['url'],
            'thumbnail_image': info['value']['thumbnail']['url'],
            'raw' : response.text}

        self._channel_info = channel_info
        self._channel_id = self._channel_info['channel_id']
    
    #-------------------------------------------------------------------------#

    def get_all_videos(self):

        """Get a list of all videos posted by a specified channel name. 

        Returns
        -------
        all_videos: list<dict>
            List of dictionaries, with each dict corresponding to a JSON response 
            containing data about a single video.

        """

        api_url = 'https://api.na-backend.odysee.com/api/v1/proxy'

        all_videos = []

        page = 1

        while True:

            post_data = {
                "jsonrpc":"2.0",
                "method":"claim_search",
                "params":{
                    "page_size":30,
                    "page":page,
                    "order_by":["release_time"],
                    "channel_ids":[self._channel_id]}}

            response = requests.post(
                url = api_url, 
                json = post_data)

            result = json.loads(response.text)

            videos = result['result']['items']

            if not videos:
                break
            else:
                all_videos.extend(videos)
                page += 1

        self._all_videos = all_videos
    
    #-------------------------------------------------------------------------#

    def process_all_videos(self):
        
        self.get_all_videos()
        all_videos_processed = [OdyseeVideo(video)._video_info for video in self._all_videos]
        
        return all_videos_processed
    
    #-------------------------------------------------------------------------#

    def process_all_videos_and_comments(self):
        
        self.get_all_videos()
        all_videos = [OdyseeVideo(video) for video in self._all_videos]
        all_videos_processed = [video._video_info for video in all_videos]
        
        all_comments_processed = []
        
        for video in all_videos:
            all_comments_processed.extend(video.process_all_comments())
        
        return all_videos_processed, all_comments_processed
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeVideo:

    #-------------------------------------------------------------------------#
    
    def __init__(self, full_video_info):
        
        self._video_info = {
            'canonical_url' : full_video_info['canonical_url'],
            'claim_id' : full_video_info['claim_id'],
            'created' : full_video_info['value']['release_time'],
            'description' : full_video_info['value']['description'],
            'languages' : full_video_info['value']['languages'],
            'tags' : full_video_info['value'].get('tags',[]),
            'title' : full_video_info['value']['title'],
            'duration' : full_video_info['value']['video']['duration'],
            'thumbnail' : full_video_info['value']['thumbnail']['url'],
            'raw' : json.dumps(full_video_info)}
        
        self._claim_id = self._video_info ['claim_id']

        self.get_views()
        self.get_video_reactions()

    #-------------------------------------------------------------------------#
        
    def get_views(self):

        """Get the number of views for a given video.
        """

        api_url = 'https://api.odysee.com/file/view_count'

        params = {
            'auth_token': AUTH_TOKEN,
            'claim_id': self._claim_id }

        response = requests.get(api_url, params = params)
        views = json.loads(response.text)['data'][0]

        self._video_info['views'] = views
    
    #-------------------------------------------------------------------------#

    def get_video_reactions(self):

        """Get all reactions for a given video.  
        """

        api_url = f'https://api.odysee.com/reaction/list'

        post_data = {
            'auth_token': AUTH_TOKEN,
            'claim_ids': self._claim_id }

        response = requests.post(url = api_url, data = post_data)
        result = json.loads(response.text)
        reactions = result['data']['others_reactions'][self._claim_id ]

        self._video_info['likes'] = reactions['like']
        self._video_info['dislikes'] = reactions['dislike']
    
    #-------------------------------------------------------------------------#

    def get_all_comments(self):

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

        api_url = 'https://comments.odysee.com/api/v2'

        all_comments = []

        page = 1

        while True:

            post_data = {
                "jsonrpc":"2.0",
                "id":1,
                "method":"comment.List",
                "params":{
                    "page":page,
                    "claim_id":self._claim_id,
                    "page_size":10,
                    "top_level":False,
                    "sort_by":3}}

            response = requests.post(
                url = api_url, 
                json = post_data)

            result = json.loads(response.text)

            if 'items' not in result['result']:
                break
            else:
                _comments = result['result']['items']
                comments = append_comment_reactions(comments = _comments)
                all_comments.extend(comments)
                page += 1

        self._all_comments = all_comments
        
    #-------------------------------------------------------------------------#

    def process_all_comments(self):
        
        self.get_all_comments()
        all_comments_processed = [OdyseeComment(comment)._comment_info for comment in self._all_comments]
        
        return all_comments_processed

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeComment:

    def __init__(self, full_comment_info):
        
        self._comment_info = {
            'comment' : full_comment_info['comment'],
            'created' : full_comment_info['timestamp'],
            'video_claim_id' : full_comment_info['claim_id'],
            'channel_id' : full_comment_info['channel_id'],
            'channel_name' : full_comment_info['channel_name'],
            'replies' : full_comment_info.get('replies', 0),
            'likes' : full_comment_info['likes'],
            'dislikes' : full_comment_info['dislikes'],
            'raw' : json.dumps(full_comment_info)}

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

    post_data = {
        "jsonrpc":"2.0",
        "id":1,
        "method":"reaction.List",
        "params":{
            "comment_ids":comment_ids}}

    api_url = 'https://comments.odysee.com/api/v2'
    response = requests.post(url = api_url, json = post_data)
    result = json.loads(response.text)

    reactions = result['result']['others_reactions']
    
    for comment in comments:
        comment['likes'] = reactions[comment['comment_id']]['like']
        comment['dislikes'] = reactions[comment['comment_id']]['dislike']
        
    return comments

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

    odysee_channel = OdyseeChannel(channel_name = CHANNEL_NAME)

    video_info_list, comment_info_list = odysee_channel.process_all_videos_and_comments()

    channel_df = pd.DataFrame([odysee_channel._channel_info])
    video_df = pd.DataFrame(video_info_list)
    comment_df = pd.DataFrame(comment_info_list)

    output_subdir = Path(OUTPUT_DIR, CHANNEL_NAME)
    os.makedirs(output_subdir, exist_ok = True)

    channel_df.to_csv(
        path_or_buf = Path(output_subdir, f'{CHANNEL_NAME}_channel.csv'),
        index = False,
        quoting = csv.QUOTE_NONNUMERIC )

    video_df.to_csv(
        path_or_buf = Path(output_subdir, f'{CHANNEL_NAME}_videos.csv'),
        index = False,
        quoting = csv.QUOTE_NONNUMERIC )

    comment_df.to_csv(
        path_or_buf = Path(output_subdir, f'{CHANNEL_NAME}_comments.csv'),
        index = False,
        quoting = csv.QUOTE_NONNUMERIC )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


    


