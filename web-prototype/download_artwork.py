#!/usr/bin/env python3
"""Download credited upstream artwork and produce a single-file offline copy.
Run from this folder: python download_artwork.py
Python standard library only. Never uploads conversation data or credentials.
"""
from __future__ import annotations
import base64
from pathlib import Path
import sys
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parent
ARTWORK = {
    'dark': 'https://raw.githubusercontent.com/Small-tailqwq/dsh-deep-whale/HEAD/maid-atelier/preview/dark.webp',
    'light': 'https://raw.githubusercontent.com/small-tailqwq/dsh-deep-whale/main/maid-atelier/preview/light.webp',
}

def main() -> int:
    original = ROOT / 'index.html'
    if not original.exists():
        print('找不到同目录下的 index.html。')
        return 1
    html = original.read_text(encoding='utf-8')
    target = ROOT / 'assets'
    target.mkdir(exist_ok=True)
    for scheme, url in ARTWORK.items():
        path = target / f'maid-atelier-{scheme}.webp'
        try:
            if path.exists():
                image = path.read_bytes()
            else:
                request = urllib.request.Request(url, headers={'User-Agent': 'MeijianArtworkPack/1.0'})
                with urllib.request.urlopen(request, timeout=35) as response:
                    image = response.read(20_000_001)
            if len(image) > 20_000_000 or not (image[:4] == b'RIFF' and image[8:12] == b'WEBP'):
                raise ValueError('资源不是有效的 WebP 图片，或大小超出 20 MB。')
            path.write_bytes(image)
            data_url = 'data:image/webp;base64,' + base64.b64encode(image).decode('ascii')
            html = html.replace(url, data_url)
            print(f'已取得 {scheme} 原图 ({len(image):,} bytes)。')
        except (OSError, ValueError, urllib.error.URLError) as error:
            print(f'未能取得 {scheme} 图片：{error}')
            print('没有生成不完整的离线版；原 index.html 保持不变。')
            return 1
    out = ROOT / '眉间_深海工坊_离线完整版.html'
    out.write_text(html, encoding='utf-8')
    print(f'已生成：{out.name}\n可双击打开；主题图片不再依赖网络。')
    return 0

if __name__ == '__main__':
    sys.exit(main())
