#!/usr/bin/env python3
"""Build the practice projects of the eight lessons: a starter and a solution for each.

    lessons/practice/NN-topic-start.sb3     «заготовка»: sprites, backdrops and sounds, no program;
                                             the note in the code area lists the steps of the practice.
    lessons/practice/NN-topic-solution.sb3  «разгадка»: the finished practice project.

A starter is made from its solution by removing the program, so both always share the same artwork.
The block builder, artwork and sounds come from build-games.py.

Run:    python3 scripts/build-practice.py
Check:  python3 scripts/build-practice.py --check   (writes nothing, exit code 1 when files are out of date)
"""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location('build_games', ROOT / 'scripts' / 'build-games.py')
games = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(games)
globals().update({name: value for name, value in vars(games).items() if not name.startswith('__')})
OUT = ROOT / 'lessons' / 'practice'      # after the import: build-games.py has its own OUT


# ───────────────────────────── Notes in the code area ─────────────────────────────

def practice_comment(self):
    """The note of a practice project says what the file is: «Заготовка» or «Разгадка»."""
    game = self.game
    text = f'{BRAND} · Урок {game.lesson}. {game.topic}\n{game.kind} «{game.title}» — {self.name}\n{self.note}'.strip()
    height = max(160, 60 + 21 * (text.count('\n') + 1))
    return {f'{game.prefix}note{len(game.targets_done)}':
            {'blockId': None, 'x': 40, 'y': 30, 'width': 480, 'height': height, 'minimized': False, 'text': text}}


games.Target.comment = practice_comment


# ───────────────────────────── Artwork of the practice ─────────────────────────────
# Same rules as in build-games.py: basic SVG shapes only, no text, filters, gradients or rx.

# The bug is drawn facing right, so «point in direction 90» sends it head-first.
BUG = svg(96, 96,
    '<path d="M70 30 84 16M70 66 84 80" fill="none" stroke="#1d2b3a" stroke-width="4" stroke-linecap="round"/>'
    '<circle cx="78" cy="48" r="14" fill="#1d2b3a"/><circle cx="44" cy="48" r="34" fill="#e8483f"/>'
    '<path d="M10 48H76" fill="none" stroke="#1d2b3a" stroke-width="3"/>'
    '<circle cx="30" cy="30" r="6" fill="#1d2b3a"/><circle cx="54" cy="28" r="5" fill="#1d2b3a"/>'
    '<circle cx="30" cy="66" r="6" fill="#1d2b3a"/><circle cx="54" cy="68" r="5" fill="#1d2b3a"/>'
    '<circle cx="84" cy="42" r="3" fill="#ffffff"/><circle cx="84" cy="54" r="3" fill="#ffffff"/>')

# Walls of the maze, in stage pixels (x, y, width, height), y grows downwards.
# The bug walks in steps of 10 from (44, 46), so every wall edge lies 5 px off its path: a clear «touching» or «free».
MAZE_WALLS = [
    (0, 0, 480, 11), (0, 351, 480, 9), (0, 0, 9, 360), (469, 0, 11, 360),      # border
    (329, 0, 151, 61),                                                         # block under the «V Labs» badge
    (0, 81, 239, 10), (319, 61, 10, 120), (79, 171, 250, 10),
    (0, 261, 159, 10), (239, 261, 241, 10),
]
MAZE = svg(480, 360, ''.join(f'<path d="M{x} {y}h{w}v{h}h{-w}Z" fill="#59e0c8"/>' for x, y, w, h in MAZE_WALLS))
MAZE_FLOOR = svg(480, 360,
    '<rect width="480" height="360" fill="#14283d"/>'
    + ''.join(f'<circle cx="{44 + 40 * i}" cy="{46 + 45 * j}" r="2" fill="#2c4a66"/>'
              for i in range(11) for j in range(7)))


