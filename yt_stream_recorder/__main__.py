#!/bin/python

import sys
from pathlib import Path

proj_path = str(Path(__file__).parent.parent.resolve())

if proj_path not in sys.path:
    sys.path.append(
        proj_path
    )

import yt_stream_recorder
