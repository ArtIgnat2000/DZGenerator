#!/usr/bin/env python3
"""Build the eight mini-games of course 2 and their starters.

    lessons/course-2/games/NN-name.sb3           демо-игра урока: играем до урока;
    lessons/course-2/practice/NN-name-start.sb3  заготовка: те же герои и фоны без программы.

The finished demo doubles as the «разгадка» of the practice: in course 2 the lesson
builds exactly the game the child played before the lesson.

Run:    python3 scripts/build-course2.py
Check:  python3 scripts/build-course2.py --check
"""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('build_games', ROOT / 'scripts' / 'build-games.py')
games = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(games)
globals().update({name: value for name, value in vars(games).items() if not name.startswith('__')})

GAME_OUT = ROOT / 'lessons' / 'course-2' / 'games'
START_OUT = ROOT / 'lessons' / 'course-2' / 'practice'

# ───────────────────────────── Artwork ─────────────────────────────
# Same rules as course 1: only basic SVG shapes Scratch Paint supports.

def fox_svg():
    return svg(96, 96,
        '<path d="M18 18 34 34 48 12 62 34 78 18 74 52 48 86 22 52Z" fill="#ef8b3c" stroke="#ffd7a8" stroke-width="2"/>'
        '<path d="M18 18 34 34 30 48 22 52Z" fill="#c96a24"/><path d="M78 18 62 34 66 48 74 52Z" fill="#c96a24"/>'
        '<path d="M30 52q18 20 36 0-6 24-18 26-12-2-18-26Z" fill="#fff2e0"/>'
        '<circle cx="38" cy="52" r="4" fill="#24303f"/><circle cx="58" cy="52" r="4" fill="#24303f"/>'
        '<path d="M45 64h6l-3 5Z" fill="#24303f"/><path d="M43 72q5 4 10 0" fill="none" stroke="#24303f" stroke-width="2.5" stroke-linecap="round"/>')

def star_svg():
    return svg(96, 96,
        '<path d="M48 6 59 36 91 38 66 58 74 90 48 72 22 90 30 58 5 38 37 36Z" fill="#ffd75e" stroke="#fff3b0" stroke-width="3"/>'
        '<circle cx="41" cy="48" r="3" fill="#6b4a10"/><circle cx="55" cy="48" r="3" fill="#6b4a10"/>'
        '<path d="M42 57q6 5 12 0" fill="none" stroke="#6b4a10" stroke-width="2.5" stroke-linecap="round"/>')

def shadow_svg():
    return svg(96, 96,
        '<path d="M48 8c18 0 30 14 30 32 0 12-7 16-7 26 0 8 8 10 8 18H17c0-8 8-10 8-18 0-10-7-14-7-26C18 22 30 8 48 8Z" fill="#40325c"/>'
        '<circle cx="37" cy="44" r="5" fill="#f6e7ff"/><circle cx="59" cy="44" r="5" fill="#f6e7ff"/>'
        '<path d="M38 58q10 8 20 0" fill="none" stroke="#f6e7ff" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M30 78q18 10 36 0" fill="none" stroke="#6b57a0" stroke-width="3" stroke-linecap="round"/>')

def robot_svg():
    return svg(96, 96,
        '<path d="M28 22h40q8 0 8 8v38q0 8-8 8H28q-8 0-8-8V30q0-8 8-8Z" fill="#8fd6e8" stroke="#e6f8ff" stroke-width="3"/>'
        '<path d="M48 22V10" stroke="#c9d7e2" stroke-width="4" stroke-linecap="round"/><circle cx="48" cy="9" r="5" fill="#ff8b60"/>'
        '<circle cx="36" cy="44" r="7" fill="#fff"/><circle cx="60" cy="44" r="7" fill="#fff"/>'
        '<circle cx="37" cy="45" r="3.5" fill="#1d2b3a"/><circle cx="59" cy="45" r="3.5" fill="#1d2b3a"/>'
        '<path d="M38 60h20" stroke="#1d2b3a" stroke-width="3" stroke-linecap="round"/>'
        '<path d="M18 38h-8v18h8M78 38h8v18h-8" fill="#6aa9c4"/>')

def platform_svg():
    return svg(140, 26,
        '<path d="M4 0h132v20H4Z" fill="#8a6136"/><path d="M0 4h140v18H0Z" fill="#b07c46"/>'
        '<path d="M8 22h124v4H8Z" fill="#6b4a2a"/>'
        '<circle cx="28" cy="12" r="3" fill="#8a6136"/><circle cx="70" cy="9" r="2.5" fill="#8a6136"/>'
        '<circle cx="112" cy="13" r="3.5" fill="#8a6136"/>')

def coin_svg():
    return svg(64, 64,
        '<circle cx="32" cy="32" r="27" fill="#ffd75e" stroke="#fff3b0" stroke-width="3"/>'
        '<path d="M32 14 36 26 48 27 39 35 42 47 32 40 22 47 25 35 16 27 28 26Z" fill="#c98d12"/>')

def basket_svg():
    return svg(96, 96,
        '<path d="M18 42h60l-8 42H26Z" fill="#e2a55a" stroke="#fff0d2" stroke-width="3" stroke-linejoin="round"/>'
        '<path d="M22 56h52M25 70h46M36 42l3 42M48 42v42M60 42l-3 42" fill="none" stroke="#b9773a" stroke-width="3"/>')

def apple_svg():
    return svg(64, 64,
        '<circle cx="32" cy="36" r="22" fill="#e8483f"/><circle cx="24" cy="28" r="0"/>'
        '<path d="M32 15q-2-8 6-11" fill="none" stroke="#3f8f4f" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M33 17q8-8 16-2-6 10-16 2Z" fill="#59c46b"/>'
        '<path d="M24 26q5-4 9 0" fill="none" stroke="#ff9a92" stroke-width="3" stroke-linecap="round"/>')