def robot_svg(singing):
    mouth = ('<path d="M36 62q12 16 24 0Z" fill="#1d2b3a"/><path d="M41 63h14v3H41Z" fill="#ffffff"/>' if singing
             else '<path d="M37 64h22" fill="none" stroke="#1d2b3a" stroke-width="4" stroke-linecap="round"/>')
    return svg(96, 96,
        '<path d="M48 20V9" fill="none" stroke="#c9d7e2" stroke-width="4" stroke-linecap="round"/>'
        '<circle cx="48" cy="8" r="5" fill="#ff8b60"/>'
        '<path d="M9 40h7v18H9ZM80 40h7v18h-7Z" fill="#6aa9c4"/>'
        '<path d="M24 20h48q8 0 8 8v46q0 8-8 8H24q-8 0-8-8V28q0-8 8-8Z" fill="#8fd6e8" stroke="#e6f8ff" stroke-width="3"/>'
        '<circle cx="35" cy="43" r="8" fill="#ffffff"/><circle cx="61" cy="43" r="8" fill="#ffffff"/>'
        '<circle cx="36" cy="44" r="4" fill="#1d2b3a"/><circle cx="60" cy="44" r="4" fill="#1d2b3a"/>'
        f'{mouth}<circle cx="24" cy="74" r="2" fill="#6aa9c4"/><circle cx="72" cy="74" r="2" fill="#6aa9c4"/>')


BASKET = svg(96, 96,
    '<path d="M24 46a24 26 0 0 1 48 0" fill="none" stroke="#b9773a" stroke-width="6" stroke-linecap="round"/>'
    '<circle cx="36" cy="40" r="11" fill="#ff6d78"/><circle cx="58" cy="38" r="12" fill="#ffd45e"/>'
    '<path d="M36 29q2-6 7-7" fill="none" stroke="#3f8f4f" stroke-width="3" stroke-linecap="round"/>'
    '<path d="M12 44h72l-9 40H21Z" fill="#e2a55a" stroke="#fff0d2" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M16 57h64M19 70h58M34 44l3 40M48 44v40M62 44l-3 40" fill="none" stroke="#b9773a" stroke-width="3"/>')


def practice(stem, lesson, topic, title):
    game = Game(stem, lesson, topic, title)
    game.prefix = f'p{lesson}'
    game.kind = 'Разгадка'
    return game


def add_mark(game):
    """The «V Labs» badge of a practice project has no program: only blocks made at the lesson are inside."""
    mark = game.sprite(BRAND, [costume(BRAND, badge_svg(), 64, 20)], x=168, y=154, rotation_style="don't rotate",
                       note='Знак лаборатории V Labs. Программа ему не нужна.')
    mark.todo = mark.note
    return mark


# ───────────────────────────── The eight practice projects ─────────────────────────────
# Every function builds the solution. Target.todo is the note shown in the starter instead of the program,
# Target.start overrides the look of a sprite in the starter (a hidden sprite could not be found by a child).

def practice_events():
    g = practice('01-events', 1, 'События', 'Солнце и дождь')
    stage = g.stage([backdrop('Солнечно', events_backdrop('sunny')), backdrop('Дождливо', events_backdrop('rainy')),
                     backdrop('Радуга', events_backdrop('rainbow'))],
                    note='Сцена слушает сообщения и меняет фон.')
    stage.todo = ('У сцены три фона: «Солнечно», «Дождливо» и «Радуга».\n'
                  'Сцена должна менять фон, когда получит сообщение «Дождь» или «Радуга».')
    stage.when(flag(), set_backdrop('Солнечно'))
    stage.when(receive('Дождь'), set_backdrop('Дождливо'))
    stage.when(receive('Радуга'), set_backdrop('Радуга'))

    sun = g.sprite('Солнце', [costume('Солнце', sprite_svg('sun'))], x=-158, y=60,
                   note='Флажок — солнце выходит. Пробел — солнце отправляет сообщение «Радуга».')
    sun.todo = ('Что собираем на уроке:\n'
                '1. Флажок — солнце выходит и здоровается.\n'
                '2. Клик по облаку — идёт дождь: облако отправляет сообщение «Дождь».\n'
                '3. Пробел — появляется радуга: солнце отправляет сообщение «Радуга».\n'
                'Начни с солнца: какое событие запускает его программу?')
    sun.when(flag(), show(), goto_xy(-158, 60), say_for('Доброе утро!', 2))
    sun.when(key('space'), broadcast('Радуга'))
    sun.when(receive('Дождь'), hide())
    sun.when(receive('Радуга'), show(), say_for('После дождя бывает радуга!', 2))

    cloud = g.sprite('Облако', [costume('Облачко', CLOUD, 60, 45)], x=135, y=58, rotation_style="don't rotate",
                     note='Клик по облаку — сообщение «Дождь». Его слышат сцена, солнце и капля.')
    cloud.todo = 'Клик по облаку — событие. Облако должно отправить сообщение «Дождь».'
    cloud.when(clicked(), broadcast('Дождь'), say_for('Кап-кап!', 2))

    drop = g.sprite('Капля', [costume('Капля', DROP, 24, 28)], x=135, y=10, size=60, visible=False,
                    rotation_style="don't rotate",
                    note='Капля ждёт сообщение «Дождь» и падает из облака.')
    drop.todo = 'Капля падает, когда получает сообщение «Дождь». До дождя она спрятана.'
    drop.start = {'visible': True}
    drop.when(flag(), hide())
    drop.when(receive('Дождь'), repeat(3, [goto_xy(135, 10), show(), repeat(10, [dy(-14)]), hide()]))
    drop.when(receive('Радуга'), hide())
    add_mark(g)
    return g


