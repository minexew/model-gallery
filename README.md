# model-gallery

## Usage

```
DB=model-gallery.sqlite
OUTDIR=out/

mkdir -p $OUTDIR
./analysis/build_db.py $DB obj_dir/
./analysis/update_previews.py $DB $OUTDIR obj_dir/
./analysis/make_html.py $DB $OUTDIR
```

## Special thanks

- Blender, sqlite
- https://purecss.io/
