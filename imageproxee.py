#!/usr/bin/env python3
from pathlib import Path
import mimetypes

from PIL import Image
from fire import Fire
from flask import Flask, Response, request

app = Flask(__name__)

DIR = Path(__file__).resolve().parent
ROOT_PATH = DIR
CACHE_PATH = DIR / 'cache'

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
    orig_img_path = (ROOT_PATH / path).resolve(True)
    if not orig_img_path.exists():
        return Response(status=404)
    arg = request.args.get

    mw = int(arg('mw', 768))
    mh = int(arg('mh', 640))
    quality = int(arg('q', 85))
    ft = arg('ft')

    img_path = get_image(orig_img_path, mw, mh, quality, ft)

    mt, _ = mimetypes.guess_type(img_path)

    with img_path.open('rb') as img:
        return Response(img.read(), mimetype=mt)


def main(images_dir, cache_dir='cache'):
    global ROOT_PATH
    global CACHE_PATH
    ROOT_PATH = Path(images_dir).resolve()
    CACHE_PATH = Path(cache_dir).resolve()
    if not CACHE_PATH.exists():
        CACHE_PATH.mkdir()
    app.run()

if __name__ == '__main__':
    Fire(main)
