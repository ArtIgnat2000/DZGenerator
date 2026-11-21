#!/usr/bin/env python3
"""Сверяет миссии писем «Готовимся к уроку» с программами игр.

В миссии ученик ищет в игре конкретный блок и меняет в нём конкретное число. Если игру
изменить в scripts/build-games.py, а текст миссии в V-labs-generator.html оставить прежним,
ребёнок не найдёт блок и застрянет. Скрипт проверяет обе стороны каждого такого факта:

  - в игре у названного спрайта есть этот блок с этим числом, и встречается он столько раз,
    сколько сказано в «Ответах для вас»;
  - в тексте миссии этого урока есть фраза, которая на этот факт опирается.

Запуск:
    python3 scripts/check-missions.py

Проверка читает только файлы — саму игру она не запускает. Как пройти миссии в настоящем
движке Scratch, написано в checks/play-missions.js.
"""
import json, re, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GAMES = ROOT / 'lessons' / 'games'
GAMES2 = ROOT / 'lessons' / 'course-2' / 'games'

# (спрайт, блок, {поле или вход: значение}, сколько раз встречается, фразы миссии, которые на это опираются)
FACTS = {
    1: ('01-events.sb3', [
        ('Солнце', 'event_whengreaterthan', {'WHENGREATERTHANMENU': 'TIMER', 'VALUE': '20'}, 1,
         ['спрайт «Солнце»', '[когда таймер > 20]', '5 вместо 20']),
        ('Солнце', 'event_whenkeypressed', {'KEY_OPTION': 'space'}, 1, ['нажми пробел', 'пробел — радуга']),
        ('Облако', 'event_whenkeypressed', {'KEY_OPTION': '3'}, 1, ['клавишу 3', 'клавиша 3 — гром']),
        ('Облако', 'event_whenkeypressed', {'KEY_OPTION': '4'}, 1, ['Ветер — клавиша 4']),
    ]),
    2: ('02-motion.sb3', [
        ('Ракета', 'motion_movesteps', {'STEPS': '6'}, 4,
         ['спрайт «Ракета»', '[идти 6 шагов]', '20 вместо 6', 'встречается 4 раза']),
    ]),
    3: ('03-looks.sb3', [
        ('Артист', 'looks_changesizeby', {'CHANGE': '10'}, 1,
         ['спрайт «Артист»', '[изменить размер на 10]', '50 вместо 10']),
        ('Артист', 'looks_setsizeto', {'SIZE': '120'}, 2, ['со 120 до 270']),
        ('Артист', 'event_whenkeypressed', {'KEY_OPTION': '7'}, 1, ['клавишу 7']),
        ('Stage', 'event_whenstageclicked', {}, 1, ['Кликни по занавесу']),
    ]),
    4: ('04-sound.sb3', [
        ('Синтезатор', 'sound_changevolumeby', {'VOLUME': '-10'}, 1,
         ['спрайт «Синтезатор»', '[изменить громкость на -10]', '-40 вместо -10']),
        ('Синтезатор', 'sound_setvolumeto', {'VOLUME': '80'}, 1, ['громкость равна 80', 'после двух нажатий (было восемь)']),
        ('Барабан', 'sound_setvolumeto', {'VOLUME': '90'}, 1, ['громкость после флажка 90', 'за девять нажатий']),
        ('Барабан', 'sound_changevolumeby', {'VOLUME': '-10'}, 1, ['У барабана свой такой же блок']),
    ]),
    5: ('05-control.sb3', [
        ('Stage', 'control_wait', {'DURATION': '8'}, 1, ['нажми на «Сцена»', '[ждать 8 секунд]', '2 вместо 8']),
        ('Корабль', 'event_whenkeypressed', {'KEY_OPTION': 'space'}, 1, ['Набери 10 очков и нажми пробел']),
    ]),
    6: ('06-sensing.sb3', [
        ('Следопыт', 'sensing_distanceto', {'DISTANCETOMENU': 'Клад'}, 3,
         ['спрайт «Следопыт»', '[расстояние до Клад]', 'встречается у следопыта 3 раза']),
        ('Следопыт', 'operator_lt', {'OPERAND2': '80'}, 1, ['стоит число 80', '«Горячо!» — ближе 80']),
        ('Следопыт', 'operator_lt', {'OPERAND2': '130'}, 1, ['ближе 130 шагов']),
        ('Следопыт', 'motion_movesteps', {}, 1, ['Найди блок «идти»']),
        ('Следопыт', 'operator_divide', {'NUM2': '6'}, 1, ['замени в нём 6 на 2']),
    ]),
    7: ('07-operators.sb3', [
        ('Оракул', 'operator_random', {'FROM': '2', 'TO': '9'}, 2,
         ['спрайт «Оракул»', '[выдать случайное от 2 до 9]', '99 вместо 9', 'от 2 до 9» два']),
        ('Оракул', 'control_repeat', {'TIMES': '5'}, 1, ['реши пять примеров', 'из пяти']),
    ]),
    8: ('08-data.sb3', [
        ('Дневник', 'data_addtolist', {'LIST': 'Мои желания'}, 2,
         ['спрайт «Дневник»', '[добавить ответ к Мои желания]', 'встречается 2 раза']),
        ('Дневник', 'control_repeat', {'TIMES': '3'}, 1, ['[повторить 3 раз]', '5 вместо 3', 'запиши три желания']),
        ('Дневник', 'event_whenkeypressed', {'KEY_OPTION': '6'}, 1, ['нажми клавишу 6']),
        ('Дневник', 'event_whenkeypressed', {'KEY_OPTION': '5'}, 1, ['Клавиша 5 ищет желание']),
        ('Дневник', 'event_whenkeypressed', {'KEY_OPTION': '0'}, 1, ['Клавиша 0 стирает всё']),
    ]),
}