def practice_motion():
    g = practice('02-motion', 2, 'Движение', 'Лабиринт')
    stage = g.stage([backdrop('Поле', MAZE_FLOOR)], note='Поле лабиринта. Программа сцене не нужна.')
    stage.todo = stage.note
    walls = g.sprite('Стены', [costume('Стены', MAZE, 240, 180)], x=0, y=0, rotation_style="don't rotate",
                     note='Стены стоят на месте. Жук проверяет, не коснулся ли он их.')
    walls.todo = 'Стены стоят на месте, программа им не нужна. Не двигай их: дорога к кристаллу уже есть.'
    bug = g.sprite('Жук', [costume('Жук', BUG)], x=-196, y=134, size=30,
                   note='Стрелки поворачивают жука и ведут его на 10 шагов.\n'
                        'Если жук коснулся стены, он делает 10 шагов назад.')
    bug.todo = ('Что собираем на уроке:\n'
                '1. Флажок — жук встаёт на старт: x = -196, y = 134.\n'
                '2. Стрелки — жук поворачивается в нужную сторону и идёт на 10 шагов.\n'
                '3. Коснулся стены — отходит на 10 шагов назад.\n'
                '4. Дошёл до кристалла — говорит «Победа!».\n'
                'Подсказка: вправо — направление 90, влево — -90, вверх — 0, вниз — 180.')
    bug.when(flag(), goto_xy(-196, 134), point(90), wait_until(touching('Финиш')), say_for('Победа!', 3))
    for name, angle in [('right arrow', 90), ('left arrow', -90), ('up arrow', 0), ('down arrow', 180)]:
        bug.when(key(name), point(angle), move(10), if_(touching('Стены'), [move(-10)]))
    finish = g.sprite('Финиш', [costume('Кристалл', sprite_svg('gem'))], x=194, y=-136, size=40,
                      rotation_style="don't rotate",
                      note='Кристалл ждёт жука в конце лабиринта.')
    finish.todo = 'Кристалл — это финиш. Программа ему не нужна.'
    add_mark(g)
    return g


