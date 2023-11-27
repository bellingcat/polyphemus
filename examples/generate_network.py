# -*- coding: UTF-8 -*-

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

from pathlib import Path
import pickle
import os

import networkx as nx

import polyphemus

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

CHANNEL_NAME = "PatriotFront"

ITERATIONS = 2

OUTPUT_DIR = Path(
    "../../data", f"{CHANNEL_NAME}_recommendation_iterations={ITERATIONS}"
)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

if __name__ == "__main__":
    engine = polyphemus.base.RecommendationEngine(channel_list=[CHANNEL_NAME])

    weighted_edge_list, channels, claim_id_to_video = engine.generate(
        iterations=ITERATIONS
    )

    G = nx.DiGraph()
    G.add_weighted_edges_from(weighted_edge_list)

    # -------------------------------------------------------------------------#

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    nx.write_gexf(G=G, path=Path(OUTPUT_DIR, "network.gexf"))

    with open(Path(OUTPUT_DIR, f"weighted_edge_list.pkl"), "wb") as f:
        pickle.dump(weighted_edge_list, f)

    with open(Path(OUTPUT_DIR, f"claim_id_to_video.pkl"), "wb") as f:
        pickle.dump(claim_id_to_video, f)

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#