# Курс 2: миссия «Готовимся к уроку» проверяет демо-игру урока.
FACTS2 = {
    1: ('01-chase.sb3', [
        ('Лис', 'motion_changexby', {'DX': '15'}, 1, ['[изменить x на 15]']),
    ]),
    2: ('02-platform.sb3', [
        ('Герой', 'data_changevariableby', {'VARIABLE': 'Скорость', 'VALUE': '-1'}, 1,
         ['[изменить Скорость на -1]']),
        ('Герой', 'data_setvariableto', {'VARIABLE': 'Скорость', 'VALUE': '14'}, 1, ['+14', 'Скорость']),
    ]),
    3: ('03-maze.sb3', [
        ('Робот', 'sensing_touchingobject', {'TOUCHINGOBJECTMENU': 'Стены'}, 4,
         ['[если касается Стены, то …]']),
    ]),
    4: ('04-catcher.sb3', [
        ('Яблоко', 'control_create_clone_of', {'CLONE_OPTION': '_myself_'}, 1, ['[создать клон]']),
        ('Яблоко', 'control_delete_this_clone', {}, 1, ['[удалить клон]']),
    ]),
    5: ('05-pursuit.sb3', [
        ('Тень', 'motion_pointtowards', {'TOWARDS': 'Лис'}, 1, ['[направиться к Лис]']),
        ('Тень', 'motion_movesteps', {'STEPS': '2'}, 1, ['[двигаться на 2 шагов]']),
    ]),
    6: ('06-shooter.sb3', [
        ('Пуля', 'control_start_as_clone', {}, 1, ['[когда я начинаю как клон]']),
        ('Пуля', 'control_create_clone_of', {'CLONE_OPTION': '_myself_'}, 1, ['[создать клон]']),
    ]),
    7: ('07-quest.sb3', [
        ('Предмет 1', 'looks_switchbackdropto', {'BACKDROP': 'Замок'}, 1, ['[переключить фон на Замок]']),
        ('Предмет 1', 'event_broadcast', {'BROADCAST_INPUT': 'Уровень 2'}, 1, ['[отправить Уровень 2]']),
    ]),
    8: ('08-own-game.sb3', [
        ('Герой', 'sensing_askandwait', {}, 1, ['[спросить … и ждать]']),
        ('Герой', 'data_setvariableto', {'VARIABLE': 'Скорость', 'VALUE': '14'}, 1, ['«Скорость»']),
    ]),
}


def value(blocks, block, name):
    """Значение поля или входа блока так, как его видит ученик; None — если там выражение."""
    if name in block.get('fields', {}):
        return str(block['fields'][name][0])
    if name not in block.get('inputs', {}):
        return None
    inner = block['inputs'][name][1]
    if isinstance(inner, list):                       # число или текст, вписанные прямо в блок
        return str(inner[1])
    menu = blocks.get(inner)
    if isinstance(menu, dict) and menu.get('shadow') and len(menu['fields']) == 1:  # выпадающее меню
        return str(next(iter(menu['fields'].values()))[0])
    return None


def mission_texts():
    """Строки LESSONS и GAME_LESSONS из генератора: номер урока → исходный текст."""
    src = (ROOT / 'V-labs-generator.html').read_text(encoding='utf-8')
    first = src.split('const GAME_LESSONS=', 1)[0]
    found = {int(m.group(1)): m.group(0) for m in re.finditer(r'^\{n:(\d+),.*$', first, re.M)}
    second = src.split('const GAME_LESSONS=', 1)[1].split('\n];', 1)[0]
    found2 = {int(m.group(1)): m.group(0) for m in re.finditer(r'^\{n:(\d+),.*$', second, re.M)}
    return found, found2


def check(course, facts_map, games_dir, texts, errors):
    for n, (file, facts) in sorted(facts_map.items()):
        project = json.loads(zipfile.ZipFile(games_dir / file).read('project.json'))
        targets = {('Stage' if t['isStage'] else t['name']): t for t in project['targets']}
        text = texts.get(n, '')
        if not text:
            errors.append(f'курс {course}, урок {n}: в генераторе нет строки урока')
        for sprite, opcode, want, count, phrases in facts:
            what = f'курс {course}, урок {n}, {file}: «{sprite}» · {opcode} {want or ""}'.rstrip()
            target = targets.get(sprite)
            if not target:
                errors.append(f'{what}: в игре нет такого спрайта')
                continue
            blocks = target['blocks']
            got = sum(1 for b in blocks.values() if isinstance(b, dict) and b['opcode'] == opcode and not b['shadow']
                      and all(value(blocks, b, k) == v for k, v in want.items()))
            if got != count:
                errors.append(f'{what}: в игре таких блоков {got}, а миссия рассчитана на {count}')
            for phrase in phrases:
                if phrase not in text:
                    errors.append(f'{what}: в миссии нет фразы «{phrase}» — текст изменён, проверьте, что он сходится с игрой')
        if not any(e.startswith(f'курс {course}, урок {n}') for e in errors):
            print(f'курс {course}, урок {n}: {file} — сходится с игрой, проверено фактов: {len(facts)}')


def main():
    (texts1, texts2), errors = mission_texts(), []
    check(1, FACTS, GAMES, texts1, errors)
    check(2, FACTS2, GAMES2, texts2, errors)
    if errors:
        for e in errors:
            print('::error::' + e, file=sys.stderr)
        sys.exit(1)
    print('Миссии сходятся с играми.')


if __name__ == '__main__':
    main()
