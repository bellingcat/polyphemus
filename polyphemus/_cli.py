# -*- coding: UTF-8 -*-

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

import argparse
import asyncio
from pprint import pprint

import yappi

from . import api

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #

# Mapping of command-line arguments to their respective functions
ARGUMENTS_MAPPING: dict = {
    "channel": {
        "profile": (api.get_channel_info, ["channel_name"]),
        "videos": (api.get_raw_video_info_list, ["channel_id"]),
        "subscribers": (api.get_subscribers, ["channel_id"]),
    },
    "video": {
        "views": (api.get_views, ["claim_id"]),
        "comments": (api.get_all_comments, ["claim_id"]),
        "reactions": (api.get_video_reactions, ["claim_id"]),
        "streaming_url": (api.get_streaming_url, ["canonical_url"]),
        "recommended_videos": (api.get_recommended, ["video_title", "claim_id"]),
    },
    "misc": {
        "append_comments_reactions": (
            api.append_comment_reactions,
            ["comments_list"],
        ),
        "normalized_names2video_info": (
            api.normalized_names_to_video_info,
            ["normalized_names"],
        ),
    },
}

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #


# Function to create and configure the argument parser.
def create_parser() -> argparse.ArgumentParser:
    # Create a parser with a description of the tool.
    parser = argparse.ArgumentParser(
        description="Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.",
        epilog="Copyright © 2022-2023 Bellingcat. All rights reserved.",
    )
    parser.add_argument(
        "--runtime-prof",
        dest="runtime_profiler",
        help="enable runtime profiler",
        action="store_true",
    )
    parser.add_argument(
        "-pct",
        "--prof-clock-type",
        dest="prof_clock_type",
        help="set profiler clock type (default: %(default)s)",
        default="CPU",
        choices=["WALL", "CPU"],
    )
    parser.add_argument(
        "-pst",
        "--prof-sort-type",
        dest="prof_sort_type",
        help="set profiler stats' sort type (default: %(default)s)",
        default="ncall",
        choices=[
            "ttot",
            "tsub",
            "tavg",
            "ncall",
            "name",
        ],
    )
    parser.add_argument(
        "-pso",
        "--prof-sort-order",
        dest="prof_sort_order",
        help="set profiler stats' sort order (default: %(default)s)",
        default="desc",
        choices=["asc", "desc"],
    )

    # Creating subparsers for different command categories.
    subparsers = parser.add_subparsers(
        dest="target",
        help="target",
    )

    # Parser for channel-related operations.
    channel_parser = subparsers.add_parser(
        "channel",
        help="channel operations",
    )
    # Adding arguments to the channel parser for different types of channel data.
    channel_parser.add_argument(
        "data",
        help="retrievable channel data",
        choices=["profile", "subscribers", "videos"],
    )
    # Additional arguments for channel operations, specifying either name or ID.
    channel_parser.add_argument(
        "-n",
        "--name",
        dest="channel_name",
        type=str,
        help="channel_name: use to get a channel's `profile`",
    )
    channel_parser.add_argument(
        "-i",
        "--id",
        dest="channel_id",
        type=str,
        help="channel_id: use to get a channel's `subscribers` or `videos`",
    )

    # Parser for video-related operations.
    video_parser = subparsers.add_parser(
        "video",
        help="video operations",
    )
    # Adding arguments to the video parser for different types of video data.
    video_parser.add_argument(
        "data",
        help="retrievable video data",
        choices=["comments", "views", "streaming_url", "recommended_videos"],
    )
    # Additional arguments for video operations, specifying either ID, title, or URL.
    video_parser.add_argument(
        "-i",
        "--id",
        dest="claim_id",
        type=str,
        help="claim_id: use to get a video's `views`, `comments` or `streaming_url`",
    )
    video_parser.add_argument(
        "-t",
        "--title",
        dest="video_title",
        type=str,
        help="video_title: use with -i/--id to get recommended videos",
    )
    video_parser.add_argument(
        "-cu",
        "--canonical-url",
        dest="canonical_url",
        type=str,
        help="canonical_url: use to get a video's `streaming_url`",
    )

    # Parser for miscellaneous operations.
    miscellaneous_parser = subparsers.add_parser(
        "misc", help="miscellaneous operations"
    )
    # Adding arguments to the miscellaneous parser for different types of miscellaneous data.
    miscellaneous_parser.add_argument(
        "data",
        help="retrievable miscellaneous data",
        choices=["append_comments_reactions", "normalized_names2video_info"],
    )
    miscellaneous_parser.add_argument(
        "-c",
        "--comments",
        dest="comments_list",
        type=list,
        help="(use to get `append_comments_reactions`) a list of dictionaries, each dict corresponding to a JSON"
        " response about a single comment for a specified video.",
    )
    miscellaneous_parser.add_argument(
        "-nn",
        "--normalized-names",
        "--normalised-names",
        dest="normalized_names",
        type=str,
        help="a dash (-) separated list of normalized names (e.g. si-une-tude-montre-que-le-masque-permet): "
        "use with `normalized_names2video_info` to convert normalized names to a list of videos",
    )
    return parser


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
def profiler(enable: bool, options: argparse.Namespace):
    """
    Enables/Disables the profiler.

    Parameters
    ----------
    enable: bool
        A boolean value indicating whether the profiler is enabled/disabled.
    options: argparse
        An argparse namespace object containing profiler options.
    """
    if options.has_been_run:
        if enable:
            yappi.set_clock_type(type=options.clock_type)
            yappi.start()
        else:
            yappi.stop()
            yappi.get_func_stats().sort(
                sort_type=options.sort_type, sort_order=options.sort_order
            ).print_all()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
def run():
    """Main entrypoint for polyphemus cli."""
    parser = create_parser()
    arguments = parser.parse_args()

    # Create a custom Namespace object to store profiler options
    profiler_options = argparse.Namespace(
        has_been_run=arguments.runtime_profiler,
        sort_type=arguments.prof_sort_type,
        sort_order=arguments.prof_sort_order,
        clock_type=arguments.prof_clock_type,
    )

    try:
        if (
            arguments.target in ARGUMENTS_MAPPING
            and arguments.data in ARGUMENTS_MAPPING.get(arguments.target)
        ):
            function, function_arguments = ARGUMENTS_MAPPING.get(arguments.target).get(
                arguments.data
            )

            # Preparing keyword arguments for the function call
            kwargs = {
                cli_argument: getattr(arguments, cli_argument)
                for cli_argument in function_arguments
            }

            # Check for missing expected arguments
            if any(
                kwargs.get(cli_argument) is None for cli_argument in function_arguments
            ):
                print(
                    f"polyphemus {arguments.target}: "
                    f"missing expected argument(s) for `{arguments.data}` operation."
                )
                parser.print_usage()
                return

            # ------------------------------------------- #

            profiler(enable=True, options=profiler_options)

            # Executing the function asynchronously
            call_function = asyncio.run(function(**kwargs))
            pprint(call_function)

            profiler(enable=False, options=profiler_options)

            # ------------------------------------------- #

        else:
            parser.print_usage()

    except KeyboardInterrupt:
        print("User interruption detected (Ctrl+C)")
    except Exception as error:
        print(f"An error occurred: {error}")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ #
