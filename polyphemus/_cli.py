# -*- coding: UTF-8 -*-

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
import argparse
import asyncio
import cProfile
import pstats
from pprint import pprint

from . import api


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#


# Function to create and configure the argument parser.
def create_parser() -> argparse.ArgumentParser:
    # Create a parser with a description of the tool.
    parser = argparse.ArgumentParser(
        description="Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.",
        epilog="Copyright © 2022-2023 Bellingcat. All rights reserved.",
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
        "data", help="channel data", choices=["profile", "subscribers", "videos"]
    )
    # Additional arguments for channel operations, specifying either name or ID.
    channel_parser.add_argument(
        "-n",
        "--name",
        help="channel_name: use to get `profile`",
        type=str,
        dest="channel_name",
    )
    channel_parser.add_argument(
        "-i",
        "--id",
        help="channel_id: use to get `subscribers` or `videos`",
        type=str,
        dest="channel_id",
    )

    # Parser for video-related operations.
    video_parser = subparsers.add_parser(
        "video",
        help="video operations",
    )
    # Adding arguments to the video parser for different types of video data.
    video_parser.add_argument(
        "data",
        help="video data",
        choices=["comments", "views", "streaming_url", "recommended_videos"],
    )
    # Additional arguments for video operations, specifying either ID, title, or URL.
    video_parser.add_argument(
        "-i",
        "--id",
        help="video/claim_id: use to get `views`, `comments` or `streaming_url`",
        type=str,
        dest="claim_id",
    )
    video_parser.add_argument(
        "-t",
        "--title",
        help="video_title: use with -i/--id to get recommended videos",
        type=str,
        dest="video_title",
    )
    video_parser.add_argument(
        "-Cu",
        "--canonical-url",
        help="video canonical_url: use to get a video's `streaming_url`",
        dest="canonical_url",
        type=str,
    )

    # Parser for miscellaneous operations.
    miscellaneous_parser = subparsers.add_parser(
        "misc", help="miscellaneous data operations"
    )
    # Adding arguments to the miscellaneous parser for different types of miscellaneous data.
    miscellaneous_parser.add_argument(
        "data", choices=["append_comments_reactions", "normalized_names2video_info"]
    )
    miscellaneous_parser.add_argument(
        "-c",
        "--comments",
        dest="comments_list",
        help="(use to get `append_comments_reactions`) list of dictionaries, each dict corresponding to a JSON"
        " response about a single comment for a specified video.",
    )
    miscellaneous_parser.add_argument(
        "-Nn",
        "--normalized-names",
        dest="normalized_names",
        help="a dash (-) separated list of normalized names (e.g. si-une-tude-montre-que-le-masque-permet): "
        "use with `normalized_names2video_info` to convert normalized names to a list of videos",
    )
    return parser


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

# Mapping of functions to their respective command-line arguments.
arguments_mapping: dict = {
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


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
def main():
    """Main entrypoint for polyphemus cli."""
    arguments: argparse = create_parser().parse_args()

    try:
        # Validate and execute the command based on user input.
        if (
            arguments.target in arguments_mapping
            and arguments.data in arguments_mapping.get(arguments.target)
        ):
            function, function_arguments = arguments_mapping.get(arguments.target).get(
                arguments.data
            )

            # Preparing keyword arguments for the function call.
            kwargs: dict = {
                argument: getattr(arguments, argument)
                for argument in function_arguments
            }

            # Check for missing expected arguments before calling the function.
            if any(kwargs.get(argument) is None for argument in function_arguments):
                print(
                    f"polyphemus {arguments.target}: missing expected argument(s) for `{arguments.data}` operation."
                )
                # Display usage if one or more expected arguments are missing.
                create_parser().print_usage()
                return
            # Running the profiler
            profiler = cProfile.Profile()
            profiler.enable()

            # Call the function with prepared arguments.
            call_function = asyncio.run(function(**kwargs))
            pprint(call_function)

            profiler.disable()
            stats = pstats.Stats(profiler)
            stats.sort_stats("cumulative").print_stats(10)

        else:
            # Display usage if arguments.data is not valid.
            create_parser().print_usage()

    except KeyboardInterrupt:
        # Handle user interruption exception
        print("User interruption detected (Ctrl+C)")
    except Exception as error:
        # General exception handling for any unexpected errors.
        print(f"An unknown error occurred: {error}")


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
