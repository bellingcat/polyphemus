# -*- coding: UTF-8 -*-

"""Base classes and methods for scraping video data from Odysee video platform.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import json
from dataclasses import dataclass

from polyphemus import api

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

#TODO Figure out how to reverse-engineer this
AUTH_TOKEN = 'BseGAiye641UqUsv4g31ZcUCRiLasv3U'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeChannel:

    #-------------------------------------------------------------------------#
    
    def __init__(self, channel_name):
        
        self._channel_name = channel_name

        info = api.get_channel_info(channel_name = self._channel_name)

        self.info = info
        self._channel_id = self.info['channel_id']

        self.info['subscribers'] = api.get_subscribers(claim_id = self.info['channel_id'])
    
    #-------------------------------------------------------------------------#

    def get_all_videos(self):

        """Return list of OdyseeVideo objects for all videos posted by the channel
        """

        all_video_info = api.get_all_videos(channel_id=self.info['channel_id'])
        self.all_videos = [OdyseeVideo(video) for video in all_video_info]
        
        return self.all_videos

    #-------------------------------------------------------------------------#

    def get_all_videos_and_comments(self):

        """Return list of OdyseeVideo and OdyseeComment objects for all videos 
        posted by the channel and all comments posted to those videos
        """

        all_videos = self.get_all_videos()

        all_comments = []
        
        for video in all_videos:
            all_comments.extend(video.get_all_comments())
        
        return all_videos, all_comments
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeVideo:

    #-------------------------------------------------------------------------#
    
    def __init__(self, full_video_info):

        # Handle edge cases
        #.....................................................................#

        if 'video' in full_video_info['value']:
            video_type = 'video'
            duration = full_video_info['value']['video'].get('duration')
        elif 'audio' in full_video_info['value']:
            video_type = 'audio'
            duration = full_video_info['value']['audio'].get('duration')
        elif 'claim_hash' in full_video_info['value']:
            video_type = 'repost'
            duration = None
            
            full_video_info['value'] = full_video_info['reposted_claim']['value']
            full_video_info['canonical_url'] = full_video_info['reposted_claim']['canonical_url']

        else:
            raise KeyError(f'nether `video`, `audio`, nor `claim_hash` keys are in `full_video_info["value"]`, only {full_video_info["value"].keys()}')

        if 'signing_channel' in full_video_info:
            channel_name = full_video_info['signing_channel'].get('name')
            if 'claim_id' in full_video_info['signing_channel']:
                channel_id = full_video_info['signing_channel']['claim_id']
            else:
                channel_id = full_video_info['signing_channel']['channel_id']
        else:
            channel_name = None
            channel_id = None

        if 'release_time' in full_video_info['value']:
            created = full_video_info['value']['release_time']
        else:
            created = full_video_info['meta']['creation_timestamp']

        if 'thumbnail' in full_video_info['value']:
            thumbnail = full_video_info['value']['thumbnail'].get('url', None)
        else:
            thumbnail = None
        
        # Store relevant information in flat dict
        #.....................................................................#
        
        self.info = {
            'canonical_url' : full_video_info['canonical_url'],
            'type' : video_type,
            'channel_id' : channel_id,
            'channel' : channel_name,
            'claim_id' : full_video_info['claim_id'],
            'created' : int(created),
            'description' : full_video_info['value'].get('description'),
            'languages' : full_video_info['value'].get('languages'),
            'tags' : full_video_info['value'].get('tags',[]),
            'title' : full_video_info['value']['title'],
            'duration' : duration,
            'thumbnail' : thumbnail,
            'raw' : json.dumps(full_video_info)}
        
        self._claim_id = self.info['claim_id']

        self.info['views'] = api.get_views(claim_id=self._claim_id)

        self.info['likes'], self.info['dislikes']= api.get_video_reactions(
            claim_id = self._claim_id)

        self.info['streaming_url'] = api.get_streaming_url(self.info['canonical_url'])

    #-------------------------------------------------------------------------#

    def get_all_comments(self):
        
        all_comment_info = api.get_all_comments(claim_id=self._claim_id)
        self.all_comments = [OdyseeComment(comment) for comment in all_comment_info]
        
        return self.all_comments

    #-------------------------------------------------------------------------#
    
    def get_recommended(self):
        
        recommended_video_info = api.get_recommended(
            title=self.info['title'], claim_id=self._claim_id)
        recommended_videos = [OdyseeVideo(video_info) for video_info in recommended_video_info]

        return recommended_videos

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeComment:

    def __init__(self, full_comment_info):
        
        self.info = {
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