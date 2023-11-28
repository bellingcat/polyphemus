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

### Polyphemus CLI

To run the CLI instance of Polyphemus, you have to call it from the command-line and pass in command line arguments.
> Use `-h/--help` to get started

```commandline
polyphemus -h
```

```commandline
usage: polyphemus [-h] [--runtime-prof] [-pct {WALL,CPU}] [-psc {ttot,tsub,tavg,ncall,name,lineno,builtin,threadid,tt_perc,tsub_perc}] {channel,video,misc} ...

Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.

positional arguments:
  {channel,video,misc}  target
    channel             channel operations
    video               video operations
    misc                miscellaneous data operations

options:
  -h, --help            show this help message and exit
  --runtime-prof        enable runtime profiler.
  -pct {WALL,CPU}, --prof-clock-type {WALL,CPU}
                        set profiler clock type (default: CPU)
  -psc {ttot,tsub,tavg,ncall,name,lineno,builtin,threadid,tt_perc,tsub_perc}, --prof-sort {ttot,tsub,tavg,ncall,name,lineno,builtin,threadid,tt_perc,tsub_perc}
                        profiler output sort criterion (default: ncall)

Copyright © 2022-2023 Bellingcat. All rights reserved.

```

#### CLI Examples

##### Get channel profile info

```commandline
polyphemus channel profile --name channel_name
```

##### Get video views

```commandline
polyphemus video views --id claim_id
```

### Polyphemus Python Library

To integrate Polyphemus in your projects, you will need to import it as follows:

```python
from polyphemus import api, base
```

> Code examples are available [here](examples).