def bomb_svg():
    return svg(64, 64,
        '<circle cx="30" cy="38" r="22" fill="#33364d"/><circle cx="23" cy="31" r="6" fill="#5b5f7e"/>'
        '<path d="M44 22q10-8 16 0" fill="none" stroke="#8a6136" stroke-width="4" stroke-linecap="round"/>'
        '<path d="M56 18q4-8 10-4" fill="none" stroke="#ffb95c" stroke-width="3" stroke-linecap="round"/>'
        '<circle cx="62" cy="12" r="4" fill="#ffcf5c"/>')

def cannon_svg():
    return svg(96, 96,
        '<path d="M28 40h40v26H28Z" fill="#51708f" stroke="#cfe6ff" stroke-width="3"/>'
        '<path d="M40 40V16h16v24Z" fill="#6f93b6" stroke="#cfe6ff" stroke-width="3"/>'
        '<circle cx="48" cy="70" r="16" fill="#374b63" stroke="#9dc0e0" stroke-width="3"/>'
        '<circle cx="48" cy="70" r="6" fill="#ffd75e"/>')

def bullet_svg():
    return svg(24, 24, '<circle cx="12" cy="12" r="9" fill="#ffe36d" stroke="#fff6c8" stroke-width="2"/>')

def target_svg():
    return svg(80, 80,
        '<circle cx="40" cy="40" r="35" fill="#ff7c63" stroke="#ffe0a1" stroke-width="3"/>'
        '<circle cx="40" cy="40" r="24" fill="#fff4d6"/><circle cx="40" cy="40" r="12" fill="#ff7c63"/>'
        '<circle cx="40" cy="40" r="4" fill="#fff4d6"/>')

def door_svg():
    return svg(96, 128,
        '<path d="M8 120V48a40 40 0 0 1 80 0v72Z" fill="#8a5a2b" stroke="#ffd7a8" stroke-width="4"/>'
        '<path d="M20 120V48a28 28 0 0 1 56 0v72Z" fill="#b57a3c"/>'
        '<circle cx="66" cy="84" r="5" fill="#ffd75e"/>'
        '<path d="M8 120h80" stroke="#6b4a2a" stroke-width="6"/>')

def key_svg():
    return svg(64, 64,
        '<circle cx="20" cy="32" r="12" fill="none" stroke="#ffd75e" stroke-width="7"/>'
        '<path d="M32 32h26m-8 0v10m-8-10v8" stroke="#ffd75e" stroke-width="7" stroke-linecap="round"/>')

def maze_walls_svg():
    walls = [
        (0, 0, 480, 11), (0, 351, 480, 9), (0, 0, 9, 360), (469, 0, 11, 360),
        (329, 0, 151, 61),
        (0, 81, 239, 10), (319, 61, 10, 120), (79, 171, 250, 10),
        (0, 261, 159, 10), (239, 261, 241, 10),
    ]
    return svg(480, 360, ''.join(f'<path d="M{x} {y}h{w}v{h}h{-w}Z" fill="#59e0c8"/>' for x, y, w, h in walls))

def meadow_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#a8dcf2"/>'
        '<circle cx="86" cy="70" r="38" fill="#ffe98a"/><circle cx="86" cy="70" r="28" fill="#fff3b0"/>'
        '<path d="M0 238q92-58 180 0t160-6q74-50 140 2v126H0Z" fill="#6cc27a"/>'
        '<path d="M0 292q96-40 182 0t162 0q70-32 136 0v68H0Z" fill="#3f9c64"/>'
        '<path d="M0 326q94-26 176 0t160 0q76-24 144 0v34H0Z" fill="#2d7d52"/>')

def sky_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#bde7fa"/>'
        '<path d="M60 80q0-22 22-22 6-18 26-18 20 0 26 18 20 2 20 22Z" fill="#ffffff" opacity=".85"/>'
        '<path d="M330 120q0-18 18-18 6-16 22-16 18 0 22 16 18 2 18 18Z" fill="#ffffff" opacity=".7"/>'
        '<path d="M0 300h480v60H0Z" fill="#4f9a5e"/>'
        '<path d="M0 300q80-18 160 0t160 0q80-18 160 0v14H0Z" fill="#6cc27a"/>')

def garden_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#a9dcf5"/>'
        '<circle cx="300" cy="110" r="36" fill="#ffe98a"/>'
        '<path d="M0 258q100-54 190 0t150-8q70-46 140 2v108H0Z" fill="#6cc27a"/>'
        '<path d="M0 310q96-32 184 0t158 0q72-28 138 0v50H0Z" fill="#3f9c64"/>'
        '<path d="M30 226q0-26 18-26t18 26Z" fill="#2d7d52"/><path d="M414 234q0-24 17-24t17 24Z" fill="#2d7d52"/>')

def forest_day_backdrop():
    trees = ''.join(
        f'<path d="M{x - 6} 250h12v64H{x - 6}Z" fill="#8a6136"/>'
        f'<circle cx="{x}" cy="212" r="34" fill="#3f9c64"/>'
        f'<circle cx="{x - 26}" cy="232" r="25" fill="#4fae70"/>'
        f'<circle cx="{x + 26}" cy="232" r="25" fill="#4fae70"/>'
        f'<circle cx="{x}" cy="240" r="23" fill="#2d7d52"/>'
        for x in (48, 152, 302, 416))
    return svg(480, 360,
        '<rect width="480" height="360" fill="#a9dcf5"/>'
        + trees +
        '<path d="M0 300q120-28 240 0t240 0v60H0Z" fill="#6cc27a"/>'
        '<path d="M0 330q110-20 230 0t250 0v30H0Z" fill="#3f9c64"/>')


