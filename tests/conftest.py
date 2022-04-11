# -*- coding: UTF-8 -*-

"""Configuration for pytest sessions
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import pytest

from polyphemus.api import get_auth_token

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

CHANNEL_NAME = 'Mak1nBacon'
CHANNEL_ID = 'fb2a33dc4252feb2e99c6d6949fbd3cc557cab2b'
VIDEO_ID = 'a754344cd7887a15ab4fddaa893ff08926c63bf3'
VIDEO_TITLE = 'chips'
NORMALIZED_NAME = 'want-me-eat-all-chips-meme'
CANONICAL_URL = 'lbry://@Mak1nBacon#f/want-me-eat-all-chips-meme#a'

FULL_VIDEO_INFO = {
    'address': 'bPfL73FnWqHMd9idqgGh2xbJfYu85MMMRw',
    'canonical_url': 'lbry://@Mak1nBacon#f/doggo-meme-cute-funny#5',
    'claim_id': '53e51a9417a8445de3c11af3d45412df9693d015',
    'name': 'doggo-meme-cute-funny',
    'normalized_name': 'doggo-meme-cute-funny',
    'permanent_url': 'lbry://doggo-meme-cute-funny#53e51a9417a8445de3c11af3d45412df9693d015',
    'short_url': 'lbry://doggo-meme-cute-funny#5',
    'signing_channel': {
        'address': 'bPfL73FnWqHMd9idqgGh2xbJfYu85MMMRw',
        'canonical_url': 'lbry://@Mak1nBacon#f',
        'claim_id': 'fb2a33dc4252feb2e99c6d6949fbd3cc557cab2b',
        'name': '@Mak1nBacon',
        'normalized_name': '@mak1nbacon',
        'permanent_url': 'lbry://@Mak1nBacon#fb2a33dc4252feb2e99c6d6949fbd3cc557cab2b',
        'short_url': 'lbry://@Mak1nBacon#f',
        'timestamp': 1642268511,
        'type': 'claim',
        'value': {
            'cover': {
                'url': 'https://thumbs.odycdn.com/6b6e3f5ed6b62e96e8013bbcfa486896.png'},
            'description': "Hello ladies and men! In case you're wondering, yes, i'm still a piece of pork.\n\nBasically, i'm a random animator trying out Odysee. I make an object show called Meanwhile in the Void and random memes and animations too!\n\nIf you like this type of content, you're welcome to watch, but if you don't like my content, you're also welcome to watch! I don't mind lol.\n\nIf you're considering helping the channel, feel free to follow me!\n\nBacon included. ;)\n\nSee ya soon, stay calm, stick around and stay alive!",
            'tags': ['comedy', 'animation', 'art', 'funny', 'object show'],
            'thumbnail': {
                'url': 'https://spee.ch/b/e4e3a6562e4b1cd5.png'},
            'title': "Mak1n' Bacon"},
        'value_type': 'channel'},
    'timestamp': 1645981620,
    'type': 'claim',
    'value': {
        'description': 'dog',
        'languages': ['en'],
        'license': 'None',
        'release_time': '1645981256',
        'stream_type': 'video',
        'tags': ['art', 'comedy', 'meme', 'memes', 'animals'],
        'thumbnail': {
            'url': 'https://thumbs.odycdn.com/719ad60363211ef047b18a8f354c2943.jpeg'},
        'title': 'doggo',
        'video': {
            'duration': 15, 
            'height': 640, 
            'width': 640}},
    'value_type': 'stream'}

COMMENT_INFO_LIST = [{
    'comment': 'the man on the right has some nice feet',
    'comment_id': '320a0823689b9dbefad768598d89816bda0a015b11ad4b522bc0112a8089b3f5',
    'claim_id': 'a754344cd7887a15ab4fddaa893ff08926c63bf3',
    'timestamp': 1644193831,
    'signature': '444835698b1bfe160c775210b9542970b14c8dcb7b88118a367c2fe102bb2ddcc3fa3881827a789cb183f2e3fd5c8f263ec05d7c431cfe8e145d7f3f501c0668',
    'signing_ts': '1644193830',
    'channel_id': 'a641423e6e20718f3d59138a17cf530bb419d86b',
    'channel_name': '@devnull',
    'channel_url': 'lbry://@devnull#a641423e6e20718f3d59138a17cf530bb419d86b',
    'replies': 1,}]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

@pytest.fixture(scope = 'module')
def resources():

    """SetUp fixture to create constant valued resources for testing modules
    """

    resources_dict = dict(
        channel_name = CHANNEL_NAME,
        channel_id = CHANNEL_ID,
        video_id = VIDEO_ID,
        video_title = VIDEO_TITLE,
        normalized_name = NORMALIZED_NAME,
        canonical_url = CANONICAL_URL,
        full_video_info = FULL_VIDEO_INFO,
        full_comment_info = {**COMMENT_INFO_LIST[0], **{'likes': 8, 'dislikes': 0}},
        comment_info_list = COMMENT_INFO_LIST,
        auth_token = get_auth_token())

    return resources_dict

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#