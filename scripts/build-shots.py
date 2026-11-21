#!/usr/bin/env python3
"""Собирает кадры игр для писем: lessons/games/shots/NN-name.svg.

Кадр — это сцена игры в момент запуска: фон, видимые спрайты на своих местах
и переменные в углу. Положения берутся из project.json внутри .sb3,
поэтому кадр всегда соответствует игре.

Запуск:   python3 scripts/build-shots.py [каталог для SVG]
          python3 scripts/build-shots.py --course2 [каталог для SVG]
По умолчанию SVG пишутся во временный каталог /tmp/vlabs-shots.
С ключом --course2 читаются игры и кадры курса 2 (lessons/course-2/games).

В письмо попадает PNG (почтовые программы не показывают SVG), поэтому после
сборки каждый SVG нужно один раз открыть в браузере размером 480×360 и сохранить
снимок как lessons/games/NN-name.png (960×720). В репозитории хранятся только PNG.
"""
import base64
import json
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
GAMES = ROOT / 'lessons' / 'games'
GAMES2 = ROOT / 'lessons' / 'course-2' / 'games'

# Что показать в кадре сверх начального состояния: значения переменных,
# спрятанные до запуска клоны, содержимое списка. Только для наглядности.
EXTRA = {
    '01-events': {'vars': {'Событий': 3, 'Нажатий': 5}, 'clones': [('Капля', 90, 0), ('Капля', 135, -40), ('Капля', 175, -5)]},
    '02-motion': {'vars': {'Маяки': 2}, 'move': {'Ракета': (-60, -40)}},
    '04-sound': {'vars': {'Мелодия': 'Имперский марш'}},
    '05-control': {'vars': {'Очки': 12, 'Уровень': 2},
                   'clones': [('Метеор', -130, 70), ('Метеор', 60, 120), ('Метеор', 170, -45), ('Звезда', -40, 20)]},
    '06-sensing': {'vars': {'Подсказка': 'Тепло', 'Найдено': 2, 'Мышь x': -40, 'Мышь y': -12}, 'move': {'Следопыт': (-40, -12)}},
    '07-operators': {'vars': {'Очки': 3, 'Вопрос': 4}},
    '08-data': {'vars': {'Счётчик': 3}, 'list': ['Собака', 'Велосипед', 'Полететь в космос']},
}

# Кадры курса 2: показываем, как игра выглядит в разгаре, а не в начальной точке.
EXTRA2 = {
    '01-chase': {'vars': {'Очки': 2, 'Время': 18}},
    '02-platform': {'vars': {'Монеты': 1}, 'move': {'Герой': (60, 62)}},
    '03-maze': {'vars': {'Ключи': 2, 'Жизни': 2}},
    '04-catcher': {'vars': {'Очки': 4, 'Жизни': 2, 'Время': 12},
                   'clones': [('Яблоко', 80, -110), ('Яблоко', -60, -40), ('Бомба', 150, 40)]},
    '05-pursuit': {'vars': {'Ключи': 2, 'Жизни': 2}, 'move': {'Тень': (-40, -10)}},
    '06-shooter': {'vars': {'Очки': 3, 'Время': 20},
                   'clones': [('Мишень', 50, 120), ('Мишень', -100, 80), ('Пуля', 30, 30)]},
    '07-quest': {'vars': {'Найдено': 2, 'Уровень': 1}},
    '08-own-game': {'vars': {'Очки': 2, 'Жизни': 2}},
}


def image(data, x, y, w, h):
    uri = 'data:image/svg+xml;base64,' + base64.b64encode(data).decode()
    return f'<image href="{uri}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/>'


def size_of(svg):
    """Ширина и высота костюма из атрибутов корневого <svg>."""
    import re
    head = svg[:400].decode('utf-8', 'replace')
    w = float(re.search(r'width="([\d.]+)"', head).group(1))
    h = float(re.search(r'height="([\d.]+)"', head).group(1))
    return w, h


def sprite(z, target, x=None, y=None):
    c = target['costumes'][target['currentCostume']]
    data = z.read(c['md5ext'])
    w, h = size_of(data)
    k = target['size'] / 100
    x = target['x'] if x is None else x
    y = target['y'] if y is None else y
    return image(data, 240 + x - c['rotationCenterX'] * k, 180 - y - c['rotationCenterY'] * k, w * k, h * k)