def forest_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#20304a"/>'
        '<circle cx="392" cy="58" r="26" fill="#ffe9a8"/>'
        + ''.join(f'<path d="M{x} 360  {x + 34} {150 + (i % 3) * 24}  {x + 68} 360Z" fill="#142235"/>' for i, x in enumerate(range(-10, 480, 58)))
        + '<path d="M0 310q120-30 240 0t240 0v50H0Z" fill="#0f1c2c"/>')

def range_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#141f3d"/>'
        + ''.join(f'<circle cx="{(i * 67 + 31) % 480}" cy="{(i * 43 + 17) % 190}" r="{1 + (i % 3)}" fill="#ffffff" opacity=".6"/>' for i in range(22))
        + '<path d="M0 296q120-24 240 0t240 0v64H0Z" fill="#1f3a52"/>')

def castle_backdrop():
    return svg(480, 360,
        '<rect width="480" height="360" fill="#6f7fc4"/>'
        '<circle cx="394" cy="64" r="30" fill="#ffe9a8"/>'
        '<path d="M40 60h60v120H40ZM110 40h50v140h-50ZM170 60h60v120h-60Z" fill="#3c477e"/>'
        '<path d="M0 300q120-32 240 0t240 0v60H0Z" fill="#2f3a63"/>'
        '<path d="M44 60h8v10h-8Zm14 0h8v10h-8Zm14 0h8v10h-8Zm14 0h8v10h-8Z" fill="#5a68a8"/>')

def maze_floor_backdrop():
    dots = ''.join(f'<circle cx="{24 + 32 * i}" cy="{24 + 32 * j}" r="2" fill="#2c4a66"/>' for i in range(15) for j in range(11))
    return svg(480, 360, '<rect width="480" height="360" fill="#14283d"/>' + dots)

# ───────────────────────────── Notes ─────────────────────────────

def course_comment(self):
    kind = getattr(self.game, 'kind', 'Игра')
    text = (f'{BRAND} · Курс 2, урок {self.game.lesson}. {self.game.topic}\n'
            f'{kind} «{self.game.title}» — {self.name}\n{self.note}').strip()
    height = max(160, 60 + 21 * (text.count('\n') + 1))
    return {f'{self.game.prefix}note{len(self.game.targets_done)}':
            {'blockId': None, 'x': 40, 'y': 30, 'width': 480, 'height': height, 'minimized': False, 'text': text}}


Target.comment = course_comment


def game(stem, lesson, topic, title):
    g = Game(stem, lesson, topic, title)
    g.prefix = f'c2g{lesson}'
    g.kind = 'Игра'
    return g


def add_badge(g):
    badge = g.sprite(BRAND, [costume(BRAND, badge_svg(), 64, 20)], x=168, y=154, rotation_style="don't rotate",
                     note='Знак лаборатории V Labs. Он всегда остаётся поверх сцены.')
    badge.when(flag(), goto_xy(168, 154), size_to(100), fx_clear(), show(), layer('front'))
    badge.when(clicked(), say_for(f'{BRAND}: курс 2, урок {g.lesson} — «{g.topic}».', 2))
    return badge


def add_walls(g):
    walls = g.sprite('Стены', [costume('Стены', maze_walls_svg(), 240, 180)], x=0, y=0,
                     rotation_style="don't rotate", note='Стены лабиринта. У них нет программы: герой проверяет касание.')
    walls.todo = 'Стены лабиринта не двигаются. Герой проверяет, касается ли он их после каждого шага.'
    return walls


# ───────────────────────────── The eight games ─────────────────────────────

def game_chase():
    g = game('01-chase', 1, 'Догонялки', 'Догонялки')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Время', 30, show=(5, 32))
    stage = g.stage([backdrop('Поляна', meadow_backdrop())],
                    note='Сцена считает время: 30 секунд — и игра заканчивается.')
    stage.todo = ('Что собираем на уроке:\n'
                  '1. Флажок обнуляет очки и ставит таймер на 30 секунд.\n'
                  '2. Каждую секунду «Время» уменьшается на 1.\n'
                  '3. Когда время вышло, сцена говорит счёт и останавливает игру.')
    stage.when(flag(), set_var('Очки', 0), set_var('Время', 30),
               repeat(30, [wait(1), change_var('Время', -1)]),
               say_for(join('Время вышло! Очки: ', var('Очки')), 3), stop('all'))

    fox = g.sprite('Лис', [costume('Лис', fox_svg(), 48, 48)], x=-150, y=-90, size=75,
                   rotation_style='left-right',
                   note='Стрелки — движение. Собирай звёзды: за каждую +1 очко.')
    fox.todo = ('Что собираем на уроке:\n'
                '1. Флажок ставит лиса на старт.\n'
                '2. Стрелки меняют x и y: вправо-влево и вверх-вниз.\n'
                '3. На краю сцены лис отталкивается, чтобы не убежать.')
    fox.when(flag(), show(), goto_xy(-150, -90), size_to(75),
             say_for('Лови звёзды стрелками!', 2))
    fox.when(key('right arrow'), dx(15), bounce())
    fox.when(key('left arrow'), dx(-15), bounce())
    fox.when(key('up arrow'), dy(15), bounce())
    fox.when(key('down arrow'), dy(-15), bounce())

    star = g.sprite('Звезда', [costume('Звезда', star_svg(), 48, 48)], x=120, y=60, size=65,
                    sounds=[note_sound('Поймал', 880, 0.12)],
                    note='Звезда появляется в случайном месте. Касание лиса — очко и новая звезда.')
    star.todo = ('Что собираем на уроке:\n'
                 '1. Флажок показывает звезду в случайном месте.\n'
                 '2. Всегда проверяй, касается ли звезда лиса.\n'
                 '3. Если касается: +1 очко, звук и новое случайное место.')
    star.when(flag(), show(), size_to(65), goto_xy(rnd(-200, 200), rnd(-120, 130)))
    star.when(flag(), forever([if_(touching('Лис'), [change_var('Очки', 1), play('Поймал'),
                                             say_for('Поймал!', 0.5),
                                             goto_xy(rnd(-200, 200), rnd(-120, 130))])]))
    add_badge(g)
    return g


