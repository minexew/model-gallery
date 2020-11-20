#!/usr/bin/env python3

import argparse
from datetime import datetime
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import zipfile

from PIL import Image

from db import DB, bad_resource_sha1s

parser = argparse.ArgumentParser()
parser.add_argument('db', type=Path)
parser.add_argument('model_dir', type=Path)
args = parser.parse_args()

db = DB(args.db)


def file_hash(path):
    h = hashlib.sha1()

    with open(path, "rb", buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b""):
            h.update(b)

    return h.hexdigest()

for path in args.model_dir.iterdir():
    print('found', path, file=sys.stderr)

    ext = path.suffix.upper()

    if ext == ".OBJ":
        sha1 = file_hash(path)

        db.add_resource(sha1=sha1, path=path, type=ext)

db.close()
