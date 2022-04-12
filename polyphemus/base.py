# -*- coding: UTF-8 -*-

"""Base classes and methods for scraping video data from Odysee video platform.
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import json
from urllib.parse import unquote
from dataclasses import dataclass
import typing
from datetime import datetime 

from polyphemus import api

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

@dataclass
class Channel:
    channel_id: str
    created: datetime
    subscribers: int
    raw : str
    title : typing.Optional[str] = None
    description: typing.Optional[str] = None
    cover_image: typing.Optional[str] = None
    thumbnail_image: typing.Optional[str] = None

@dataclass
class Video:
    canonical_url: str
    type: str
    claim_id: str
    created: datetime
    title: str
    raw: str
    views: typing.Optional[int] = None
    streaming_url: typing.Optional[str] = None
    text: typing.Optional[str] = None
    thumbnail : typing.Optional[str] = None
    channel_id: typing.Optional[str] = None
    channel_name: typing.Optional[str] = None
    duration: typing.Optional[int] = None
    languages : typing.Optional[typing.List[str]] = None
    tags: typing.Optional[typing.List[str]] = None
    likes: typing.Optional[int] = None
    dislikes: typing.Optional[int] = None
    is_comment: bool = False

@dataclass
class Comment:
    text: str
    created: datetime
    claim_id : str
    video_claim_id : str
    channel_id: str
    channel_name : str
    replies: int
    likes: int
    dislikes: int
    raw : str
    is_comment: bool = True

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class OdyseeChannelScraper:

    #-------------------------------------------------------------------------#
    
    def __init__(self, channel_name: str, auth_token: str = None):
        
        self._channel_name = unquote(channel_name)

        if auth_token is None:
            self.auth_token = api.get_auth_token()
        else:
            self.auth_token = auth_token

        self._raw_channel_info = api.get_channel_info(channel_name = self._channel_name)
        self._channel_id = self._raw_channel_info['channel_id']
    
    #-------------------------------------------------------------------------#

    def get_entity(self) -> Channel:

        """Return Channel object containing information about the specified channel.
        """

        subscribers = api.get_subscribers(
            channel_id = self._channel_id,
            auth_token = self.auth_token)

        return Channel(
            channel_id=self._raw_channel_info['channel_id'],
            title=self._raw_channel_info['title'],
            created=datetime.fromtimestamp(self._raw_channel_info['created']),
            description=self._raw_channel_info['description'],
            cover_image=self._raw_channel_info['cover_image'],
            thumbnail_image=self._raw_channel_info['thumbnail_image'],
            raw=self._raw_channel_info['raw'],
            subscribers=subscribers)
        
    #-------------------------------------------------------------------------#

    def get_all_videos(self) -> typing.Generator[Video, None, None]:

        """Return list of Video objects for all videos posted by the specified channel
        """

        raw_video_info_list = api.get_raw_video_info_list(channel_id=self._channel_id)
        videos = (process_raw_video_info(raw_video_info, self.auth_token) for raw_video_info in raw_video_info_list)
        
        return videos

    #-------------------------------------------------------------------------#

    def get_all_videos_and_comments(self) -> typing.Tuple[typing.List['Video'], typing.List['Comment']]:

        """Return list of OdyseeVideo and OdyseeComment objects for all videos 
        posted by the channel and all comments posted to those videos
        """

        all_videos = list(self.get_all_videos())

        raw_comment_info_list = []
        
        for video in all_videos:
            raw_comment_info_list.extend(api.get_all_comments(video_id=video.claim_id))

        all_comments = [process_raw_comment_info(raw_comment_info) for raw_comment_info in raw_comment_info_list]
        
        return all_videos, all_comments
    
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def process_raw_video_info(raw_video_info: dict, auth_token: str = None, additional_fields: bool = True) -> Video:

    if auth_token is None:
        auth_token = api.get_auth_token()
    else:
        auth_token = auth_token

    # Handle edge cases
    #.....................................................................#

    if 'video' in raw_video_info['value']:
        video_type = 'video'
        duration = raw_video_info['value']['video'].get('duration')
    elif 'audio' in raw_video_info['value']:
        video_type = 'audio'
        duration = raw_video_info['value']['audio'].get('duration')
    elif 'claim_hash' in raw_video_info['value']:
        video_type = 'repost'
        duration = None
        raw_video_info['value'] = raw_video_info['reposted_claim']['value']
        raw_video_info['canonical_url'] = raw_video_info['reposted_claim']['canonical_url']
    elif 'image' in raw_video_info['value']:
        video_type = 'image'
        duration = None
    else:
        video_type = 'other'
        duration = None

    if 'signing_channel' in raw_video_info:
        channel_name = raw_video_info['signing_channel'].get('name')
        if 'claim_id' in raw_video_info['signing_channel']:
            channel_id = raw_video_info['signing_channel']['claim_id']
        else:
            channel_id = raw_video_info['signing_channel']['channel_id']
    else:
        channel_name = None
        channel_id = None

    if 'release_time' in raw_video_info['value']:
        created = raw_video_info['value']['release_time']
    else:
        created = raw_video_info['meta']['creation_timestamp']

    if 'thumbnail' in raw_video_info['value']:
        thumbnail = raw_video_info['value']['thumbnail'].get('url', None)
    else:
        thumbnail = None
    
    # Retrieve additional fields
    #.....................................................................#

    claim_id = raw_video_info['claim_id']

    if additional_fields:
        streaming_url = api.get_streaming_url(raw_video_info['canonical_url'])
        views = api.get_views(video_id=claim_id, auth_token = auth_token)
        likes, dislikes = api.get_video_reactions(
            video_id = claim_id,
            auth_token = auth_token)

    else:
        streaming_url = None
        views = None
        likes = None
        dislikes = None

    # Return Video object
    #.....................................................................#

    return Video(
        canonical_url = raw_video_info['canonical_url'],
        type = video_type,
        channel_id = channel_id,
        channel_name = channel_name,
        claim_id = raw_video_info['claim_id'],
        created = datetime.fromtimestamp(int(created)),
        text = raw_video_info['value'].get('description'),
        languages = raw_video_info['value'].get('languages'),
        tags = raw_video_info['value'].get('tags',[]),
        title = raw_video_info['value']['title'],
        duration = duration,
        thumbnail = thumbnail,
        is_comment = False,
        raw = json.dumps(raw_video_info),
        views = views,
        likes = likes,
        dislikes = dislikes,
        streaming_url = streaming_url)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def process_raw_comment_info(raw_comment_info: dict) -> Comment:

    return Comment(
        text = raw_comment_info['comment'],
        created = raw_comment_info['timestamp'],
        claim_id = raw_comment_info.get('comment_id'),
        video_claim_id = raw_comment_info['claim_id'],
        channel_id = raw_comment_info['channel_id'],
        channel_name = raw_comment_info['channel_name'],
        replies = raw_comment_info.get('replies', 0),
        likes = raw_comment_info['likes'],
        dislikes = raw_comment_info['dislikes'],
        is_comment = True,
        raw = json.dumps(raw_comment_info))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

def get_recommended(video: Video, auth_token: str = None) -> typing.List['Video']:

    if auth_token is None:
        auth_token = api.get_auth_token()
    else:
        auth_token = auth_token
    
    recommended_video_info_list = api.get_recommended(
        video_title=video.title, video_id=video.claim_id)
    recommended_videos = [process_raw_video_info(raw_video_info, auth_token) for raw_video_info in recommended_video_info_list]

    return recommended_videos

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#