def game_platform():
    g = game('02-platform', 2, 'Платформер', 'Платформер')
    g.variable('Монеты', 0, show=(5, 5))
    g.stage([backdrop('Небо', sky_backdrop())],
            note='Сцена только задаёт фон. Платформы и монеты — отдельные спрайты.')
    stage = g.targets[0]
    stage.todo = 'Сцена задаёт фон. Платформы, монеты и герой — отдельные спрайты: расставь их на сцене.'

    platforms = [(-130, -40), (20, 20), (160, -20)]
    for i, (px, py) in enumerate(platforms, 1):
        p = g.sprite(f'Платформа {i}', [costume('Платформа', platform_svg(), 70, 13)], x=px, y=py,
                     rotation_style="don't rotate",
                     note='Платформа стоит на месте. Герой проверяет касание и приземляется сверху.')
        p.todo = 'Платформа не двигается. Герой проверяет касание платформы и встаёт на неё сверху.'
    ground = g.sprite('Земля', [costume('Земля', svg(480, 50, '<rect width="480" height="50" fill="#4f9a5e"/><path d="M0 0h480v10H0Z" fill="#6cc27a"/>'), 240, 25)],
                      x=0, y=-160, rotation_style="don't rotate",
                      note='Земля — нижняя платформа. С неё герой прыгает.')
    ground.todo = 'Земля не двигается. Герой проверяет касание и не проваливается вниз.'

    hero = g.sprite('Герой', [costume('Герой', fox_svg(), 48, 48)], x=-170, y=-110, size=60,
                    rotation_style='left-right',
                    note='Стрелки влево-вправо — бег, ↑ — прыжок. Переменная «Скорость» — для этого спрайта.')
    hero.todo = ('Что собираем на уроке:\n'
                 '1. Флажок: герой на старте, скорость 0.\n'
                 '2. ← и → двигают героя в сторону.\n'
                 '3. ↑ — прыжок: задай скорости 14 и каждый кадр уменьшай её на 1.\n'
                 '4. Касание платформы или земли — скорость 0 и герой стоит сверху.')
    hero.local('Скорость', 0)
    hero.when(flag(), show(), goto_xy(-170, -110), size_to(60), set_var('Монеты', 0), set_var('Скорость', 0),
              say_for('Собери три монеты!', 2))
    hero.when(key('right arrow'), dx(7))
    hero.when(key('left arrow'), dx(-7))
    hero.when(flag(), forever([
        if_(and_(key_down('up arrow'), or_(touching('Земля'), or_(touching('Платформа 1'),
                                                                or_(touching('Платформа 2'), touching('Платформа 3'))))),
            [set_var('Скорость', 14)]),
        change_var('Скорость', -1), dy(var('Скорость')),
        if_(and_(touching('Земля'), gt(y_pos(), -140)), [set_y(-106), set_var('Скорость', 0)]),
        if_(and_(touching('Платформа 1'), gt(y_pos(), -40)), [set_y(2), set_var('Скорость', 0)]),
        if_(and_(touching('Платформа 2'), gt(y_pos(), 20)), [set_y(62), set_var('Скорость', 0)]),
        if_(and_(touching('Платформа 3'), gt(y_pos(), -20)), [set_y(22), set_var('Скорость', 0)]),
        if_(lt(y_pos(), -170), [goto_xy(-170, -110), set_var('Скорость', 0)]),
    ]))

    for i, (px, py) in enumerate([(-130, -8), (20, 52), (160, 12)], 1):
        coin = g.sprite(f'Монета {i}', [costume('Монета', coin_svg(), 32, 32)], x=px, y=py, size=55,
                        rotation_style="don't rotate",
                        note='Монета исчезает, когда герой её касается.')
        coin.todo = 'Монета висит над платформой. При касании героя она добавляет монету и исчезает.'
        coin.when(flag(), show(), size_to(55))
        coin.when(flag(), forever([if_(touching('Герой'), [change_var('Монеты', 1), hide(), stop('this script')])]))

    stage.when(flag(), forever([if_(eq(var('Монеты'), 3), [say_for('Все монеты! Победа!', 3), stop('all')])]))
    add_badge(g)
    return g


