#!/usr/bin/env python3

import argparse
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile
import zipfile

from PIL import Image

from db import DB, PreviewsDB

sys.path.insert(0, "../MascotCapsule/tools")
from render_obj import render_obj

MIN_VERSION = 4
VERSION = 5

# v5: add model orientation information in DB

parser = argparse.ArgumentParser()
parser.add_argument("db")
parser.add_argument("workdir", type=Path)
parser.add_argument("--resource")
parser.add_argument("model_dir", type=Path)

args = parser.parse_args()

rel_full_dir = Path("full")
rel_thumbs_dir = Path("thumbs")

workdir = args.workdir
workdir.mkdir(exist_ok=True)
(workdir / rel_full_dir).mkdir(exist_ok=True)
(workdir / rel_thumbs_dir).mkdir(exist_ok=True)

db = DB(args.db)
previews_db = PreviewsDB(workdir / "previews.sqlite")


def file_hash(path):
    h = hashlib.sha1()

    with open(path, "rb", buffering=0) as f:
        for b in iter(lambda: f.read(128 * 1024), b""):
            h.update(b)

    return h.hexdigest()


def stream_hash(f):
    h = hashlib.sha1()

    for b in iter(lambda: f.read(128 * 1024), b""):
        h.update(b)

    return h.hexdigest()


def my_render_obj(path, rel_output_path, is_thumb, resolution):
    # TODO: search by exact resolution instead of is_thumb
    record = previews_db.get_mbac_preview(source=str(path), thumb=is_thumb)

    axis_forward = "X"
    axis_up = "Y"

    output_path = workdir / rel_output_path

    if (
        record
        and record["version"] >= MIN_VERSION
        and record["axis_forward"] == axis_forward
        and record["axis_up"] == axis_up
        and output_path.is_file()
    ):
        print("UP-TO-DATE", rel_output_path)
        return

    print(
        f"RENDER path={path} {resolution=} {is_thumb=} {axis_forward=} {axis_up=}"
    )

    with NamedTemporaryFile() as imagefile:
        render_obj(
            path,
            imagefile.name,     # blender will add its own suffix, see below
            None,
            resolution=resolution,
            axis_forward=axis_forward,
            axis_up=axis_up,
        )

        shutil.move(f"{imagefile.name}0000.png", output_path)

    previews_db.add_mbac_preview(
        source=str(path),
        thumb=is_thumb,
        filename=str(rel_output_path),
        width=resolution[0],
        height=resolution[1],
        version=VERSION,
        axis_forward=axis_forward,
        axis_up=axis_up,
    )


# previews

for path in args.model_dir.iterdir():
    if args.resource and path != args.resource:
        continue

    ext = path.suffix.upper()

    if ext == ".OBJ":
        my_render_obj(
            path,
            rel_thumbs_dir / (path.stem + ".png"),

            is_thumb=True,
            resolution=(256, 144),
        )

# full-size renders

for path in args.model_dir.iterdir():
    if args.resource and path != args.resource:
        continue

    ext = path.suffix.upper()

    if ext == ".OBJ":
        my_render_obj(
            path,
            rel_full_dir / (path.stem + ".png"),

            is_thumb=False,
            resolution=(1280, 720),
        )