def practice_looks():
    g = practice('03-looks', 3, 'Внешность', 'История с персонажем')
    stage = g.stage([backdrop('Поляна', events_backdrop('sunny')), backdrop('Радуга', events_backdrop('rainbow'))],
                    note='Фон меняет Кубик: в конце истории появляется радуга.')
    stage.todo = 'У сцены два фона: «Поляна» и «Радуга». Сменить фон может любой герой.'
    cube = g.sprite('Кубик', [costume(name, mood_svg(name)) for name in ('Радость', 'Грусть', 'Удивление')],
                    x=-110, y=-60, size=110, rotation_style="don't rotate",
                    note='Кубик рассказывает историю и меняет костюмы: радость, грусть, удивление.\n'
                         'Сообщение «Выходи» зовёт Звёздочку. Кубик ждёт, пока она ответит.')
    cube.todo = ('Что собираем на уроке:\n'
                 '1. Кубик рассказывает историю блоками «говорить … секунд».\n'
                 '2. По ходу истории он меняет костюмы: «Радость», «Грусть», «Удивление».\n'
                 '3. Звёздочка сначала спрятана, а потом появляется.\n'
                 'Придумай свою историю или возьми нашу: Кубик и Звёздочка играют в прятки.')
    cube.when(flag(), set_backdrop('Поляна'), set_costume('Радость'), size_to(110),
              say_for('Привет! Я Кубик.', 2),
              say_for('Мы со Звёздочкой играем в прятки.', 3),
              set_costume('Грусть'),
              say_for('Ищу, ищу… Нигде её нет.', 3),
              broadcast_wait('Выходи'),
              set_costume('Удивление'), size_by(20),
              say_for('Вот это да! Ты была совсем рядом!', 3),
              set_costume('Радость'), size_by(-20), set_backdrop('Радуга'),
              say_for('Ура, мы снова вместе!', 2))
    star = g.sprite('Звёздочка', [costume('Звёздочка', sprite_svg('tracker'))], x=30, y=-75, size=90, visible=False,
                    rotation_style="don't rotate",
                    note='Звёздочка спрятана, пока не получит сообщение «Выходи».')
    star.todo = 'Звёздочка — второй герой. В начале истории она прячется, потом появляется.'
    star.start = {'visible': True}
    star.when(flag(), hide())
    star.when(receive('Выходи'), show(), say_for('Я здесь!', 2))
    add_mark(g)
    return g


def practice_sound():
    g = practice('04-sound', 4, 'Звук', 'Мелодия на клавишах')
    stage = g.stage([backdrop('Сцена', scene_svg(['#2a1f4d', '#7a4fb0'], SCENES['sound']))],
                    note='Сцена для концерта. Программа ей не нужна.')
    stage.todo = stage.note
    notes = [note_sound(name, freq) for name, freq in NOTES[:5]]
    robot = g.sprite('Робот', [costume('Молчит', robot_svg(False)), costume('Поёт', robot_svg(True))], sounds=notes,
                     x=0, y=-100, size=130, rotation_style="don't rotate",
                     note='Клавиши 1–5 — ноты, ↑ ↓ — громкость, пробел — песенка «Братец Яков».\n'
                          '«Играть звук до конца» ждёт, пока нота допоёт, и только потом закрывает рот.')
    robot.todo = ('Что собираем на уроке:\n'
                  '1. Клавиши 1, 2, 3, 4, 5 — робот поёт ноты: До, Ре, Ми, Фа, Соль.\n'
                  '2. Пока нота звучит, у робота костюм «Поёт», потом снова «Молчит».\n'
                  '3. Стрелки вверх и вниз меняют громкость.\n'
                  '4. Пробел — робот сам поёт песенку.\n'
                  'Звуки уже лежат на вкладке «Звуки» у робота.')
    robot.when(flag(), vol_to(100), set_costume('Молчит'), say_for('Клавиши 1–5 — ноты, пробел — песенка.', 3))
    for number, (name, _) in enumerate(NOTES[:5], 1):
        robot.when(key(str(number)), set_costume('Поёт'), play_wait(name), set_costume('Молчит'))
    robot.when(key('up arrow'), vol_by(10))
    robot.when(key('down arrow'), vol_by(-10))
    robot.when(key('space'), set_costume('Поёт'),
               repeat(2, [play_wait('До'), play_wait('Ре'), play_wait('Ми'), play_wait('До')]),
               repeat(2, [play_wait('Ми'), play_wait('Фа'), play_wait('Соль'), wait(0.4)]),
               set_costume('Молчит'))
    add_mark(g)
    return g


def practice_control():
    g = practice('05-control', 5, 'Управление', 'Салют из клонов')
    stage = g.stage([backdrop('Ночное небо', scene_svg(['#0d1838', '#2b2f77'], ''))],
                    note='Ночное небо. Программа сцене не нужна.')
    stage.todo = stage.note
    spark = g.sprite('Искра', [costume('Искра', STAR, 32, 32)], x=0, y=-120, size=70, visible=False,
                     rotation_style="don't rotate",
                     note='Сама искра спрятана и всё время создаёт клоны.\n'
                          'Каждый клон летит вверх, а выше y = 60 вспыхивает и удаляется.')
    spark.todo = ('Что собираем на уроке:\n'
                  '1. Флажок — искра прячется и всегда создаёт клон самой себя, потом ждёт 0.3 секунды.\n'
                  '2. Клон появляется внизу в случайном месте и показывается.\n'
                  '3. Клон всегда летит вверх: «изменить y на 8».\n'
                  '4. Если клон поднялся выше y = 60 — он вспыхивает и удаляется.\n'
                  'Понадобятся блоки «навсегда», «если … то» и блоки клонов.')
    spark.start = {'visible': True}
    spark.when(flag(), hide(), forever([clone('_myself_'), wait(0.3)]))
    spark.when(as_clone(), goto_xy(rnd(-200, 200), -140), size_to(70), fx_to('COLOR', rnd(0, 200)), show(),
               forever([dy(8),
                        if_(gt(y_pos(), 60), [repeat(8, [size_by(12), fx_by('GHOST', 12)]), delete_clone()])]))
    add_mark(g)
    return g


def practice_sensing():
    g = practice('06-sensing', 6, 'Сенсоры', 'Викторина')
    stage = g.stage([backdrop('Студия', theatre_backdrop('#3d6fb5', '#2c5590'))],
                    note='Студия викторины. Программа сцене не нужна.')
    stage.todo = stage.note
    host = g.sprite('Робот', [costume('Молчит', robot_svg(False)), costume('Поёт', robot_svg(True))],
                    x=-90, y=-50, size=120, rotation_style="don't rotate",
                    note='Робот спрашивает и сравнивает «ответ» с правильным словом.\n'
                         'Ответ пишут так же, как в блоке: «Париж», число 8.')
    host.todo = ('Что собираем на уроке:\n'
                 '1. Робот спрашивает имя и здоровается по имени.\n'
                 '2. Робот задаёт вопрос и ждёт ответ.\n'
                 '3. Если ответ равен «Париж» — «Верно!», иначе робот называет правильный ответ.\n'
                 '4. Добавь второй вопрос — свой.\n'
                 'Дополнительно: Звёздочка всегда переходит к указателю мыши.')
    host.when(flag(), set_costume('Молчит'),
              ask('Как тебя зовут?'),
              say_for(join('Привет, ', answer(), '! Начинаем викторину.'), 2),
              ask('Столица Франции?'),
              if_else(eq(answer(), 'Париж'), [say_for('Верно!', 2)], [say_for('Нет. Столица Франции — Париж.', 2)]),
              ask('Сколько ног у паука?'),
              if_else(eq(answer(), 8), [say_for('Верно!', 2)], [say_for('Нет. У паука 8 ног.', 2)]),
              say_for('Викторина окончена. Спасибо за игру!', 2))
    star = g.sprite('Звёздочка', [costume('Звёздочка', sprite_svg('tracker'))], x=140, y=-90, size=40,
                    note='Дополнительно: Звёздочка всегда переходит к указателю мыши.')
    star.todo = 'Дополнительное задание: Звёздочка следует за мышью. Начни с робота.'
    star.when(flag(), forever([goto('_mouse_')]))
    add_mark(g)
    return g


def practice_operators():
    g = practice('07-operators', 7, 'Операторы', 'Калькулятор удачи')
    g.variable('Удача', 0, show=(5, 5))
    stage = g.stage([backdrop('Звёзды', scene_svg(['#2a1f4d', '#6a4fb0'], SCENES['operators']))],
                    note='Фон калькулятора. Программа сцене не нужна.')
    stage.todo = stage.note
    gem = g.sprite('Кристалл', [costume('Кристалл', sprite_svg('gem'))], x=-90, y=-40, size=130,
                   rotation_style="don't rotate",
                   note='Случайное число хранится в переменной «Удача»: так оно одно и то же\n'
                        'и в реплике, и в проверке «Удача > 80».')
    gem.todo = ('Что собираем на уроке:\n'
                '1. Кристалл спрашивает имя.\n'
                '2. Создай переменную «Удача» и запиши в неё случайное число от 1 до 100.\n'
                '3. Кристалл говорит: имя, потом «твоя удача:» и число. Склей слова блоком «объединить».\n'
                '4. Если удача больше 80 — «Ты везунчик!».\n'
                'Понадобятся зелёные блоки: «случайное от … до …», «объединить», «… > …».')
    gem.when(flag(), ask('Как тебя зовут?'), set_var('Удача', rnd(1, 100)),
             say_for(join(answer(), ', твоя удача: ', var('Удача')), 3),
             if_else(gt(var('Удача'), 80), [say_for('Ты везунчик!', 2)],
                     [say_for('Нажми на флажок и попробуй ещё раз.', 2)]))
    add_mark(g)
    return g


def practice_data():
    g = practice('08-data', 8, 'Данные', 'Список покупок')
    items = 'Покупки'
    g.list(items, show=(5, 5, 200, 200))
    stage = g.stage([backdrop('Магазин', scene_svg(['#27405c', '#3a8f7c'], SCENES['data']))],
                    note='Фон магазина. Программа сцене не нужна.')
    stage.todo = stage.note
    basket = g.sprite('Корзина', [costume('Корзина', BASKET)], x=110, y=-80, size=130, rotation_style="don't rotate",
                      note='Флажок — список очищается, корзина три раза спрашивает и добавляет ответ в список.\n'
                           'Пробел — добавить ещё одну покупку.')
    basket.todo = ('Что собираем на уроке:\n'
                   '1. Создай список «Покупки».\n'
                   '2. Флажок — список очищается и прячется.\n'
                   '3. Корзина три раза спрашивает «Что купить?» и добавляет ответ в список.\n'
                   '4. В конце список показывается, а корзина говорит, сколько в нём покупок.\n'
                   'Дополнительно: пробел — добавить ещё одну покупку.')
    basket.when(flag(), list_clear(items), hide_list(items),
                say_for('Собираемся в магазин. Запишем три покупки!', 2),
                repeat(3, [ask('Что купить?'), list_add(answer(), items)]),
                show_list(items),
                say_for(join('В списке покупок: ', list_length(items)), 2),
                say_for(join('Сначала купим: ', list_item(1, items)), 2))
    basket.when(key('space'), ask('Что ещё купить?'), list_add(answer(), items))
    add_mark(g)
    return g


PRACTICE = [practice_events, practice_motion, practice_looks, practice_sound,
            practice_control, practice_sensing, practice_operators, practice_data]


def starter(game):
    """Turn a solution into a starter: the artwork stays, the program, variables and lists go."""
    game.kind = 'Заготовка'
    game.variables, game.lists = {}, {}
    for target in game.targets:
        target.scripts, target.locals = [], {}
        target.note = target.todo
        for name, value in getattr(target, 'start', {}).items():
            setattr(target, name, value)
    return game


def assets_of(project):
    return sorted((t['name'], a['name'], a['md5ext']) for t in project['targets'] for a in t['costumes'] + t['sounds'])


def main():
    check = '--check' in sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for make in PRACTICE:
        solution = make()
        done, done_assets = solution.project()
        start, start_assets = starter(make()).project()
        if assets_of(start) != assets_of(done):
            sys.exit(f'{solution.stem}: the starter and the solution have different artwork or sounds')
        if any(t['blocks'] or t['variables'] or t['lists'] or t['broadcasts'] for t in start['targets']):
            sys.exit(f'{solution.stem}: the starter must not contain blocks, variables, lists or messages')
        if not sum(len(t['blocks']) for t in done['targets']):
            sys.exit(f'{solution.stem}: the solution has no program')
        for kind, project, assets in (('start', start, start_assets), ('solution', done, done_assets)):
            data = package(project, assets)
            path = OUT / f'{solution.stem}-{kind}.sb3'
            if check:
                if not path.exists() or contents(path.read_bytes()) != contents(data):
                    stale.append(path.name)
            else:
                path.write_bytes(data)
            counts = solution.stats(project)
            summary = ', '.join(f'{CATEGORY_NAMES[c]} {n}' for c, n in sorted(counts.items(), key=lambda kv: -kv[1]))
            print(f'{path.relative_to(ROOT)}: {len(data):,} bytes, {sum(counts.values())} blocks'
                  + (f' ({summary})' if summary else ''))
    if stale:
        sys.exit('Out of date, run python3 scripts/build-practice.py: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