def game_maze():
    g = game('03-maze', 3, 'Лабиринт', 'Лабиринт')
    g.variable('Ключи', 0, show=(5, 5))
    g.variable('Жизни', 3, show=(5, 32))
    g.stage([backdrop('Подземелье', maze_floor_backdrop())], note='Фон подземелья. Стену рисует отдельный спрайт.')
    stage = g.targets[0]
    stage.todo = 'Сцена задаёт фон подземелья. Стены — отдельный спрайт, герой проверяет касание.'
    stage.when(flag(), set_var('Ключи', 0), set_var('Жизни', 3))
    add_walls(g)

    robot = g.sprite('Робот', [costume('Робот', robot_svg(), 48, 48)], x=44, y=46, size=55,
                     rotation_style="don't rotate",
                     note='Стрелки — шаг. Если коснулся стены, шаг назад. Собери три ключа.')
    robot.todo = ('Что собираем на уроке:\n'
                  '1. Флажок ставит робота на старт и обнуляет ключи.\n'
                  '2. Стрелки делают шаг 10: изменить x или y.\n'
                  '3. После шага проверь касание стены. Если коснулся — шаг назад.\n'
                  '4. Собери три ключа и дойди до двери.')
    robot.when(flag(), show(), goto_xy(44, 46), size_to(55), say_for('Найди три ключа и дверь!', 2))
    for key_name, action, back in [('up arrow', dy(10), dy(-10)), ('down arrow', dy(-10), dy(10)),
                                   ('right arrow', dx(10), dx(-10)), ('left arrow', dx(-10), dx(10))]:
        robot.when(key(key_name), action, if_(touching('Стены'), [back]))

    gems = [(-60, 140), (140, 60), (150, -60)]
    for i, (gx, gy) in enumerate(gems, 1):
        gem = g.sprite(f'Ключ {i}', [costume('Ключ', key_svg(), 32, 32)], x=gx, y=gy, size=80,
                       rotation_style="don't rotate",
                       sounds=[note_sound('Поймал', 760 + i * 80, 0.12)],
                       note='Ключ исчезает при касании робота и добавляет 1 к переменной «Ключи».')
        gem.todo = 'Ключ висит в лабиринте. При касании робота: +1 ключ, звук и ключ исчезает.'
        gem.when(flag(), show(), size_to(80))
        gem.when(flag(), forever([if_(touching('Робот'), [change_var('Ключи', 1), play('Поймал'), hide(),
                                                   stop('this script')])]))

    door = g.sprite('Дверь', [costume('Дверь', door_svg(), 48, 64)], x=200, y=-135, size=65,
                    rotation_style="don't rotate",
                    note='Дверь открыта, когда собраны три ключа.')
    door.todo = 'Дверь стоит в дальнем углу. Она открывается, когда ключей три, и завершает игру.'
    door.when(flag(), show(), size_to(65), goto_xy(200, -135))
    door.when(flag(), forever([if_(and_(eq(var('Ключи'), 3), touching('Робот')),
                           [say_for('Победа! Все ключи собраны.', 3), stop('all')])]))
    add_badge(g)
    return g


def game_catcher():
    g = game('04-catcher', 4, 'Ловец', 'Ловец')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Жизни', 3, show=(5, 32))
    g.variable('Время', 30, show=(5, 59))
    stage = g.stage([backdrop('Сад', garden_backdrop())], note='Сцена ведёт время: 30 секунд на игру.')
    stage.todo = ('Что собираем на уроке:\n'
                  '1. Флажок обнуляет очки, ставит три жизни и 30 секунд.\n'
                  '2. Каждую секунду время уменьшается на 1.\n'
                  '3. Когда время вышло, сцена говорит счёт и останавливает игру.')
    stage.when(flag(), set_var('Очки', 0), set_var('Жизни', 3), set_var('Время', 30),
               repeat(30, [wait(1), change_var('Время', -1)]),
               say_for(join('Время! Твой счёт: ', var('Очки')), 3), stop('all'))

    basket = g.sprite('Корзина', [costume('Корзина', basket_svg(), 48, 48)], x=0, y=-140, size=70,
                      rotation_style="don't rotate",
                      note='Стрелки влево-вправо двигают корзину. Яблоко — очко, бомба — жизнь.')
    basket.todo = ('Что собираем на уроке:\n'
                   '1. Флажок ставит корзину внизу по центру.\n'
                   '2. Стрелки двигают корзину влево и вправо, но не выпускают за край.\n'
                   '3. Лови яблоки и не трогай бомбы.')
    basket.when(flag(), show(), goto_xy(0, -140), size_to(70), say_for('Лови яблоки!', 2))
    basket.when(key('right arrow'), set_x(add(x_pos(), 18)), if_(gt(x_pos(), 205), [set_x(205)]))
    basket.when(key('left arrow'), set_x(sub(x_pos(), 18)), if_(lt(x_pos(), -205), [set_x(-205)]))

    def falling(name, art, good):
        s = g.sprite(name, [costume(name, art, 32, 32)], x=0, y=180, size=60, visible=False,
                     rotation_style="don't rotate",
                     sounds=[note_sound('Поймал', 660 if good else 180, 0.12)],
                     note=('Яблоко падает сверху. Касание корзины — +1 очко.' if good
                           else 'Бомба падает сверху. Касание корзины — минус одна жизнь.'))
        s.todo = (('Яблоко — клон: появляется сверху в случайном месте и падает вниз.\n'
                   'Касание корзины: +1 очко, звук, клон удаляется.') if good else
                  ('Бомба — клон: появляется сверху и падает вниз.\n'
                   'Касание корзины: −1 жизнь, звук, клон удаляется. При 0 жизнях игра кончается.'))
        s.start = {'visible': True}
        s.when(flag(), hide())
        s.when(flag(), forever([wait(0.9 if good else 1.3), clone('_myself_')]))
        body = [goto_xy(rnd(-210, 210), 180), show(), size_to(60),
                repeat_until(or_(lt(y_pos(), -165), touching('Корзина')), [dy(-7)]),
                if_(touching('Корзина'), [change_var('Очки', 1), play('Поймал')] if good else
                    [change_var('Жизни', -1), play('Поймал'),
                     if_(lt(var('Жизни'), 1), [say_for('Игра окончена!', 3), stop('all')])]),
                delete_clone()]
        s.when(as_clone(), *body)
        return s

    falling('Яблоко', apple_svg(), True)
    falling('Бомба', bomb_svg(), False)
    add_badge(g)
    return g