def monitor(m, value):
    name = m['params'].get('VARIABLE') or m['params'].get('LIST')
    x, y = m['x'], m['y']
    font = 'font-family="Arial,Helvetica,sans-serif" font-weight="700"'
    if m['mode'] == 'list':
        w, h = m['width'], m['height']
        rows = ''.join(
            f'<text x="{x + 9}" y="{y + 43 + i * 24}" font-size="11" fill="#575e75" {font}>{i + 1}</text>'
            f'<rect x="{x + 22}" y="{y + 28 + i * 24}" width="{w - 30}" height="21" rx="3" fill="#fc662c"/>'
            f'<text x="{x + 28}" y="{y + 43 + i * 24}" font-size="11.5" fill="#fff" {font}>{escape(str(v))}</text>'
            for i, v in enumerate(value))
        return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#e6f0ff" stroke="#c4ccd9"/>'
                f'<rect x="{x}" y="{y}" width="{w}" height="23" rx="4" fill="#fff" stroke="#c4ccd9"/>'
                f'<text x="{x + w / 2}" y="{y + 16}" font-size="11.5" text-anchor="middle" fill="#575e75" {font}>{escape(name)}</text>'
                f'{rows}'
                f'<text x="{x + w / 2}" y="{y + h - 7}" font-size="10.5" text-anchor="middle" fill="#575e75" {font}>длина {len(value)}</text>')
    label, val = escape(name), escape(str(value))
    lw, vw = 7.6 * len(name) + 4, max(7.6 * len(str(value)) + 12, 26)
    return (f'<rect x="{x}" y="{y}" width="{lw + vw + 17}" height="21" rx="4" fill="#e6f0ff" stroke="#c4ccd9"/>'
            f'<text x="{x + 7}" y="{y + 15}" font-size="11.5" fill="#575e75" {font}>{label}</text>'
            f'<rect x="{x + lw + 10}" y="{y + 3}" width="{vw}" height="15" rx="3" fill="#ff8c1a"/>'
            f'<text x="{x + lw + 10 + vw / 2}" y="{y + 14}" font-size="11.5" text-anchor="middle" fill="#fff" {font}>{val}</text>')


def scene(path, extra_map=EXTRA):
    extra = extra_map.get(path.stem, {})
    with zipfile.ZipFile(path) as z:
        p = json.loads(z.read('project.json'))
        targets = {t['name']: t for t in p['targets']}
        stage = next(t for t in p['targets'] if t['isStage'])
        back = stage['costumes'][stage['currentCostume']]
        parts = [image(z.read(back['md5ext']), 0, 0, 480, 360)]
        for t in sorted((t for t in p['targets'] if not t['isStage']), key=lambda t: t['layerOrder']):
            if t['visible']:
                parts.append(sprite(z, t, *extra.get('move', {}).get(t['name'], (None, None))))
            parts += [sprite(z, targets[n], x, y) for n, x, y in extra.get('clones', []) if n == t['name']]
        for m in p.get('monitors', []):
            if not m['visible']:
                continue
            name = m['params'].get('VARIABLE') or m['params'].get('LIST')
            value = extra.get('list', m['value']) if m['mode'] == 'list' else extra.get('vars', {}).get(name, m['value'])
            parts.append(monitor(m, value))
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">'
            '<defs><clipPath id="s"><rect width="480" height="360"/></clipPath></defs>'
            f'<g clip-path="url(#s)">{"".join(parts)}</g></svg>')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    course2 = '--course2' in sys.argv[1:]
    out = Path(args[0] if args else '/tmp/vlabs-shots')
    out.mkdir(parents=True, exist_ok=True)
    games = sorted((GAMES2 if course2 else GAMES).glob('*.sb3'))
    for path in games:
        (out / f'{path.stem}.svg').write_text(scene(path, EXTRA2 if course2 else EXTRA), encoding='utf-8')
    print(f'Кадров: {len(games)} → {out}')


if __name__ == '__main__':
    main()
