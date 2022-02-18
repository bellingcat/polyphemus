# -*- coding: UTF-8 -*-

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

from pathlib import Path
import pickle
import os

import polyphemus

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

CHANNEL_NAME = 'PatriotFront'

ITERATIONS = 3

OUTPUT_DIR = '../../data'

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == '__main__':

    odysee_channel = polyphemus.base.OdyseeChannel(channel_name = CHANNEL_NAME)

    edge_list = list()
    already_done = list()

    new_videos = odysee_channel.get_all_videos()
    master_video_dict = dict(zip([v.info['claim_id'] for v in new_videos], new_videos))

    for iteration in range(ITERATIONS):
        
        print(f'\n\nITERATION: {iteration}, N_VIDEOS: {len(new_videos)}\n\n')

        for i, video in enumerate(new_videos):
            claim_id = video.info['claim_id']
            title = video.info['title']

            print(f'\nVIDEO: {i}; CLAIM_ID: {claim_id}\n')

            recommended_video_info = polyphemus.api.get_recommended(title, claim_id)

            for rec_video_info in recommended_video_info:
                rec_claim_id = rec_video_info['claim_id']
                print(f'REC_CLAIM_ID: {rec_claim_id}')

                edge_list.append((claim_id, rec_claim_id))

                if rec_video_info['claim_id'] not in master_video_dict:
                    master_video_dict[rec_claim_id] = polyphemus.base.OdyseeVideo(rec_video_info)

            already_done.append(claim_id)

        new_videos = [video for video in master_video_dict.values() if video.info['claim_id'] not in already_done]

    #-------------------------------------------------------------------------#

    os.makedirs(OUTPUT_DIR, exist_ok = True)

    with open(Path(OUTPUT_DIR, 'master_video_dict.pkl'), 'wb') as f:
        pickle.dump(master_video_dict, f)

    with open(Path(OUTPUT_DIR, 'edge_list.pkl'), 'wb') as f:
        pickle.dump(edge_list)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#