def game_pursuit():
    g = game('05-pursuit', 5, 'Погоня', 'Погоня')
    g.variable('Ключи', 0, show=(5, 5))
    g.variable('Жизни', 3, show=(5, 32))
    stage = g.stage([backdrop('Тёмный лес', forest_backdrop())], note='Сцена проверяет, собраны ли все ключи.')
    stage.todo = 'Сцена проверяет, собраны ли все ключи. Когда ключей три — игра выиграна.'
    stage.when(flag(), set_var('Ключи', 0), set_var('Жизни', 3))
    stage.when(flag(), forever([if_(eq(var('Ключи'), 3), [say_for('Все ключи! Выход найден!', 3), stop('all')])]))

    hero = g.sprite('Лис', [costume('Лис', fox_svg(), 48, 48)], x=-170, y=-120, size=65,
                    rotation_style='left-right',
                    note='Стрелки — движение. Собирай ключи и не дай тени себя поймать.')
    hero.todo = ('Что собираем на уроке:\n'
                 '1. Флажок ставит лиса на старт и обнуляет ключи.\n'
                 '2. Стрелки двигают лиса, на краю он отталкивается.\n'
                 '3. Собери три ключа, убегая от тени.')
    hero.when(flag(), show(), goto_xy(-170, -120), size_to(65), say_for('Собери три ключа!', 2))
    hero.when(key('right arrow'), dx(14), bounce())
    hero.when(key('left arrow'), dx(-14), bounce())
    hero.when(key('up arrow'), dy(14), bounce())
    hero.when(key('down arrow'), dy(-14), bounce())

    shadow = g.sprite('Тень', [costume('Тень', shadow_svg(), 48, 48)], x=180, y=120, size=80,
                      note='Тень всё время идёт к лису, но медленно. Касание — минус жизнь.')
    shadow.todo = ('Что собираем на уроке:\n'
                   '1. Тень появляется в углу сцены.\n'
                   '2. Всегда: повернуться к лису и сделать 2 шага.\n'
                   '3. Касание лиса: −1 жизнь и тень возвращается в угол.\n'
                   '4. Когда жизни кончились — «Поймали!» и остановка игры.')
    shadow.when(flag(), show(), goto_xy(180, 120), size_to(80))
    shadow.when(flag(), forever([point_to('Лис'), move(2),
                         if_(touching('Лис'), [change_var('Жизни', -1),
                                               say_for('Поймал!', 1), goto_xy(180, 120),
                                               if_(lt(var('Жизни'), 1), [say_for('Тень поймала лиса!', 3), stop('all')])])]))

    for i, (kx, ky) in enumerate([(-180, 110), (0, -20), (180, -130)], 1):
        key_s = g.sprite(f'Ключ {i}', [costume('Ключ', key_svg(), 32, 32)], x=kx, y=ky, size=55,
                         rotation_style="don't rotate",
                         sounds=[note_sound('Поймал', 760 + i * 80, 0.12)],
                         note='Ключ исчезает при касании лиса и добавляет 1 к переменной «Ключи».')
        key_s.todo = 'Ключ висит на поляне. При касании лиса: +1 ключ, звук и ключ исчезает.'
        key_s.when(flag(), show(), size_to(55))
        key_s.when(flag(), forever([if_(touching('Лис'), [change_var('Ключи', 1), play('Поймал'), hide(),
                                                  stop('this script')])]))
    add_badge(g)
    return g


def game_shooter():
    g = game('06-shooter', 6, 'Тир', 'Тир')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Время', 30, show=(5, 32))
    stage = g.stage([backdrop('Ночной тир', range_backdrop())], note='Сцена ведёт время: 30 секунд на стрельбу.')
    stage.todo = ('Что собираем на уроке:\n'
                  '1. Флажок обнуляет очки и запускает таймер на 30 секунд.\n'
                  '2. Каждую секунду время уменьшается на 1.\n'
                  '3. В конце сцена говорит счёт и останавливает игру.')
    stage.when(flag(), set_var('Очки', 0), set_var('Время', 30),
               repeat(30, [wait(1), change_var('Время', -1)]),
               say_for(join('Время! Попаданий: ', var('Очки')), 3), stop('all'))

    cannon = g.sprite('Пушка', [costume('Пушка', cannon_svg(), 48, 48)], x=0, y=-140, size=70,
                      rotation_style="don't rotate",
                      note='Пушка едет за мышкой. Пробел — выстрел пулей-клоном.')
    cannon.todo = ('Что собираем на уроке:\n'
                   '1. Флажок ставит пушку внизу.\n'
                   '2. Всегда: пушка ставит x равным x мышки.\n'
                   '3. Пробел создаёт клон пули.')
    cannon.when(flag(), show(), goto_xy(0, -140), size_to(70), say_for('Пробел — выстрел!', 2))
    cannon.when(flag(), forever([set_x(mouse_x()), if_(gt(x_pos(), 210), [set_x(210)]), if_(lt(x_pos(), -210), [set_x(-210)])]))

    bullet = g.sprite('Пуля', [costume('Пуля', bullet_svg(), 12, 12)], x=0, y=-120, size=100, visible=False,
                      rotation_style="don't rotate",
                      sounds=[note_sound('Попадание', 980, 0.1)],
                      note='Пуля — клон: летит вверх и удаляется при попадании.')
    bullet.todo = ('Что собираем на уроке:\n'
                   '1. Пробел создаёт клон пули.\n'
                   '2. Клон встаёт над пушкой и летит вверх.\n'
                   '3. Касание мишени: +1 очко и клон удаляется.')
    bullet.start = {'visible': True}
    bullet.when(flag(), hide())
    bullet.when(key('space'), clone('_myself_'))
    bullet.when(as_clone(), goto_xy(prop_of('x position', 'Пушка'), -125), show(),
                repeat_until(or_(gt(y_pos(), 175), touching('Мишень')), [dy(14)]),
                if_(touching('Мишень'), [change_var('Очки', 1), play('Попадание')]), delete_clone())

    target = g.sprite('Мишень', [costume('Мишень', target_svg(), 40, 40)], x=0, y=140, size=65, visible=False,
                      rotation_style="don't rotate",
                      note='Мишень — клон: летит по небу слева направо. Попадание приносит очко.')
    target.todo = ('Что собираем на уроке:\n'
                   '1. Всегда ждать и создавать клон мишени.\n'
                   '2. Клон появляется сверху в случайном месте и летит в сторону.\n'
                   '3. Долетев до края, клон удаляется.')
    target.start = {'visible': True}
    target.when(flag(), hide())
    target.when(flag(), forever([wait(0.9), clone('_myself_')]))
    target.when(as_clone(), goto_xy(rnd(-210, 215), rnd(100, 150)), show(), size_to(65),
                repeat_until(lt(x_pos(), -235), [dx(-6)]), delete_clone())
    add_badge(g)
    return g


