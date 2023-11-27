# Polyphemus

Scraper for alt-tech video sharing platform [Odysee](https://odysee.com/).

### TODO

- [x] Implement CLI
- [ ] Profile run-time, look into implementing async requests

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
Usage: polyphemus [-h] {channel,video} ...

Polyphemus: Scraper for Odysee, an alt-tech platform for sharing video.

Positional Arguments:
  {channel,video}  init mode
    channel        channel operations
    video          video operations

Options:
  -h, --help       show this help message and exit

Copyright © 2022-2023 Bellingcat. All rights reserved.
```

#### Examples

##### Get channel profile info

```commandline
polyphemus channel --name channel_name --profile
```

##### Get video views

```commandline
polyphemus video --id claim_id --views
```

### Polyphemus Library

Polyphemus can also be integrated into other python projects by importing and accessing its scraper classes and
functions

```python
import polyphemus
```

> Code examples are available [here](examples).
