# -*- coding: UTF-8 -*-

"""Tests for to polyphemus.api module.

The full set of tests for this module can be evaluated by executing the
command::

  $ python -m pytest tests/api.py

from the project root directory.

"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

import asyncio

import pytest

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

KWARGS_LIST = [
    ("get_auth_token", []),
    ("get_channel_info", ["channel_name"]),
    ("get_subscribers", ["channel_id", "auth_token"]),
    ("get_raw_video_info_list", ["channel_id"]),
    ("get_views", ["video_id", "auth_token"]),
    ("get_video_reactions", ["video_id", "auth_token"]),
    ("get_all_comments", ["video_id"]),
    ("append_comment_reactions", ["comment_info_list"]),
    ("get_recommended", ["video_title", "video_id"]),
    ("normalized_names_to_video_info", ["normalized_names"]),
    ("get_streaming_url", ["canonical_url"]),
]

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


@pytest.mark.parametrize("function_str,kwargs", KWARGS_LIST)
def test_minimal_init(resources, function_str, kwargs):
    function = eval(f"api.{function_str}")
    function_kwargs = {kwarg: resources[kwarg] for kwarg in kwargs}

    asyncio.run(function(**function_kwargs))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