def game_quest():
    g = game('07-quest', 7, 'Приключение', 'Приключение')
    g.variable('Найдено', 0, show=(5, 5))
    g.variable('Уровень', 1, show=(5, 32))
    stage = g.stage([backdrop('Лес', forest_day_backdrop()), backdrop('Замок', castle_backdrop())],
                    note='Два фона: «Лес» и «Замок». Смена фона — новый уровень.')
    stage.todo = 'У сцены два фона. Пока герой не собрал три предмета, стоит «Лес», потом — «Замок».'
    stage.when(flag(), set_var('Найдено', 0), set_var('Уровень', 1), set_backdrop('Лес'))

    hero = g.sprite('Герой', [costume('Герой', fox_svg(), 48, 48)], x=-180, y=-120, size=60,
                    rotation_style='left-right',
                    note='Стрелки — движение. Собери три предмета, потом найди дверь в замке.')
    hero.todo = ('Что собираем на уроке:\n'
                 '1. Флажок ставит героя в лес и обнуляет находки.\n'
                 '2. Стрелки двигают героя.\n'
                 '3. Собери три предмета — начнётся второй уровень.\n'
                 '4. Во втором уровне герой ищет дверь.')
    hero.when(flag(), show(), goto_xy(-180, -120), size_to(60), say_for('Собери три предмета!', 2))
    hero.when(key('right arrow'), dx(12), bounce())
    hero.when(key('left arrow'), dx(-12), bounce())
    hero.when(key('up arrow'), dy(12), bounce())
    hero.when(key('down arrow'), dy(-12), bounce())
    hero.when(receive('Уровень 2'), goto_xy(-180, -120), say_for('Замок открыт! Найди дверь.', 2))

    for i, (gx, gy) in enumerate([(-120, 30), (0, 130), (120, 60)], 1):
        item = g.sprite(f'Предмет {i}', [costume('Предмет', sprite_svg('gem'), 48, 48)], x=gx, y=gy, size=75,
                        rotation_style="don't rotate",
                        sounds=[note_sound('Поймал', 700 + i * 90, 0.12)],
                        note='Предмет исчезает при касании героя. Три предмета открывают замок.')
        item.todo = ('Предмет висит в лесу. При касании героя: +1 находка, звук и предмет исчезает.\n'
                     'Когда найдено три, сцена меняет фон на «Замок» и сообщает «Уровень 2».')
        item.when(flag(), show(), size_to(75))
        item.when(flag(), forever([if_(touching('Герой'), [change_var('Найдено', 1), play('Поймал'), hide(),
                                                    if_(eq(var('Найдено'), 3),
                                                        [set_var('Уровень', 2), set_backdrop('Замок'),
                                                         broadcast('Уровень 2')]),
                                                    stop('this script')])]))

    door = g.sprite('Дверь', [costume('Дверь', door_svg(), 48, 64)], x=200, y=-110, size=95, visible=False,
                    rotation_style="don't rotate", note='Дверь появляется во втором уровне. Касание — победа.')
    door.todo = 'Дверь появляется в замке после сообщения «Уровень 2». Касание героя завершает игру.'
    door.start = {'visible': True}
    door.when(flag(), hide())
    door.when(receive('Уровень 2'), show(), goto_xy(200, -110),
              forever([if_(touching('Герой'), [say_for('Победа! Ты прошёл приключение.', 3), stop('all')])]))
    add_badge(g)
    return g


