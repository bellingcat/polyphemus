# -*- coding: UTF-8 -*-

"""Tests for to polyphemus.base module.

The full set of tests for this module can be evaluated by executing the
command::

  $ python -m pytest tests/base.py

from the project root directory.

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import pytest

from polyphemus import base

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


class TestOdyseeChannelScraper:
    @pytest.fixture(autouse=True)
    def test_simple_init(self, resources):
        self.scraper = base.OdyseeChannelScraper(channel_name=resources["channel_name"])

    def test_get_entity(self):
        self.scraper.get_entity()

    def test_get_all_videos(self):
        self.scraper.get_all_videos()

    def test_get_all_videos_and_comments(self):
        self.scraper.get_all_videos_and_comments()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


def test_process_raw_video_info(resources):
    video = base.process_raw_video_info(
        raw_video_info=resources["full_video_info"], auth_token=resources["auth_token"]
    )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


def test_process_raw_comment_info(resources):
    base.process_raw_comment_info(raw_comment_info=resources["full_comment_info"])


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


class TestRecommendationEngine:
    @pytest.fixture(autouse=True)
    def test_simple_init(self, resources):
        self.engine = base.RecommendationEngine(
            channel_list=[resources["channel_name"]]
        )

    def test_generate(self):
        self.engine.generate(iterations=1)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
