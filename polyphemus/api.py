# -*- coding: UTF-8 -*-

"""Functions to request and process information from Odysee APIs
"""

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

import asyncio
import json
import time
from typing import Tuple, Optional, List, Callable
from urllib.parse import quote

import aiohttp

# API endpoints for Odysee data
# ----------------------------------------------------------------------------- #

BACKEND_API_URL = "https://api.na-backend.odysee.com/api/v1/proxy"
SUBSCRIBER_API_URL = "https://api.odysee.com/subscription/sub_count"
VIEW_API_URL = "https://api.odysee.com/file/view_count"
REACTION_API_URL = "https://api.odysee.com/reaction/list"
COMMENT_API_URL = "https://comments.odysee.com/api/v2"
RECOMMENDATION_API_URL = "https://recsys.odysee.com/search"
NEW_USER_API_URL = "https://api.odysee.com/user/new"

# Allow responses to `get_streaming_url` that contain no `streaming_url` field
ALLOWED_ERROR_CODES = [-32603]

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def make_request(request: Callable, kwargs: dict) -> aiohttp.ClientResponse:
    """
    Async wrapper for making HTTP requests with retries and error handling.

    Parameters
    ----------
    request : Callable
        The aiohttp session method to be called (session.get, session.post).
    kwargs : dict
        Keyword arguments for the `request` function. Must include `url` key.

    Returns
    -------
    aiohttp.ClientResponse
        The HTTP response received upon a successful request.

    Raises
    ------
    ValueError
        If the maximum number of retries is reached without a successful response.
    """

    # Set a default timeout
    kwargs.setdefault("timeout", aiohttp.ClientTimeout(total=15))

    retry_reasons = []

    # Retrying the request up to 10 times
    for n_retries in range(10):
        # Backoff strategy for retries
        await asyncio.sleep(2**n_retries - 1)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(request.__name__, **kwargs) as response:
                    if response.status == 200:
                        return await process_successful_response(response)
                    else:
                        retry_reasons.append(f"HTTP status code: {response.status}")
            except Exception as exception:
                retry_reasons.append(f"Python exception: {exception}")

    # If all retries failed, raise an exception
    raise ValueError(
        f"Maximum number of retries reached for request {request.__name__} with kwargs {kwargs}. "
        f"Retry reasons: {retry_reasons}"
    )