def game_own():
    g = game('08-own-game', 8, 'Своя игра', 'Своя игра')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Жизни', 3, show=(5, 32))
    stage = g.stage([backdrop('Арена', meadow_backdrop())], note='Сцена проверяет победу: пять звёзд — и игра пройдена.')
    stage.todo = ('Что собираем на уроке:\n'
                  '1. Сцена проверяет, собраны ли пять звёзд.\n'
                  '2. Когда звёзд пять — «Победа!» и остановка игры.')
    stage.when(flag(), set_var('Очки', 0), set_var('Жизни', 3))
    stage.when(flag(), forever([if_(eq(var('Очки'), 5), [say_for('Победа! Игра собрана.', 3), stop('all')])]))

    hero = g.sprite('Герой', [costume('Герой', fox_svg(), 48, 48)], x=-150, y=-100, size=60,
                    rotation_style='left-right',
                    note='В начале — имя и выбор скорости. 1 — спокойно, 2 — быстро. Стрелки — движение.')
    hero.todo = ('Что собираем на уроке:\n'
                 '1. Флажок спрашивает имя и говорит приветствие.\n'
                 '2. Ждёт клавишу 1 или 2 и выбирает скорость.\n'
                 '3. Стрелки двигают героя с выбранной скоростью.\n'
                 '4. Собери пять звёзд и убеги от тени.')
    hero.local('Скорость', 8)
    hero.when(flag(), show(), goto_xy(-150, -100), size_to(60), set_var('Скорость', 8),
              ask('Как тебя зовут?'),
              say_for(join('Привет, ', answer(), '! 1 — спокойно, 2 — быстро.'), 2),
              wait_until(or_(key_down('1'), key_down('2'))),
              if_else(key_down('2'), [set_var('Скорость', 14), say_for('Быстрый режим!', 1)],
                      [set_var('Скорость', 8), say_for('Спокойный режим.', 1)]),
              say_for('Собирай звёзды и убегай от тени!', 2))
    hero.when(key('right arrow'), dx(var('Скорость')), bounce())
    hero.when(key('left arrow'), dx(sub(0, var('Скорость'))), bounce())
    hero.when(key('up arrow'), dy(var('Скорость')), bounce())
    hero.when(key('down arrow'), dy(sub(0, var('Скорость'))), bounce())

    shadow = g.sprite('Тень', [costume('Тень', shadow_svg(), 48, 48)], x=150, y=80, size=75,
                      note='Тень идёт к герою. Касание — минус жизнь.')
    shadow.todo = ('Что собираем на уроке:\n'
                   '1. Тень появляется в углу.\n'
                   '2. Всегда идёт к герою.\n'
                   '3. Касание: −1 жизнь и возврат в угол. При 0 жизнях — конец игры.')
    shadow.when(flag(), show(), goto_xy(150, 80), size_to(75))
    shadow.when(flag(), forever([point_to('Герой'), move(2),
                         if_(touching('Герой'), [change_var('Жизни', -1), say_for('Поймал!', 1),
                                                 goto_xy(150, 80),
                                                 if_(lt(var('Жизни'), 1), [say_for('Игра окончена.', 3), stop('all')])])]))

    for i, (sx, sy) in enumerate([(-170, 120), (0, 60), (180, -120), (-60, -140), (60, -40)], 1):
        star = g.sprite(f'Звезда {i}', [costume('Звезда', star_svg(), 48, 48)], x=sx, y=sy, size=55,
                        rotation_style="don't rotate", sounds=[note_sound('Поймал', 820 + i * 50, 0.12)],
                        note='Звезда исчезает при касании героя и добавляет очко.')
        star.todo = 'Звезда висит на арене. При касании героя: +1 очко, звук и звезда исчезает.'
        star.when(flag(), show(), size_to(55))
        star.when(flag(), forever([if_(touching('Герой'), [change_var('Очки', 1), play('Поймал'), hide(),
                                                    stop('this script')])]))
    add_badge(g)
    return g


GAMES2 = [game_chase, game_platform, game_maze, game_catcher, game_pursuit, game_shooter, game_quest, game_own]


def starter(source):
    """The starter keeps the artwork but loses the program, variables and messages."""
    source.kind = 'Заготовка'
    source.variables, source.lists = {}, {}
    for target in source.targets:
        target.scripts, target.locals = [], {}
        target.note = getattr(target, 'todo', target.note)
        for name, value in getattr(target, 'start', {}).items():
            setattr(target, name, value)
    return source


def assets_of(project):
    return sorted((t['name'], a['name'], a['md5ext']) for t in project['targets'] for a in t['costumes'] + t['sounds'])


def main():
    check = '--check' in sys.argv[1:]
    GAME_OUT.mkdir(parents=True, exist_ok=True)
    START_OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for make in GAMES2:
        demo = make()
        done, done_assets = demo.project()
        started = starter(make()).project()
        start, start_assets = started
        if assets_of(start) != assets_of(done):
            sys.exit(f'{demo.stem}: the starter and the game have different artwork or sounds')
        if any(t['blocks'] or t['variables'] or t['lists'] or t['broadcasts'] for t in start['targets']):
            sys.exit(f'{demo.stem}: the starter must not contain blocks, variables, lists or messages')
        blocks = sum(len(t['blocks']) for t in done['targets'])
        if blocks < 40:
            sys.exit(f'{demo.stem}: the game has only {blocks} blocks')
        for kind, project, assets, out in (('game', done, done_assets, GAME_OUT),
                                           ('start', start, start_assets, START_OUT)):
            data = package(project, assets)
            path = out / f'{demo.stem}{"-start" if kind == "start" else ""}.sb3'
            if check:
                if not path.exists() or contents(path.read_bytes()) != contents(data):
                    stale.append(str(path.relative_to(ROOT)))
            else:
                path.write_bytes(data)
            counts = demo.stats(project)
            summary = ', '.join(f'{CATEGORY_NAMES[c]} {n}' for c, n in sorted(counts.items(), key=lambda kv: -kv[1]))
            print(f'{path.relative_to(ROOT)}: {len(data):,} bytes, {sum(counts.values())} blocks'
                  + (f' ({summary})' if summary else ''))
    if stale:
        sys.exit('Out of date, run python3 scripts/build-course2.py: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
