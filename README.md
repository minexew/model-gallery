# model-gallery

## Usage

```
DB=model-gallery.sqlite
OUTDIR=out/

mkdir -p $OUTDIR
./build_db.py $DB obj_dir/
./update_previews.py $DB $OUTDIR obj_dir/
./make_html.py $DB $OUTDIR
```

## Special thanks

- Blender, sqlite
- https://purecss.io/
