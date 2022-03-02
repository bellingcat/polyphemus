# -*- coding: UTF-8 -*-

"""Tests for to polyphemus.base module.

The full set of tests for this module can be evaluated by executing the
command::

  $ python -m pytest tests/base.py

from the project root directory.

"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import pytest

from polyphemus import base

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class TestOdyseeChannel:

    @pytest.fixture(autouse=True)
    def test_simple_init(self, resources):
        self.channel = base.OdyseeChannel(channel_name = resources['channel_name'])

    def test_get_all_videos(self):
        self.channel.get_all_videos()

    def test_get_all_videos_and_comments(self):
        self.channel.get_all_videos_and_comments()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class TestOdyseeVideo:

    @pytest.fixture(autouse=True)
    def test_simple_init(self, resources):
        self.video = base.OdyseeVideo(full_video_info = resources['full_video_info'])

    def test_get_all_comments(self):
        self.video.get_all_comments()

    def test_get_recommended(self):
        self.video.get_recommended()
        
#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

class TestOdyseeComment:

    @pytest.fixture(autouse=True)
    def test_simple_init(self, resources):
        self.comment = base.OdyseeComment(full_comment_info = resources['full_comment_info'])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#