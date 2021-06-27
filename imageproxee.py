#!/usr/bin/env python3
from pathlib import Path
import mimetypes

from PIL import Image
from fire import Fire
from flask import Flask, Response, request

app = Flask(__name__)

root = '.'
CACHE_PATH = Path(__file__).resolve().parent / 'cache'

def get_image(path:Path, mw=768, mh=640, quality=85, ft=None):
    if not ft:
        ft = path.suffix[1:]
    cached_img_hash = str(hash(f'{path}:{mw}:{mh}:{quality}'))
    cached_img_path = CACHE_PATH / f'{cached_img_hash}.{ft}'
    if not cached_img_path.exists():
        img = Image.open(path)
        img.thumbnail((mw, mh))
        img.save(cached_img_path, quality=quality)
    return cached_img_path


@app.route('/<path:path>')
def image(path):
    orig_img_path = Path(path).relative_to(root)
    if not orig_img_path.exists():
        return Response(status=404)
    args = request.args

    mw = int(args.get('mw', 768))
    mh = int(args.get('mw', 640))
    quality = int(args.get('q', 85))
    ft = args.get('ft')

    img_path = get_image(orig_img_path, mw, mh, quality, ft)

    mt, _ = mimetypes.guess_type(img_path)
    print(mt)

    with img_path.open('rb') as img:
        return Response(img.read(), mimetype=mt)


def main(images_root):
    global root
    root = images_root
    if not CACHE_PATH.exists():
        CACHE_PATH.mkdir()
    app.run()

if __name__ == '__main__':
    Fire(main)
