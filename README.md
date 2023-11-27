# Polyphemus

Scraper for alt-tech video sharing platform [Odysee](https://odysee.com/).

## Installation

Polyphemus can be installed with *pip* or built from source.

### with Pip

```commandline
pip install git+https://github.com/bellingcat/polyphemus.git
```

### Build from source

1. Clone the repo

```commandline
git clone https://github.com/bellingcat/polyphemus
```

2. Navigate to the cloned project repo

```commandline
cd polyphemus
```

3. Build and install

```commandline
pip install .
```

## Usage

### Polyphemus CLI

```commandline
polyphemus -h
```

```commandline
usage: polyphemus [-h] {channel,video,misc} ...

Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.

positional arguments:
  {channel,video,misc}  target
    channel             channel operations
    video               video operations
    misc                miscellaneous data operations

options:
  -h, --help            show this help message and exit

Copyright © 2022-2023 Bellingcat. All rights reserved.

```

#### Examples

##### Get channel profile info

```commandline
polyphemus channel profile --name channel_name
```

##### Get video views

```commandline
polyphemus video views --id claim_id
```

### Polyphemus Library

Polyphemus can also be integrated into other python projects by importing and accessing its scraper classes and
functions

```python
import polyphemus
```

> Code examples are available [here](examples).
