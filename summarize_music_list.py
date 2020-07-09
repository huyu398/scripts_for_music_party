import argparse
import pathlib
from io import BytesIO

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from mutagen.mp4 import MP4

def ParseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument('username', type=str)
    parser.add_argument('icon_path', type=pathlib.Path)
    parser.add_argument('music_dir', type=pathlib.Path)
    return parser.parse_args()

def create_username_area(username, icon_path):
    font = ImageFont.truetype('meiryo.ttc', 64, encoding='utf-8')

    username_max_width = font.getsize('@'+'W'*15)[0]
    icon_size = (256, 256)
    icon_margin = (25, 25)
    canvas_size = (icon_size[0]+icon_margin[0]*3+username_max_width, icon_size[1]+icon_margin[1]*2)

    canvas = Image.new('RGB', canvas_size, (255,255,255))
    drawer = ImageDraw.Draw(canvas)

    icon_image = Image.open(str(icon_path)).resize(icon_size, Image.LANCZOS)
    canvas.paste(icon_image, icon_margin)

    username_size = font.getsize('@'+username)
    username_position = (icon_size[0]+icon_margin[0]*2, icon_margin[1]+icon_size[1]/2-username_size[1]/2)
    drawer.text(username_position, '@'+username, font=font, fill='#000')

    return canvas

def create_music_list(music_dir):
    title_font = ImageFont.truetype('meiryo.ttc', 104, encoding='utf-8')
    others_font = ImageFont.truetype('meiryo.ttc', 72, encoding='utf-8')

    file_list = [file_item for file_item in music_dir.iterdir() if file_item.suffix in ['.m4a']]

    textarea_max_width = 1024*3
    artwork_size = (384, 384)
    artwork_margin = (25, 25)
    image_bar_size = (25, 384)
    music_item_size = (artwork_size[0]+artwork_margin[0]*4+image_bar_size[0]+textarea_max_width, artwork_size[1]+artwork_margin[1]*2)
    canvas_size = (music_item_size[0], music_item_size[1]*len(file_list))

    canvas = Image.new('RGB', canvas_size, (255,255,255))

    for i, music_file in enumerate(file_list):
        music_item = Image.new('RGB', music_item_size, (255,255,255))
        drawer = ImageDraw.Draw(music_item)

        meta_info = MP4(str(music_file))
        title = meta_info['\xa9nam'][0] if '\xa9nam' in meta_info.keys() else 'no title'
        artist = meta_info['\xa9ART'][0] if '\xa9ART' in meta_info.keys() else 'no artist'
        album = meta_info['\xa9alb'][0] if '\xa9alb' in meta_info.keys() else 'no album'

        if 'covr' in meta_info.keys():
            artwork = Image.open(BytesIO(meta_info['covr'][0])).resize(artwork_size, Image.LANCZOS)
        else:
            artwork = Image.open('./resource/no_image.png').resize(artwork_size, Image.LANCZOS)
        music_item.paste(artwork, artwork_margin)

        # draw image_bar
        artwork_array = np.asarray(artwork)
        image_bar_color = tuple(int(artwork_array[...,i].mean()) for i in range(3))
        drawer.rectangle((artwork_size[0]+artwork_margin[0]*2, artwork_margin[1],
                          artwork_size[0]+artwork_margin[0]*2+image_bar_size[0], artwork_margin[1]+image_bar_size[1]),
                         fill=image_bar_color)

        # draw meta info
        title_size = title_font.getsize(title)
        drawer.text((artwork_size[0]+artwork_margin[0]*3+image_bar_size[0], artwork_margin[1]*2),
                    title, font=title_font, fill='#000')
        artist_and_album = f'　{artist} / {album}'
        def check_text_length(font, text, limit):
            size = font.getsize(text)
            if limit < size[0]:
                center = int(len(text) / 2)
                text = f'{text[:center]}\n　{text[center:]}'
            return text
        drawer.text((artwork_size[0]+artwork_margin[0]*3+image_bar_size[0], artwork_margin[1]*4+title_size[1]),
                    check_text_length(others_font, artist_and_album, textarea_max_width), font=others_font, fill='#000')

        canvas.paste(music_item, (0, music_item_size[1]*i))

    return canvas

def main(args):
    username_area = create_username_area(args.username, args.icon_path)
    music_list = create_music_list(args.music_dir)

    username_area_position_x = int(music_list.size[0]/2 - username_area.size[0]/2)
    canvas_size = (music_list.size[0], username_area.size[1]+music_list.size[1])

    canvas = Image.new('RGB', canvas_size, (255,255,255))
    canvas.paste(username_area, (username_area_position_x, 0))
    canvas.paste(music_list, (0, username_area.size[1]))

    canvas.save(str(args.music_dir / 'summary.png'))

if __name__ == '__main__':
    args = ParseArgs()
    main(args)
