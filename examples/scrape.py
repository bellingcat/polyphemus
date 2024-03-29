# -*- coding: UTF-8 -*-

"""Scrape all video and comment data from a specified Odysee channel
"""

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

import csv
from pathlib import Path 
import os 

import pandas as pd

from polyphemus.base import OdyseeChannelScraper

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

CHANNEL_NAME = 'PatriotFront'
OUTPUT_DIR = Path('.').resolve().parents[1]/'data'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

    odysee_channel = OdyseeChannelScraper(channel_name = CHANNEL_NAME)

    video_list, comment_list = odysee_channel.get_all_videos_and_comments()

    channel_df = pd.DataFrame([odysee_channel.get_entity().__dict__])
    video_df = pd.DataFrame([v.__dict__ for v in video_list])
    comment_df = pd.DataFrame([c.__dict__ for c in comment_list])

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
