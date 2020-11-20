#!/usr/bin/env python3

import argparse
import base64
import os
from pathlib import Path
import sys
import zipfile

from PIL import Image

from db import DB

parser = argparse.ArgumentParser()
parser.add_argument("db")
parser.add_argument("outputdir", type=Path)

args = parser.parse_args()

db = DB(args.db)

args.outputdir.mkdir(exist_ok=True)

full_dir = args.outputdir / "full"
thumbs_dir = args.outputdir / "thumbs"

# TODO: should obviously use Jinja or something
with open(args.outputdir / "index.html", "wt") as f:
    f.write(
        '<link rel="stylesheet" href="https://unpkg.com/purecss@1.0.1/build/pure-min.css" '
        'integrity="sha384-oAOxQR6DkCoMliIh8yFnu25d7Eq/PHS21PClpwjOTeU2jRSq11vu66rf90/cZr47" '
        'crossorigin="anonymous">\n'
    )

    # https://stackoverflow.com/a/1094933
    def sizeof_fmt(num, suffix="B"):
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, "Yi", suffix)

    # sort resources by path
    resources_by_path = dict()

    for res in db.resources():
        p = Path(res["path"])

        try:
            resources_by_path[p.parent].append(res)
        except KeyError:
            resources_by_path[p.parent] = [res]

    def display_cell(f, res):
        f.write('<div class="pure-u-1-6" style="text-align: center">')

        p = Path(res["path"])

        full = (full_dir / f'{p.stem}.png').is_file()
        # thumb = (thumbs_dir / f'{res["sha1"]}.png').is_file()

        if full:
            f.write(f'<a href="full/{p.stem}.png">')
        f.write(f'<img src="thumbs/{p.stem}.png">')
        if full:
            f.write("</a>")

        f.write(f'<p style="font-size: 12px">{p.name}</p>')
        f.write("</div>\n")

    f.write("<h2>Models</h2>")

    for path, resources in resources_by_path.items():
        filtered = [res for res in resources if res["type"] == ".OBJ"]
        if not len(filtered):
            continue

        f.write(f"<h3>{path}</h3>")
        f.write('<div class="pure-g">\n')

        for res in filtered:
            display_cell(f, res)

        f.write("</div>")

db.close()
