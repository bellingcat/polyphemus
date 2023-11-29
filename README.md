# Polyphemus

Scraper for alt-tech video sharing platform [Odysee](https://odysee.com/).

## Installation

Polyphemus can be installed with *pip* or built from source.

### Installing with Pip

```commandline
pip install git+https://github.com/bellingcat/polyphemus.git
```

### Building from source

1. Clone the repo

```commandline
git clone https://github.com/bellingcat/polyphemus
```

2. Navigate to the cloned project directory

```commandline
cd polyphemus
```

3. Build and install.

```commandline
pip install .
```

## Usage

Polyphemus can be run directly from the command-line or imported as a Python library

## Polyphemus CLI

To run the CLI instance of Polyphemus, you have to call it from the command-line and pass in command line arguments.
> Use `-h/--help` to get started

### Main

```commandline
polyphemus --help
```

```commandline
usage: polyphemus [-h] [--runtime-prof] [-pct {WALL,CPU}]
                  [-pst {ttot,tsub,tavg,ncall,name}] [-pso {asc,desc}]
                  {channel,video,misc} ...

Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.

positional arguments:
  {channel,video,misc}  target
    channel             channel operations
    video               video operations
    misc                miscellaneous operations

options:
  -h, --help            show this help message and exit
  --runtime-prof        enable runtime profiler
  -pct {WALL,CPU}, --prof-clock-type {WALL,CPU}
                        set profiler clock type (default: CPU)
  -pst {ttot,tsub,tavg,ncall,name}, --prof-sort-type {ttot,tsub,tavg,ncall,name}
                        set profiler stats' sort type (default: ncall)
  -pso {asc,desc}, --prof-sort-order {asc,desc}
                        set profiler stats' sort order (default: desc)

Copyright © 2022-2023 Bellingcat. All rights reserved.
```

### Channel Operations

```commandline
polyphemus channel --help
```

```commandline
usage: polyphemus channel [-h] [-n CHANNEL_NAME] [-i CHANNEL_ID]
                          {profile,subscribers,videos}

positional arguments:
  {profile,subscribers,videos}
                        retrievable channel data

options:
  -h, --help            show this help message and exit
  -n CHANNEL_NAME, --name CHANNEL_NAME
                        channel_name: use to get a channel's `profile`
  -i CHANNEL_ID, --id CHANNEL_ID
                        channel_id: use to get a channel's `subscribers` or
                        `videos`
```

### Video Operations

```commandline
polyphemus video --help
```

```commandline
usage: polyphemus video [-h] [-i CLAIM_ID] [-t VIDEO_TITLE]
                        [-cu CANONICAL_URL]
                        {comments,views,streaming_url,recommended_videos}

positional arguments:
  {comments,views,streaming_url,recommended_videos}
                        retrievable video data

options:
  -h, --help            show this help message and exit
  -i CLAIM_ID, --id CLAIM_ID
                        claim_id: use to get a video's `views`, `comments` or
                        `streaming_url`
  -t VIDEO_TITLE, --title VIDEO_TITLE
                        video_title: use with -i/--id to get recommended
                        videos
  -cu CANONICAL_URL, --canonical-url CANONICAL_URL
                        canonical_url: use to get a video's `streaming_url`
```

### Miscellaneous Operations

```commandline
polyphemus misc --help
```

```commandline
usage: polyphemus misc [-h] [-c COMMENTS_LIST] [-nn NORMALIZED_NAMES]
                       {append_comments_reactions,normalized_names2video_info}

positional arguments:
  {append_comments_reactions,normalized_names2video_info}
                        retrievable miscellaneous data

options:
  -h, --help            show this help message and exit
  -c COMMENTS_LIST, --comments COMMENTS_LIST
                        (use to get `append_comments_reactions`) a list of
                        dictionaries, each dict corresponding to a JSON
                        response about a single comment for a specified video.
  -nn NORMALIZED_NAMES, --normalized-names NORMALIZED_NAMES, --normalised-names NORMALIZED_NAMES
                        a dash (-) separated list of normalized names (e.g.
                        si-une-tude-montre-que-le-masque-permet): use with
                        `normalized_names2video_info` to convert normalized
                        names to a list of videos
```

## Polyphemus Python Library

To integrate Polyphemus in Python projects or scripts, you will need to import the `api` and `base` modules as follows:

```python
from polyphemus import api, base
```

> Code examples are available [here](examples).
