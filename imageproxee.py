#!/usr/bin/env python3
import mimetypes
from pathlib import Path

from PIL import Image
from fire import Fire
from flask import Flask, Response, request

app = Flask(__name__)

DIR = Path(__file__).resolve().parent
ROOT_PATH = DIR
CACHE_PATH = DIR / 'cache'

def get_image(src_path:Path, mw=768, mh=640, quality=85, ext=None):
    if not ext:
        ext = src_path.suffix[1:]

    dst_hash = str(hash(f'{src_path}:{mw}:{mh}:{quality}'))
    dst_path = CACHE_PATH / f'{dst_hash}.{ext}'

    if (not dst_path.exists()) or src_path.stat().st_mtime > dst_path.stat().st_mtime:
        img = Image.open(src_path)
        img.thumbnail((mw, mh))
        img.save(dst_path, quality=quality)

    return dst_path


@app.route('/<path:path>')
def image(path):
    orig_img_path = (ROOT_PATH / path).resolve()

    if not orig_img_path.exists():
        return Response(status=404)

    get_arg = request.args.get
    get_iarg = lambda n, d: int(get_arg(n, d))

    img_path = get_image(
        orig_img_path,
        get_iarg('mw', 768),
        get_iarg('mh', 640),
        get_iarg('q', 85),
        get_arg('ft')
    )

    mt, _ = mimetypes.guess_type(img_path)

    with img_path.open('rb') as img:
        return Response(img.read(), mimetype=mt)


def main(images_dir, cache_dir='cache'):
    global ROOT_PATH
    global CACHE_PATH

    ROOT_PATH = Path(images_dir).resolve()
    CACHE_PATH = Path(cache_dir).resolve()

    CACHE_PATH.mkdir(exist_ok=True)

    app.run()

if __name__ == '__main__':
    Fire(main)