async def process_successful_response(
    response: aiohttp.ClientResponse,
) -> aiohttp.ClientResponse:
    """
    Process a successful HTTP response asynchronously.

    Parameters
    ----------
    response : aiohttp.ClientResponse
        The successful HTTP response to process.

    Returns
    -------
    aiohttp.ClientResponse
        The processed response.

    Raises
    ------
    ValueError
        If the response contains an error not in the ALLOWED_ERROR_CODES.
    """
    parsed_response = json.loads(await response.text())
    if isinstance(parsed_response, list):
        return response
    if (
        parsed_response.get("error")
        and parsed_response.get("error").get("code") not in ALLOWED_ERROR_CODES
    ):
        raise ValueError(f'JSON response error: {parsed_response.get("error")}')
    return response


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_auth_token() -> str:
    """
    Get a fresh authorization token, to use for API calls that require it.

    Note:
    -----
    calling this function many times in quick succession may result in a 503 error.
    """
    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": NEW_USER_API_URL}
        )
        response_text = await response.text()
        auth_token = json.loads(response_text)["data"]["auth_token"]

    return auth_token


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_channel_info(channel_name: str) -> dict:
    """Get the channel information and ID from the channel name."""

    channel_url = f"lbry://@{channel_name}"

    json_data = {
        "jsonrpc": "2.0",
        "method": "resolve",
        "params": {"urls": [channel_url]},
    }

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": BACKEND_API_URL, "json": json_data}
        )
        response_text = await response.text()
        result = json.loads(response_text)

        info = result["result"][channel_url]

        info = {
            "channel_id": info["claim_id"],
            "title": info["value"].get("title"),
            "created": info["timestamp"],
            "description": info["value"].get("description"),
            "cover_image": info["value"].get("cover", {}).get("url"),
            "thumbnail_image": info["value"].get("thumbnail", {}).get("url"),
            "raw": response_text,
        }

    return info


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_subscribers(channel_id: str, auth_token: str = None) -> int:
    """Get the number of subscribers for a channel."""

    if auth_token is None:
        auth_token = await get_auth_token()

    json_data = {"auth_token": auth_token, "claim_id": channel_id}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": SUBSCRIBER_API_URL, "data": json_data}
        )
        response_text = await response.text()

        result = json.loads(response_text)
        subscribers = result["data"][0]

    return subscribers


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_raw_video_info_list(channel_id: str) -> list:
    """Get a list of all videos posted by a specified channel name.

    Odysee's ``claim_search`` API (which is used on the browser and LBRY
    desktop app) only allows up to 1000 videos to be fetched for a single value
    of the ``release_time`` parameter. You can check this by going to an Odysee
    channel with a lot of videos (e.g. @etresouverain) and holding the
    "Page Down" button until you reach the bottom, there will only be 1000
    videos.

    This function loops over all pages for a single ``release_time`` and
    fetches the raw video info for all videos until it reaches that 1000 video
    limit, then uses the minimum of the ``creation_timestamp`` for all videos
    as the new ``release_time``, and starts looping over all pages for
    that new ``release_time``.

    Returns
    -------
    raw_video_info_list: list<dict>
        List of dictionaries, with each dict corresponding to a JSON response
        containing data about a single video.

    """

    claim_id_to_raw_video_info = {}
    page = 1
    release_time = int(time.time()) + 86400
    hit_video_limit = False

    while True:
        json_data = {
            "jsonrpc": "2.0",
            "method": "claim_search",
            "params": {
                "page_size": 30,
                "page": page,
                "order_by": ["release_time"],
                "channel_ids": [channel_id],
                "release_time": f"<{release_time}",
            },
        }

        async with aiohttp.ClientSession() as session:
            response = await make_request(
                request=session.post, kwargs={"url": BACKEND_API_URL, "json": json_data}
            )
            response_text = await response.text()

            result = json.loads(response_text)

            videos = result["result"]["items"]
            new_videos = {
                video["claim_id"]: video
                for video in videos
                if video["claim_id"] not in claim_id_to_raw_video_info
            }

            if len(new_videos) == 0:
                # if there are no new videos that haven't already been scraped
                if hit_video_limit:
                    # if Odysee's limit of 1000 videos for a given timestamp was
                    # reached (which updates the `release_time`) on the last
                    # request, this means we have scraped all videos on the channel,
                    # so we break the loop.
                    break
                else:
                    # we have hit Odysee's limit of 1000 videos for a given
                    # timestamp, so we update `release_time` and reset `page`
                    hit_video_limit = True
                    release_time = min(
                        [
                            raw_video_info["meta"]["creation_timestamp"]
                            for raw_video_info in claim_id_to_raw_video_info.values()
                        ],
                        default=0,
                    )
                    page = 1
            else:
                # there were unscraped videos from the last request, so we keep
                # going in the loop and increment the `page` variable
                claim_id_to_raw_video_info.update(new_videos)
                page += 1
                hit_video_limit = False

    return list(claim_id_to_raw_video_info.values())


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_views(video_id: str, auth_token: str = None) -> int:
    """Get the number of views for a given video."""

    if auth_token is None:
        auth_token = await get_auth_token()

    params = {"auth_token": auth_token, "claim_id": video_id}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.get, kwargs={"url": VIEW_API_URL, "params": params}
        )
        response_text = await response.text()

        views = json.loads(response_text)["data"][0]

    return views


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_video_reactions(
    video_id: str, auth_token: str = None
) -> Tuple[Optional[int], Optional[int]]:
    """Get all reactions for a given video."""

    if auth_token is None:
        auth_token = await get_auth_token()

    post_data = {"auth_token": auth_token, "claim_ids": video_id}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": REACTION_API_URL, "data": post_data}
        )
        response_text = await response.text()

        result = json.loads(response_text)

        if result["success"]:
            reactions = result["data"]["others_reactions"][video_id]
            return reactions["like"], reactions["dislike"]
        else:
            return None, None


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_all_comments(video_id: str) -> List[dict]:
    """Get a list of all comments for a single video.

    Parameters
    ----------
    video_id: str
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
            "jsonrpc": "2.0",
            "id": 1,
            "method": "comment.List",
            "params": {
                "page": page,
                "claim_id": video_id,
                "page_size": 10,
                "top_level": False,
                "sort_by": 3,
            },
        }

        async with aiohttp.ClientSession() as session:
            response = await make_request(
                request=session.post, kwargs={"url": COMMENT_API_URL, "json": json_data}
            )
            response_text = await response.text()

            result = json.loads(response_text)

            if "items" not in result["result"]:
                break
            else:
                _comments = result["result"]["items"]
                comments = await append_comment_reactions(comment_info_list=_comments)
                all_comments.extend(comments)
                page += 1

    return all_comments


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def append_comment_reactions(comment_info_list: List[dict]) -> List[dict]:
    """Get reaction data for each comment and insert ``'reactions'`` key into
    dict for each comment.

    Parameters
    ----------
    comment_info_list: list<dict>
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

    comment_ids = ",".join([c["comment_id"] for c in comment_info_list])

    json_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "reaction.List",
        "params": {"comment_ids": comment_ids},
    }

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": COMMENT_API_URL, "json": json_data}
        )
        response_text = await response.text()

        result = json.loads(response_text)

        reactions = result["result"]["others_reactions"]

        for comment in comment_info_list:
            comment["likes"] = reactions[comment["comment_id"]]["like"]
            comment["dislikes"] = reactions[comment["comment_id"]]["dislike"]

    return comment_info_list


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_recommended(video_title: str, video_id: str) -> List[dict]:
    """Get list of raw video info dicts for a specified video title and video
    claim_id.
    """

    name = quote(video_title)

    params = {"s": name, "size": "20", "from": "0", "related_to": video_id}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.get,
            kwargs={"url": RECOMMENDATION_API_URL, "params": params},
        )
        response_text = await response.text()

        result = await json.loads(response_text)
        recommended_video_info = await normalized_names_to_video_info(
            [r["name"] for r in result]
        )
        recommended_video_info = [
            video
            for video in recommended_video_info
            if (
                (video.get("value_type") == "stream")
                & any(key in video.get("value", []) for key in ("video", "audio"))
            )
        ]

    return recommended_video_info


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def normalized_names_to_video_info(normalized_names: List[str]) -> list:
    """
    Convert a list of normalized names of videos to a list of raw video dicts for those videos.

    Example of a "normalized name" is:
    ----------------------------------
        ``'si-une-tude-montre-que-le-masque-permet'``,

    corresponding to the video:
        ``https://odysee.com/@filsdepangolin#e/si-une-tude-montre-que-le-masque-permet#e``.
    """

    video_urls = [f"lbry://{normalized_name}" for normalized_name in normalized_names]

    json_data = {"jsonrpc": "2.0", "method": "resolve", "params": {"urls": video_urls}}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": BACKEND_API_URL, "json": json_data}
        )
        response_text = await response.text()

        result = json.loads(response_text)

    return [result["result"][video_url] for video_url in video_urls]


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


async def get_streaming_url(canonical_url: str) -> str:
    """Retrieve the `streaming_url` for a specified video."""

    json_data = {"jsonrpc": "2.0", "method": "get", "params": {"uri": canonical_url}}

    async with aiohttp.ClientSession() as session:
        response = await make_request(
            request=session.post, kwargs={"url": BACKEND_API_URL, "json": json_data}
        )
        response_text = await response.text()

        video_url = json.loads(response_text).get("result", {}).get("streaming_url")

    return video_url


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
