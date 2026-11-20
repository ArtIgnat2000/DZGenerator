#!/usr/bin/env python3
"""Build eight self-contained, illustrated Scratch 3 projects for V Labs lessons.

Every project is assembled only from standard Scratch 3 blocks (no extensions,
no custom blocks), carries a visible «V Labs» badge sprite and a «V Labs» note
in the code area, and focuses on the block category of its lesson.

Usage:
    python3 scripts/build-games.py          # rebuild lessons/games/*.sb3
    python3 scripts/build-games.py --check  # verify the committed files are up to date
"""
import hashlib, io, json, math, random, struct, sys, wave, zipfile
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'lessons' / 'games'
BRAND = 'V Labs'

# ───────────────────────────── Artwork ─────────────────────────────
# Scratch-compatible artwork: only basic SVG shapes supported by Scratch Paint.
# No SVG text, filters, gradients, rounded-rectangle attributes, or external assets.

def svg(width, height, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">{body}</svg>')


def badge_svg():
    """«V LABS» wordmark drawn with plain strokes, so it looks the same on stage and in the editor."""
    return svg(128, 40,
        '<path d="M20 2H108A18 18 0 0 1 108 38H20A18 18 0 0 1 20 2Z" fill="#12324d" stroke="#7cf6d3" stroke-width="2.5"/>'
        '<path d="M17 10H25M19 10V17L13 28H29L23 17V10" fill="none" stroke="#7cf6d3" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
        '<path d="M16.5 24H25.5L28 28H14Z" fill="#7cf6d3"/>'
        '<path d="M40 12L46 28L52 12M61 12V28H69M73 28L79.5 12L86 28M75.5 22H83.5'
        'M91 12V28M91 12H96A4 4 0 0 1 96 20H91M91 20H97A4 4 0 0 1 97 28H91'
        'M116.5 14.5Q113.5 12 110.5 12Q106 12 106 16Q106 19.5 111 20Q116.5 20.5 116.5 24Q116.5 28 111.5 28Q108 28 105.5 25.5" '
        'fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')


STARS = ''.join(
    f'<circle cx="{(i*73+29)%480}" cy="{(i*47+19)%220}" r="{1+(i%3)*.6}" fill="#ffffff" opacity="{.3+(i%4)*.12}"/>'
    for i in range(24))
HILLS = ('<path d="M0 260Q85 222 170 264T340 249T480 257V360H0Z" fill="#173850" opacity=".58"/>'
         '<path d="M0 298Q100 275 215 300T480 288V360H0Z" fill="#0f6c6b" opacity=".62"/>'
         '<path d="M0 315Q92 282 178 315T337 315T480 315V360H0Z" fill="#0b535b" opacity=".5"/>')


def scene_svg(colors, scene, stars=True):
    a, b = colors
    return svg(480, 360,
        f'<rect width="480" height="360" fill="{a}"/><path d="M0 0h480v210H0Z" fill="{b}" opacity=".48"/>'
        f'{STARS if stars else ""}{scene}{HILLS}')


def events_backdrop(scene):
    sky = {'sunny': '#9cdef0', 'rainy': '#617caa', 'rainbow': '#a9dced'}[scene]
    weather = {
        'sunny': '<path d="M294 156c0-18 14-32 32-32 8-18 34-22 48-7 16 0 28 13 28 29 16 3 25 13 25 27H300c-13 0-20-5-20-13Z" fill="#f9fdff"/>',
        'rainy': '<path d="M255 153c0-25 19-44 44-44 8-27 44-34 62-14 28-5 51 15 51 40 23 5 33 17 33 37H273c-14 0-22-8-18-19Z" fill="#8299b8"/><path d="m292 191-9 24m40-24-9 24m40-24-9 24m40-24-9 24" stroke="#c8f3ff" stroke-width="7" stroke-linecap="round"/><path d="m60 214-7 20m47-36-7 20m47-4-7 20m47-36-7 20m47-10-7 20" stroke="#c8f3ff" stroke-width="5" stroke-linecap="round" opacity=".7"/>',
        'rainbow': '<path d="M267 202a89 89 0 0 1 178 0" fill="none" stroke="#ff6d78" stroke-width="13"/><path d="M280 202a76 76 0 0 1 152 0" fill="none" stroke="#ffb95c" stroke-width="13"/><path d="M293 202a63 63 0 0 1 126 0" fill="none" stroke="#ffe66d" stroke-width="13"/><path d="M306 202a50 50 0 0 1 100 0" fill="none" stroke="#6ed9a7" stroke-width="13"/><path d="M319 202a37 37 0 0 1 74 0" fill="none" stroke="#69baff" stroke-width="13"/>',
    }[scene]
    return svg(480, 360,
        f'<rect width="480" height="360" fill="{sky}"/><circle cx="82" cy="120" r="54" fill="#ffffff" opacity=".16"/>'
        f'<circle cx="82" cy="120" r="38" fill="#ffffff" opacity=".1"/>{weather}'
        '<path d="M0 250q85-62 177 0t160-4q76-50 143 2v112H0Z" fill="#55c998"/>'
        '<path d="M0 286q98-58 184 0t160-3q69-42 136 1v76H0Z" fill="#167c77" opacity=".7"/>'
        '<path d="M0 315q92-33 178 0t159 0q75-30 143 0v45H0Z" fill="#126b6e" opacity=".65"/>')


def theatre_backdrop(curtain, fold):
    scene = (f'<path d="M0 0h95v250H0Z" fill="{curtain}"/><path d="M385 0h95v250h-95Z" fill="{curtain}"/>'
             f'<path d="M95 0h42v235H95Zm248 0h42v235h-42Z" fill="{fold}"/>'
             f'<path d="M0 0h480v26H0Z" fill="{curtain}"/><path d="M0 26q30 22 60 0t60 0 60 0 60 0 60 0 60 0 60 0 60 0V0H0Z" fill="{fold}"/>'
             '<path d="M0 238q240 54 480 0v34q-240 56-480 0Z" fill="#f5b86e"/>')
    return svg(480, 360,
        '<rect width="480" height="360" fill="#482654"/><path d="M0 0h480v210H0Z" fill="#d45481" opacity=".4"/>'
        f'{scene}<path d="M0 272q240 56 480 0v88H0Z" fill="#6e3f37"/><path d="M0 300q240 40 480 0v60H0Z" fill="#5b322d"/>')


SCENES = {
    'motion': '<circle cx="386" cy="92" r="34" fill="#f2a65e"/><path d="M356 80q30 14 60 0M354 100q32 12 64 0" fill="none" stroke="#d97f48" stroke-width="5" stroke-linecap="round"/><path d="M330 92a56 12 0 1 0 112 0a56 12 0 1 0-112 0Z" fill="none" stroke="#ffe3a8" stroke-width="4"/><circle cx="96" cy="150" r="13" fill="#9cefff" opacity=".8"/>',
    'sound': '<path d="M64 224h42v-48H64Zm68 0h42v-96h-42Zm68 0h42V96h-42Zm68 0h42v-72h-42Zm68 0h42v-124h-42Z" fill="#71e4d0" opacity=".75"/><path d="M55 231h334" stroke="#d2fff4" stroke-width="4"/>',
    'control': '<circle cx="388" cy="150" r="36" fill="#d9d4ee"/><circle cx="376" cy="140" r="8" fill="#b9b2d6"/><circle cx="400" cy="162" r="6" fill="#b9b2d6"/><circle cx="398" cy="134" r="4" fill="#b9b2d6"/>',
    'sensing': '<circle cx="360" cy="158" r="68" fill="none" stroke="#68e7ce" stroke-width="3" opacity=".5"/><circle cx="360" cy="158" r="42" fill="none" stroke="#a1fff0" stroke-width="3" opacity=".65"/><circle cx="360" cy="158" r="15" fill="#fff0a0"/>',
    'operators': '<path d="M300 96h28m-14-14v28M352 96h28M300 168l22 22m0-22-22 22M352 172h28m-14-10v1m0 18v1M300 232h28m-28 12h28" fill="none" stroke="#e8dcff" stroke-width="7" stroke-linecap="round" opacity=".8"/><path d="M404 84v168" stroke="#a98aff" stroke-width="4" stroke-linecap="round" opacity=".6"/>',
    'data': '<path d="M250 96h196v150H250Z" fill="#17425c" opacity=".55"/><path d="M270 126h156m-156 30h156m-156 30h156m-156 30h100" stroke="#51b69e" stroke-width="5" stroke-linecap="round" opacity=".8"/>',
}

HEX = 'M48 7 84 28v40L48 89 12 68V28Z'
MOODS = {
    # name: (front, side, top, face)
    'Радость': ('#ef8bb7', '#8fe3d0', '#ffe08a', '<circle cx="37" cy="44" r="3" fill="#513060"/><circle cx="58" cy="44" r="3" fill="#513060"/><path d="M39 57q9 8 18 0" fill="none" stroke="#513060" stroke-width="3" stroke-linecap="round"/>'),
    'Грусть': ('#7f9be6', '#9fd0f5', '#dbe8ff', '<circle cx="37" cy="45" r="3" fill="#2c3566"/><circle cx="58" cy="45" r="3" fill="#2c3566"/><path d="M39 62q9-8 18 0" fill="none" stroke="#2c3566" stroke-width="3" stroke-linecap="round"/><path d="M61 51q4 7 0 9-4-2 0-9Z" fill="#e9fbff"/>'),
    'Удивление': ('#ffb35c', '#ffe08a', '#fff4c9', '<circle cx="37" cy="43" r="4.5" fill="#5a3410"/><circle cx="58" cy="43" r="4.5" fill="#5a3410"/><circle cx="48" cy="60" r="5.5" fill="#5a3410"/><path d="M31 33q6-5 12 0M52 33q6-5 12 0" fill="none" stroke="#5a3410" stroke-width="2.5" stroke-linecap="round"/>'),
    'Спокойствие': ('#8fd9a8', '#c9b8f2', '#f2fff2', '<path d="M32 45q5 4 10 0M53 45q5 4 10 0" fill="none" stroke="#2f5a48" stroke-width="3" stroke-linecap="round"/><path d="M41 59h14" stroke="#2f5a48" stroke-width="3" stroke-linecap="round"/>'),
}


def mood_svg(name):
    front, side, top, face = MOODS[name]
    return svg(96, 96,
        f'<path d="{HEX}" fill="{front}"/><path d="M48 7v39L12 28ZM48 46l36-18v40L48 89Z" fill="{side}"/>'
        f'<path d="m48 7 36 21-36 18-36-18Z" fill="{top}"/>{face}')


SPRITES = {
    'sun': '<circle cx="48" cy="48" r="25" fill="#ffbf38"/><circle cx="48" cy="48" r="18" fill="#ffe98a"/><path d="M48 5v10M48 81v10M5 48h10M81 48h10M18 18l8 8m44 44 8 8M78 18l-8 8M26 70l-8 8" stroke="#ffdc67" stroke-width="7" stroke-linecap="round"/><circle cx="41" cy="45" r="2.5" fill="#24395c"/><circle cx="56" cy="45" r="2.5" fill="#24395c"/><path d="M41 55q7 8 14 0" fill="none" stroke="#24395c" stroke-width="2.5" stroke-linecap="round"/>',
    # The rocket is drawn facing right, so «move steps» sends it nose-first.
    'rocket': '<g transform="rotate(90 48 48)"><path d="M48 4 75 76 49 65 23 76Z" fill="#e8f4ff"/><path d="m48 8 1 57-22 10Z" fill="#f7fbff"/><path d="m48 8 25 67-23-10Z" fill="#79d9e5"/><path d="m23 76 25-11 26 11-16 15H38Z" fill="#ff8b60"/><circle cx="48" cy="43" r="6" fill="#192c55"/><path d="M30 75 14 87M66 75l16 12" stroke="#ffc863" stroke-width="5" stroke-linecap="round"/></g>',
    'beacon': '<circle cx="48" cy="48" r="43" fill="#ffe875" opacity=".28"/><circle cx="48" cy="48" r="29" fill="#ffe875" opacity=".42"/><path d="M48 18v57M34 37l14-18 14 18" fill="none" stroke="#baffed" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="48" cy="46" r="7" fill="#fff"/><path d="M29 76h38" stroke="#fff" stroke-width="4" stroke-linecap="round"/>',
    'asteroid': '<path d="M30 14 58 10 80 26 86 52 72 78 44 86 18 72 10 44Z" fill="#8d7b74" stroke="#c9b8ab" stroke-width="3" stroke-linejoin="round"/><circle cx="38" cy="36" r="8" fill="#6f5f5a"/><circle cx="62" cy="54" r="10" fill="#6f5f5a"/><circle cx="40" cy="64" r="5" fill="#6f5f5a"/><circle cx="64" cy="28" r="4" fill="#6f5f5a"/>',
    'spotlight': '<circle cx="60" cy="60" r="58" fill="#fff6c7" opacity=".5"/><circle cx="60" cy="60" r="42" fill="#fffbe6" opacity=".6"/><circle cx="60" cy="60" r="24" fill="#ffffff" opacity=".55"/>',
    'synth': '<circle cx="48" cy="48" r="37" fill="#102840" stroke="#74eed9" stroke-width="3"/><circle cx="48" cy="48" r="28" fill="#17415b" stroke="#c2fff2" stroke-opacity=".55"/><path d="M48 21v27l18 12" fill="none" stroke="#ffe36d" stroke-width="6" stroke-linecap="round"/><circle cx="48" cy="48" r="5" fill="#ff7692"/><path d="M17 48h7m48 0h7M48 17v7m0 48v7" stroke="#fff" stroke-width="3" stroke-linecap="round"/>',
    # The meteor is drawn head-down: it falls from the top of the stage.
    'meteor': '<path d="M48 88 80 30 62 36 60 8 48 26 36 8 34 36 16 30Z" fill="#ff7c63" stroke="#ffe0a1" stroke-width="3" stroke-linejoin="round"/><path d="M48 80 66 44H30Z" fill="#ffc94f"/><circle cx="48" cy="62" r="9" fill="#fff1ba"/>',
    'ship': '<path d="M48 8 72 62 48 52 24 62Z" fill="#e8f4ff" stroke="#79d9e5" stroke-width="3" stroke-linejoin="round"/><circle cx="48" cy="36" r="7" fill="#192c55"/><path d="M24 62 12 80h22ZM72 62l12 18H62Z" fill="#ff8b60"/><path d="M40 58h16l-8 26Z" fill="#ffc94f"/>',
    'tracker': '<path d="M48 10 59 38 89 30 68 51 83 77 55 66 39 91 38 62 9 56 36 44Z" fill="#ffe37a" stroke="#fff4bc" stroke-width="2"/><circle cx="48" cy="49" r="9" fill="#fff"/><circle cx="51" cy="49" r="4" fill="#24395c"/><path d="M20 20 9 12m72 8 10-8M14 79 4 85" stroke="#77efdb" stroke-width="4" stroke-linecap="round"/>',
    'gem': '<path d="M24 34 36 18h24l12 16-24 44Z" fill="#59e0c8" stroke="#eafffa" stroke-width="3" stroke-linejoin="round"/><path d="M24 34h48M36 18l12 16 12-16M48 34v44" fill="none" stroke="#eafffa" stroke-width="2" stroke-linejoin="round"/><path d="M14 20l5 5m63-5-5 5M48 6v6" stroke="#ffd27a" stroke-width="3" stroke-linecap="round"/>',
    'oracle': '<circle cx="48" cy="48" r="37" fill="#a98aff"/><circle cx="48" cy="48" r="26" fill="#f5eaff"/><path d="M34 36c1-10 7-16 16-16 10 0 16 7 16 15 0 7-5 11-11 15-5 3-7 6-7 12" fill="none" stroke="#523c82" stroke-width="6" stroke-linecap="round"/><circle cx="48" cy="72" r="3.5" fill="#523c82"/><path d="M28 15q20-16 40 0" fill="none" stroke="#ffe78a" stroke-width="5" stroke-linecap="round"/>',
    'diary': '<path d="M23 8h34l18 18v50q0 8-8 8H23q-8 0-8-8V16q0-8 8-8Z" fill="#f8fbff"/><path d="M57 8v20h18" fill="#bcefe4"/><path d="M28 43h37M28 54h37M28 65h26" stroke="#51b69e" stroke-width="4" stroke-linecap="round"/><path d="m20 79 4-13 33-33 9 9-33 33Z" fill="#ffbd62"/><path d="m57 33 9 9" stroke="#fff" stroke-width="3"/>',
}
DROP = svg(48, 56, '<path d="M24 5q15 21 15 31a15 15 0 0 1-30 0q0-10 15-31Z" fill="#7fd4ff" stroke="#e8f8ff" stroke-width="3" stroke-linejoin="round"/><path d="M17 36q0 7 6 9" fill="none" stroke="#ffffff" stroke-width="3" stroke-linecap="round"/>')
DRUM = svg(96, 96, '<path d="M14 36v34q0 14 34 14t34-14V36Z" fill="#ff8b60"/><path d="M14 52l17 26M31 44l17 38M48 44l17 38M65 44l17 26" fill="none" stroke="#ffd9a8" stroke-width="3"/><path d="M14 36a34 13 0 1 0 68 0a34 13 0 1 0-68 0Z" fill="#fff4dc" stroke="#ffc94f" stroke-width="4"/><path d="M22 8 44 32M74 8 52 32" stroke="#74eed9" stroke-width="5" stroke-linecap="round"/><circle cx="22" cy="8" r="5" fill="#c2fff2"/><circle cx="74" cy="8" r="5" fill="#c2fff2"/>')
STAR = svg(64, 64, '<path d="M32 4 40 24 61 25 45 39 50 60 32 48 14 60 19 39 3 25 24 24Z" fill="#ffe36d" stroke="#fff7c9" stroke-width="3" stroke-linejoin="round"/><circle cx="32" cy="33" r="6" fill="#fffbe6"/>')
NOTE_ICON = '<path d="M46 26v35" stroke="#fff" stroke-width="5" stroke-linecap="round"/><circle cx="39" cy="62" r="8" fill="#fff"/><path d="M46 26q15 4 16 18" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round"/>'
NOTES_ICON = '<path d="M39 62V33l26-5v29" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/><circle cx="32" cy="62" r="8" fill="#fff"/><circle cx="58" cy="58" r="8" fill="#fff"/>'
STAR_ICON = '<path d="M48 21 55 39 74 40 59 52 64 71 48 60 32 71 37 52 22 40 41 39Z" fill="#ffe36d" stroke="#fff7c9" stroke-width="2" stroke-linejoin="round"/>'


def button_svg(ring, fill, icon):
    """A round stage button; the icon is drawn with shapes because Scratch renders SVG text unreliably."""
    return svg(96, 96, f'<circle cx="48" cy="48" r="43" fill="{ring}"/><circle cx="48" cy="48" r="36" fill="{fill}"/>{icon}')


CLOUD = svg(120, 90, '<path d="M22 67c-8-3-11-9-9-17 2-9 10-14 20-13 4-17 17-25 31-21 10 3 16 10 18 20 14-5 29 4 30 18 1 8-4 14-12 17H22Z" fill="#eaf6ff" stroke="#ffffff" stroke-width="3"/><circle cx="48" cy="52" r="3" fill="#36536e"/><circle cx="72" cy="52" r="3" fill="#36536e"/><path d="M52 64q8 7 16 0" fill="none" stroke="#36536e" stroke-width="3" stroke-linecap="round"/>')


def sprite_svg(kind):
    return svg(96, 96, SPRITES[kind])


def costume(name, data, cx=48, cy=48):
    return {'kind': 'costume', 'name': name, 'data': data.encode('utf-8'), 'ext': 'svg', 'cx': cx, 'cy': cy}


def backdrop(name, data):
    return costume(name, data, 240, 180)


# ───────────────────────────── Sounds ─────────────────────────────
RATE = 22050
NOTES = [('До', 261.63), ('Ре', 293.66), ('Ми', 329.63), ('Фа', 349.23),
         ('Соль', 392.00), ('Ля', 440.00), ('Си', 493.88), ('До высокая', 523.25)]


def wav_sound(name, samples):
    buff = io.BytesIO()
    with wave.open(buff, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', max(-32767, min(32767, int(s)))) for s in samples))
    return {'kind': 'sound', 'name': name, 'data': buff.getvalue(), 'ext': 'wav', 'rate': RATE, 'count': len(samples)}


def note_sound(name, freq, seconds=0.4):
    total = int(RATE * seconds)
    samples = []
    for j in range(total):
        t = j / RATE
        env = min(1, j / 110) * math.exp(-3.4 * t / seconds) * min(1, (total - j) / 400)
        wave_sum = math.sin(2*math.pi*freq*t) + .35*math.sin(4*math.pi*freq*t) + .15*math.sin(6*math.pi*freq*t)
        samples.append(8200 * env * wave_sum)
    return wav_sound(name, samples)


# Notes of the tunes: short code → (name shown in Scratch, MIDI number). The first octave reuses the names of NOTES.
PITCHES = {
    'D4': ('Ре', 62), 'Eb4': ('Ми-бемоль', 63), 'F4': ('Фа', 65), 'F#4': ('Фа-диез', 66), 'G4': ('Соль', 67),
    'G#4': ('Соль-диез', 68), 'A4': ('Ля', 69), 'Bb4': ('Си-бемоль', 70), 'B4': ('Си', 71),
    'C5': ('До высокая', 72), 'C#5': ('До-диез высокая', 73), 'D5': ('Ре высокая', 74),
    'Eb5': ('Ми-бемоль высокая', 75), 'E5': ('Ми высокая', 76), 'F5': ('Фа высокая', 77),
    'F#5': ('Фа-диез высокая', 78), 'G5': ('Соль высокая', 79), 'Bb5': ('Си-бемоль высокая', 82),
}


class Tune:
    """A melody written as text: 'G4:1 Eb4:.75 Bb4:.25 -:.5' is note:beats, «-» is a rest.

    Every note becomes two blocks, «start sound» and «wait», so pupils can read and edit the rhythm.
    Scratch checks a «wait» 30 times a second, so pick a beat whose note lengths do not fall exactly on
    a multiple of 1/30 s — otherwise equal notes come out unequal.
    """

    def __init__(self, beat):
        self.beat = Fraction(str(beat))      # seconds per beat
        self.used = set()

    def part(self, text, beats):
        """Blocks for one piece of the tune; `beats` is its exact length and guards against rhythm typos."""
        items = []
        for token in text.split():
            code, _, length = token.partition(':')
            assert code == '-' or code in PITCHES, f'unknown note {code}'
            items.append((code, Fraction(length)))
        total = sum(length for _, length in items)
        assert total == beats, f'«{text}» lasts {total} beats instead of {beats}'
        nodes, index = [], 0
        while index < len(items):
            run = 1
            while index + run < len(items) and items[index + run] == items[index]:
                run += 1
            if run >= 3 and items[index][0] != '-':
                nodes.append(repeat(run, self._note(*items[index])))   # equal notes in a row read better as a loop
            else:
                for _ in range(run):
                    nodes.extend(self._note(*items[index]))
            index += run
        return nodes

    def bars(self, *bars, beats=4):
        return [node for bar in bars for node in self.part(bar, beats)]

    def _note(self, code, length):
        pause = wait(round(float(length * self.beat), 3))
        if code == '-':
            return [pause]
        self.used.add(code)
        return [play(PITCHES[code][0]), pause]

    def sounds(self):
        codes = sorted(self.used, key=lambda code: PITCHES[code][1])
        return [note_sound(PITCHES[code][0], round(440 * 2 ** ((PITCHES[code][1] - 69) / 12), 2)) for code in codes]


def drum_sound(name='Барабан', seconds=0.22):
    rng = random.Random(7)
    total = int(RATE * seconds)
    samples = []
    for j in range(total):
        t = j / RATE
        env = math.exp(-16 * t) * min(1, (total - j) / 300)
        samples.append(env * (9000 * math.sin(2*math.pi*(150 - 260*t)*t) + 5200 * rng.uniform(-1, 1)))
    return wav_sound(name, samples)


# ─────────────────────── Scratch block mini-DSL ───────────────────────
NUM, POS, WHOLE, INT, ANGLE, COLOR, TEXT = 4, 5, 6, 7, 8, 9, 10   # Scratch primitive (shadow) types
BOOL, STACK, FIELD, VAR, LIST, BFIELD, BCAST = 'bool', 'stack', 'field', 'var', 'list', 'bfield', 'bcast'


def menu(opcode, field):
    return ('menu', opcode, field)


KEYS = ['space', 'up arrow', 'down arrow', 'right arrow', 'left arrow', 'any'] + list('0123456789')

# opcode → ordered (argument name, kind). Kinds describe how Scratch stores the argument.
SPEC = {
    # Events
    'event_whenflagclicked': [],
    'event_whenkeypressed': [('KEY_OPTION', FIELD)],
    'event_whenthisspriteclicked': [],
    'event_whenstageclicked': [],
    'event_whenbackdropswitchesto': [('BACKDROP', FIELD)],
    'event_whengreaterthan': [('WHENGREATERTHANMENU', FIELD), ('VALUE', NUM)],
    'event_whenbroadcastreceived': [('BROADCAST_OPTION', BFIELD)],
    'event_broadcast': [('BROADCAST_INPUT', BCAST)],
    'event_broadcastandwait': [('BROADCAST_INPUT', BCAST)],
    # Motion
    'motion_movesteps': [('STEPS', NUM)],
    'motion_turnright': [('DEGREES', NUM)],
    'motion_turnleft': [('DEGREES', NUM)],
    'motion_goto': [('TO', menu('motion_goto_menu', 'TO'))],
    'motion_gotoxy': [('X', NUM), ('Y', NUM)],
    'motion_glideto': [('SECS', NUM), ('TO', menu('motion_glideto_menu', 'TO'))],
    'motion_glidesecstoxy': [('SECS', NUM), ('X', NUM), ('Y', NUM)],
    'motion_pointindirection': [('DIRECTION', ANGLE)],
    'motion_pointtowards': [('TOWARDS', menu('motion_pointtowards_menu', 'TOWARDS'))],
    'motion_changexby': [('DX', NUM)],
    'motion_setx': [('X', NUM)],
    'motion_changeyby': [('DY', NUM)],
    'motion_sety': [('Y', NUM)],
    'motion_ifonedgebounce': [],
    'motion_setrotationstyle': [('STYLE', FIELD)],
    'motion_xposition': [], 'motion_yposition': [], 'motion_direction': [],
    # Looks
    'looks_sayforsecs': [('MESSAGE', TEXT), ('SECS', NUM)],
    'looks_say': [('MESSAGE', TEXT)],
    'looks_thinkforsecs': [('MESSAGE', TEXT), ('SECS', NUM)],
    'looks_think': [('MESSAGE', TEXT)],
    'looks_switchcostumeto': [('COSTUME', menu('looks_costume', 'COSTUME'))],
    'looks_nextcostume': [],
    'looks_switchbackdropto': [('BACKDROP', menu('looks_backdrops', 'BACKDROP'))],
    'looks_nextbackdrop': [],
    'looks_changesizeby': [('CHANGE', NUM)],
    'looks_setsizeto': [('SIZE', NUM)],
    'looks_changeeffectby': [('EFFECT', FIELD), ('CHANGE', NUM)],
    'looks_seteffectto': [('EFFECT', FIELD), ('VALUE', NUM)],
    'looks_cleargraphiceffects': [],
    'looks_show': [], 'looks_hide': [],
    'looks_gotofrontback': [('FRONT_BACK', FIELD)],
    'looks_goforwardbackwardlayers': [('FORWARD_BACKWARD', FIELD), ('NUM', INT)],
    'looks_costumenumbername': [('NUMBER_NAME', FIELD)],
    'looks_backdropnumbername': [('NUMBER_NAME', FIELD)],
    'looks_size': [],
    # Sound
    'sound_playuntildone': [('SOUND_MENU', menu('sound_sounds_menu', 'SOUND_MENU'))],
    'sound_play': [('SOUND_MENU', menu('sound_sounds_menu', 'SOUND_MENU'))],
    'sound_stopallsounds': [],
    'sound_changeeffectby': [('EFFECT', FIELD), ('VALUE', NUM)],
    'sound_seteffectto': [('EFFECT', FIELD), ('VALUE', NUM)],
    'sound_cleareffects': [],
    'sound_changevolumeby': [('VOLUME', NUM)],
    'sound_setvolumeto': [('VOLUME', NUM)],
    'sound_volume': [],
    # Control
    'control_wait': [('DURATION', POS)],
    'control_repeat': [('TIMES', WHOLE), ('SUBSTACK', STACK)],
    'control_forever': [('SUBSTACK', STACK)],
    'control_if': [('CONDITION', BOOL), ('SUBSTACK', STACK)],
    'control_if_else': [('CONDITION', BOOL), ('SUBSTACK', STACK), ('SUBSTACK2', STACK)],
    'control_wait_until': [('CONDITION', BOOL)],
    'control_repeat_until': [('CONDITION', BOOL), ('SUBSTACK', STACK)],
    'control_stop': [('STOP_OPTION', FIELD)],
    'control_start_as_clone': [],
    'control_create_clone_of': [('CLONE_OPTION', menu('control_create_clone_of_menu', 'CLONE_OPTION'))],
    'control_delete_this_clone': [],
    # Sensing
    'sensing_touchingcolor': [('COLOR', COLOR)],
    'sensing_touchingobject': [('TOUCHINGOBJECTMENU', menu('sensing_touchingobjectmenu', 'TOUCHINGOBJECTMENU'))],
    'sensing_distanceto': [('DISTANCETOMENU', menu('sensing_distancetomenu', 'DISTANCETOMENU'))],
    'sensing_askandwait': [('QUESTION', TEXT)],
    'sensing_answer': [],
    'sensing_keypressed': [('KEY_OPTION', menu('sensing_keyoptions', 'KEY_OPTION'))],
    'sensing_mousedown': [], 'sensing_mousex': [], 'sensing_mousey': [],
    'sensing_setdragmode': [('DRAG_MODE', FIELD)],
    'sensing_timer': [], 'sensing_resettimer': [],
    'sensing_of': [('PROPERTY', FIELD), ('OBJECT', menu('sensing_of_object_menu', 'OBJECT'))],
    'sensing_current': [('CURRENTMENU', FIELD)],
    'sensing_dayssince2000': [],
    # Operators
    'operator_add': [('NUM1', NUM), ('NUM2', NUM)],
    'operator_subtract': [('NUM1', NUM), ('NUM2', NUM)],
    'operator_multiply': [('NUM1', NUM), ('NUM2', NUM)],
    'operator_divide': [('NUM1', NUM), ('NUM2', NUM)],
    'operator_random': [('FROM', NUM), ('TO', NUM)],
    'operator_gt': [('OPERAND1', TEXT), ('OPERAND2', TEXT)],
    'operator_lt': [('OPERAND1', TEXT), ('OPERAND2', TEXT)],
    'operator_equals': [('OPERAND1', TEXT), ('OPERAND2', TEXT)],
    'operator_and': [('OPERAND1', BOOL), ('OPERAND2', BOOL)],
    'operator_or': [('OPERAND1', BOOL), ('OPERAND2', BOOL)],
    'operator_not': [('OPERAND', BOOL)],
    'operator_join': [('STRING1', TEXT), ('STRING2', TEXT)],
    'operator_letter_of': [('LETTER', WHOLE), ('STRING', TEXT)],
    'operator_length': [('STRING', TEXT)],
    'operator_contains': [('STRING1', TEXT), ('STRING2', TEXT)],
    'operator_mod': [('NUM1', NUM), ('NUM2', NUM)],
    'operator_round': [('NUM', NUM)],
    'operator_mathop': [('OPERATOR', FIELD), ('NUM', NUM)],
    # Data
    'data_variable': [('VARIABLE', VAR)],
    'data_setvariableto': [('VARIABLE', VAR), ('VALUE', TEXT)],
    'data_changevariableby': [('VARIABLE', VAR), ('VALUE', NUM)],
    'data_showvariable': [('VARIABLE', VAR)],
    'data_hidevariable': [('VARIABLE', VAR)],
    'data_addtolist': [('ITEM', TEXT), ('LIST', LIST)],
    'data_deleteoflist': [('INDEX', INT), ('LIST', LIST)],
    'data_deletealloflist': [('LIST', LIST)],
    'data_insertatlist': [('ITEM', TEXT), ('INDEX', INT), ('LIST', LIST)],
    'data_replaceitemoflist': [('INDEX', INT), ('LIST', LIST), ('ITEM', TEXT)],
    'data_itemoflist': [('INDEX', INT), ('LIST', LIST)],
    'data_itemnumoflist': [('ITEM', TEXT), ('LIST', LIST)],
    'data_lengthoflist': [('LIST', LIST)],
    'data_listcontainsitem': [('LIST', LIST), ('ITEM', TEXT)],
    'data_showlist': [('LIST', LIST)],
    'data_hidelist': [('LIST', LIST)],
}

# Allowed values of plain dropdown fields — a typo here would give a broken block in Scratch.
FIELD_VALUES = {
    ('event_whenkeypressed', 'KEY_OPTION'): KEYS,
    ('event_whengreaterthan', 'WHENGREATERTHANMENU'): ['TIMER'],
    ('motion_setrotationstyle', 'STYLE'): ['left-right', "don't rotate", 'all around'],
    ('looks_changeeffectby', 'EFFECT'): ['COLOR', 'FISHEYE', 'WHIRL', 'PIXELATE', 'MOSAIC', 'BRIGHTNESS', 'GHOST'],
    ('looks_seteffectto', 'EFFECT'): ['COLOR', 'FISHEYE', 'WHIRL', 'PIXELATE', 'MOSAIC', 'BRIGHTNESS', 'GHOST'],
    ('looks_gotofrontback', 'FRONT_BACK'): ['front', 'back'],
    ('looks_goforwardbackwardlayers', 'FORWARD_BACKWARD'): ['forward', 'backward'],
    ('looks_costumenumbername', 'NUMBER_NAME'): ['number', 'name'],
    ('looks_backdropnumbername', 'NUMBER_NAME'): ['number', 'name'],
    ('sound_changeeffectby', 'EFFECT'): ['PITCH', 'PAN'],
    ('sound_seteffectto', 'EFFECT'): ['PITCH', 'PAN'],
    ('control_stop', 'STOP_OPTION'): ['all', 'this script', 'other scripts in sprite'],
    ('sensing_setdragmode', 'DRAG_MODE'): ['draggable', 'not draggable'],
    ('sensing_of', 'PROPERTY'): ['x position', 'y position', 'direction', 'costume #', 'costume name', 'size', 'volume'],
    ('sensing_current', 'CURRENTMENU'): ['YEAR', 'MONTH', 'DATE', 'DAYOFWEEK', 'HOUR', 'MINUTE', 'SECOND'],
    ('operator_mathop', 'OPERATOR'): ['abs', 'floor', 'ceiling', 'sqrt'],
}
HATS = {'event_whenflagclicked', 'event_whenkeypressed', 'event_whenthisspriteclicked', 'event_whenstageclicked',
        'event_whenbackdropswitchesto', 'event_whengreaterthan', 'event_whenbroadcastreceived', 'control_start_as_clone'}
CATEGORY_NAMES = {'event': 'События', 'motion': 'Движение', 'looks': 'Внешность', 'sound': 'Звук',
                  'control': 'Управление', 'sensing': 'Сенсоры', 'operator': 'Операторы', 'data': 'Данные'}


class Node:
    __slots__ = ('op', 'args')

    def __init__(self, op, *args):
        if len(args) != len(SPEC[op]):
            raise ValueError(f'{op}: expected {len(SPEC[op])} arguments, got {len(args)}')
        self.op, self.args = op, args


def _alias(op):
    return lambda *args: Node(op, *args)


# Short readable names for the blocks used by the games.
flag = _alias('event_whenflagclicked');            key = _alias('event_whenkeypressed')
clicked = _alias('event_whenthisspriteclicked');   stage_clicked = _alias('event_whenstageclicked')
backdrop_is = _alias('event_whenbackdropswitchesto')
receive = _alias('event_whenbroadcastreceived');   broadcast = _alias('event_broadcast')
broadcast_wait = _alias('event_broadcastandwait')
move = _alias('motion_movesteps');                 right = _alias('motion_turnright')
left = _alias('motion_turnleft');                  goto = _alias('motion_goto')
goto_xy = _alias('motion_gotoxy');                 glide_to = _alias('motion_glideto')
glide_xy = _alias('motion_glidesecstoxy');         point = _alias('motion_pointindirection')
point_to = _alias('motion_pointtowards');          dx = _alias('motion_changexby')
set_x = _alias('motion_setx');                     dy = _alias('motion_changeyby')
set_y = _alias('motion_sety');                     bounce = _alias('motion_ifonedgebounce')
rotation = _alias('motion_setrotationstyle');      x_pos = _alias('motion_xposition')
y_pos = _alias('motion_yposition');                direction = _alias('motion_direction')
say_for = _alias('looks_sayforsecs');              say = _alias('looks_say')
think_for = _alias('looks_thinkforsecs');          think = _alias('looks_think')
set_costume = _alias('looks_switchcostumeto');     next_costume = _alias('looks_nextcostume')
set_backdrop = _alias('looks_switchbackdropto');   next_backdrop = _alias('looks_nextbackdrop')
size_by = _alias('looks_changesizeby');            size_to = _alias('looks_setsizeto')
fx_by = _alias('looks_changeeffectby');            fx_to = _alias('looks_seteffectto')
fx_clear = _alias('looks_cleargraphiceffects');    show = _alias('looks_show')
hide = _alias('looks_hide');                       layer = _alias('looks_gotofrontback')
layers = _alias('looks_goforwardbackwardlayers');  costume_info = _alias('looks_costumenumbername')
backdrop_info = _alias('looks_backdropnumbername'); size = _alias('looks_size')
play_wait = _alias('sound_playuntildone');         play = _alias('sound_play')
stop_sounds = _alias('sound_stopallsounds');       sfx_by = _alias('sound_changeeffectby')
sfx_to = _alias('sound_seteffectto');              sfx_clear = _alias('sound_cleareffects')
vol_by = _alias('sound_changevolumeby');           vol_to = _alias('sound_setvolumeto')
volume = _alias('sound_volume')
wait = _alias('control_wait');                     repeat = _alias('control_repeat')
forever = _alias('control_forever');               if_ = _alias('control_if')
if_else = _alias('control_if_else');               wait_until = _alias('control_wait_until')
repeat_until = _alias('control_repeat_until');     stop = _alias('control_stop')
as_clone = _alias('control_start_as_clone');       clone = _alias('control_create_clone_of')
delete_clone = _alias('control_delete_this_clone')
touching = _alias('sensing_touchingobject');       distance = _alias('sensing_distanceto')
touching_color = _alias('sensing_touchingcolor')
ask = _alias('sensing_askandwait');                answer = _alias('sensing_answer')
key_down = _alias('sensing_keypressed');           mouse_down = _alias('sensing_mousedown')
mouse_x = _alias('sensing_mousex');                mouse_y = _alias('sensing_mousey')
drag_mode = _alias('sensing_setdragmode');         timer = _alias('sensing_timer')
reset_timer = _alias('sensing_resettimer');        prop_of = _alias('sensing_of')
current = _alias('sensing_current');               days2000 = _alias('sensing_dayssince2000')
add = _alias('operator_add');                      sub = _alias('operator_subtract')
mul = _alias('operator_multiply');                 div = _alias('operator_divide')
rnd = _alias('operator_random');                   gt = _alias('operator_gt')
lt = _alias('operator_lt');                        eq = _alias('operator_equals')
and_ = _alias('operator_and');                     or_ = _alias('operator_or')
not_ = _alias('operator_not');                     letter = _alias('operator_letter_of')
length = _alias('operator_length');                contains = _alias('operator_contains')
mod = _alias('operator_mod');                      round_ = _alias('operator_round')
mathop = _alias('operator_mathop')
var = _alias('data_variable');                     set_var = _alias('data_setvariableto')
change_var = _alias('data_changevariableby');      show_var = _alias('data_showvariable')
hide_var = _alias('data_hidevariable');            list_add = _alias('data_addtolist')
list_delete = _alias('data_deleteoflist');         list_clear = _alias('data_deletealloflist')
list_insert = _alias('data_insertatlist');         list_replace = _alias('data_replaceitemoflist')
list_item = _alias('data_itemoflist');             list_index = _alias('data_itemnumoflist')
list_length = _alias('data_lengthoflist');         list_has = _alias('data_listcontainsitem')
show_list = _alias('data_showlist');               hide_list = _alias('data_hidelist')


def timer_gt(seconds):
    return Node('event_whengreaterthan', 'TIMER', seconds)


def join(*parts):
    """Nest Scratch «join» blocks so that any number of pieces becomes one text."""
    if len(parts) == 1:
        return parts[0]
    return Node('operator_join', parts[0], join(*parts[1:]))


def literal(value):
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


class Target:
    def __init__(self, game, name, costumes, *, stage=False, sounds=(), x=0, y=0, size=100, direction=90,
                 visible=True, rotation_style='all around', note=''):
        self.game, self.name, self.is_stage = game, name, stage
        self.costumes, self.sounds = list(costumes), list(sounds)
        self.x, self.y, self.size, self.direction = x, y, size, direction
        self.visible, self.rotation_style, self.note = visible, rotation_style, note
        self.scripts, self.locals, self.blocks, self._count = [], {}, {}, 0

    def when(self, hat, *body):
        if hat.op not in HATS:
            raise ValueError(f'{self.name}: a script must start with a hat block, got {hat.op}')
        self.scripts.append([hat, *body])
        return self

    def local(self, name, value=0):
        """A «for this sprite only» variable: every clone gets its own copy."""
        self.locals[name] = (f'local-{len(self.game.targets)}-{len(self.locals) + 1}', value)

    # ── serialisation ──
    def _id(self):
        self._count += 1
        return f'{self.game.prefix}{len(self.game.targets_done)}b{self._count}'

    def _variable(self, name):
        if name in self.locals:
            return [name, self.locals[name][0]]
        if name not in self.game.variables:
            raise KeyError(f'{self.name}: unknown variable «{name}»')
        return [name, self.game.variables[name]['id']]

    def _list(self, name):
        if name not in self.game.lists:
            raise KeyError(f'{self.name}: unknown list «{name}»')
        return [name, self.game.lists[name]['id']]

    def _stack(self, nodes, parent, top=False, x=0, y=0):
        first = prev = None
        for node in nodes:
            if node.op in HATS and not (top and prev is None):
                raise ValueError(f'{self.name}: hat block {node.op} inside a script')
            bid = self._block(node, prev or parent, top and prev is None, x, y)
            if prev:
                self.blocks[prev]['next'] = bid
            first, prev = first or bid, bid
        return first

    def _block(self, node, parent, top=False, x=0, y=0):
        bid = self._id()
        block = {'opcode': node.op, 'next': None, 'parent': parent, 'inputs': {}, 'fields': {},
                 'shadow': False, 'topLevel': top}
        if top:
            block['x'], block['y'] = x, y
        self.blocks[bid] = block
        for (name, kind), value in zip(SPEC[node.op], node.args):
            if kind == FIELD:
                allowed = FIELD_VALUES.get((node.op, name))
                if allowed is not None and value not in allowed:
                    raise ValueError(f'{self.name}: {node.op}.{name} cannot be {value!r}')
                if node.op == 'event_whenbackdropswitchesto':
                    self.game.need('backdrop', value, self.name)
                block['fields'][name] = [value, None]
            elif kind == VAR:
                block['fields'][name] = self._variable(value)
            elif kind == LIST:
                block['fields'][name] = self._list(value)
            elif kind == BFIELD:
                block['fields'][name] = [value, self.game.broadcast_id(value)]
            elif kind == BCAST:
                block['inputs'][name] = [1, [11, value, self.game.broadcast_id(value)]]
            elif kind == BOOL:
                if value is not None:
                    block['inputs'][name] = [2, self._block(value, bid)]
            elif kind == STACK:
                if value:
                    block['inputs'][name] = [2, self._stack(value, bid)]
            elif isinstance(kind, tuple):          # dropdown that lives in its own shadow block
                _, menu_op, menu_field = kind
                self.game.need(menu_op, value, self.name)
                shadow_id = self._id()
                self.blocks[shadow_id] = {'opcode': menu_op, 'next': None, 'parent': bid, 'inputs': {},
                                          'fields': {menu_field: [value, None]}, 'shadow': True, 'topLevel': False}
                block['inputs'][name] = [1, shadow_id]
            else:                                   # number / text slot
                default = [kind, {TEXT: '', COLOR: '#000000'}.get(kind, '0')]
                if isinstance(value, Node) and value.op == 'data_variable':
                    block['inputs'][name] = [3, [12, *self._variable(value.args[0])], default]
                elif isinstance(value, Node):
                    block['inputs'][name] = [3, self._block(value, bid), default]
                else:
                    block['inputs'][name] = [1, [kind, literal(value)]]
        if node.op == 'control_stop':
            has_next = 'true' if node.args[0] == 'other scripts in sprite' else 'false'
            block['mutation'] = {'tagName': 'mutation', 'children': [], 'hasnext': has_next}
        return bid

    def build_blocks(self):
        """Lay scripts out in one tidy column below the «V Labs» note (like Scratch's own «Clean up Blocks»)."""
        y = 230
        for script in self.scripts:
            self._stack(script, None, top=True, x=40, y=y)
            y += script_height(script) + 40
        return self.blocks

    def comment(self):
        lesson = self.game.lesson
        text = (f'{BRAND} · Урок {lesson}. {self.game.topic}\nИгра «{self.game.title}» — {self.name}\n'
                f'{self.note}').strip()
        return {f'{self.game.prefix}note{len(self.game.targets_done)}':
                {'blockId': None, 'x': 40, 'y': 30, 'width': 460, 'height': 160, 'minimized': False, 'text': text}}


def script_height(nodes):
    """Generous pixel height of a stack, used only to keep scripts from overlapping in the editor."""
    total = 0
    for node in nodes:
        total += 72 if node.op in HATS else 56
        for (_, kind), value in zip(SPEC[node.op], node.args):
            if kind == STACK:
                total += max(script_height(value), 32) + 36
    return total


class Game:
    def __init__(self, stem, lesson, topic, title):
        self.stem, self.lesson, self.topic, self.title = stem, lesson, topic, title
        self.prefix = f'g{lesson}'
        self.targets, self.targets_done = [], []
        self.variables, self.lists, self.broadcasts, self.needs = {}, {}, {}, []

    def variable(self, name, value=0, show=None):
        self.variables[name] = {'id': f'{self.prefix}var{len(self.variables) + 1}', 'value': value, 'show': show}

    def list(self, name, show=None):
        self.lists[name] = {'id': f'{self.prefix}list{len(self.lists) + 1}', 'show': show}

    def broadcast_id(self, name):
        return self.broadcasts.setdefault(name, f'{self.prefix}msg{len(self.broadcasts) + 1}')

    def need(self, kind, value, owner):
        self.needs.append((kind, value, owner))

    def stage(self, backdrops, **kw):
        target = Target(self, 'Stage', backdrops, stage=True, **kw)
        self.targets.insert(0, target)
        return target

    def sprite(self, name, costumes, **kw):
        target = Target(self, name, costumes, **kw)
        self.targets.append(target)
        return target

    def add_badge(self):
        """Every project is marked with the «V Labs» badge in the top-right corner of the stage."""
        badge = self.sprite(BRAND, [costume(BRAND, badge_svg(), 64, 20)], x=168, y=154, rotation_style="don't rotate",
                            note='Знак лаборатории V Labs. Он всегда остаётся поверх сцены.')
        badge.when(flag(), goto_xy(168, 154), size_to(100), fx_clear(), show(), layer('front'))
        badge.when(clicked(), say_for(f'{BRAND}: урок {self.lesson} — «{self.topic}».', 2))
        return badge

    # ── serialisation ──
    def project(self):
        assets = {}

        def asset(item):
            digest = hashlib.md5(item['data']).hexdigest()
            md5ext = f'{digest}.{item["ext"]}'
            assets[md5ext] = item['data']
            if item['kind'] == 'sound':
                return {'name': item['name'], 'assetId': digest, 'dataFormat': 'wav', 'format': '',
                        'rate': item['rate'], 'sampleCount': item['count'], 'md5ext': md5ext}
            return {'name': item['name'], 'assetId': digest, 'md5ext': md5ext, 'dataFormat': 'svg',
                    'bitmapResolution': 1, 'rotationCenterX': item['cx'], 'rotationCenterY': item['cy']}

        targets = []
        for order, target in enumerate(self.targets):
            blocks = target.build_blocks()
            data = {
                'isStage': target.is_stage, 'name': target.name,
                'variables': {vid: [name, value] for name, (vid, value) in target.locals.items()},
                'lists': {}, 'broadcasts': {}, 'blocks': blocks,
                'comments': target.comment(),
                'currentCostume': 0, 'costumes': [asset(c) for c in target.costumes],
                'sounds': [asset(s) for s in target.sounds], 'volume': 100, 'layerOrder': order,
            }
            if target.is_stage:
                data.update({'tempo': 60, 'videoTransparency': 50, 'videoState': 'on', 'textToSpeechLanguage': None})
            else:
                data.update({'visible': target.visible, 'x': target.x, 'y': target.y, 'size': target.size,
                             'direction': target.direction, 'draggable': False,
                             'rotationStyle': target.rotation_style})
            targets.append(data)
            self.targets_done.append(target)
        stage = targets[0]
        stage['variables'].update({v['id']: [name, v['value']] for name, v in self.variables.items()})
        stage['lists'] = {l['id']: [name, []] for name, l in self.lists.items()}
        stage['broadcasts'] = {bid: name for name, bid in self.broadcasts.items()}
        monitors = []
        for name, v in self.variables.items():
            if v['show']:
                monitors.append({'id': v['id'], 'mode': 'default', 'opcode': 'data_variable',
                                 'params': {'VARIABLE': name}, 'spriteName': None, 'value': v['value'],
                                 'width': 0, 'height': 0, 'x': v['show'][0], 'y': v['show'][1], 'visible': True,
                                 'sliderMin': 0, 'sliderMax': 100, 'isDiscrete': True})
        for name, l in self.lists.items():
            if l['show']:
                x, y, width, height = l['show']
                monitors.append({'id': l['id'], 'mode': 'list', 'opcode': 'data_listcontents',
                                 'params': {'LIST': name}, 'spriteName': None, 'value': [],
                                 'width': width, 'height': height, 'x': x, 'y': y, 'visible': True})
        project = {'targets': targets, 'monitors': monitors, 'extensions': [],
                   'meta': {'semver': '3.0.0', 'vm': '0.2.0', 'agent': f'{BRAND} lesson game builder'}}
        self.validate(project)
        return project, assets

    def validate(self, project):
        """Catch broken references before Scratch does: every name used in a dropdown must exist."""
        names = {t['name'] for t in project['targets'] if not t['isStage']}
        by_name = {t['name']: t for t in project['targets']}
        stage = project['targets'][0]
        special = {'_mouse_', '_random_', '_edge_', '_myself_', '_stage_'}
        for kind, value, owner in self.needs:
            target = by_name[owner]
            if kind in ('backdrop', 'looks_backdrops'):
                ok = value in {c['name'] for c in stage['costumes']}
            elif kind == 'looks_costume':
                ok = value in {c['name'] for c in target['costumes']}
            elif kind == 'sound_sounds_menu':
                ok = value in {s['name'] for s in target['sounds']}
            elif kind == 'sensing_keyoptions':
                ok = value in KEYS
            else:
                ok = value in names or value in special
            if not ok:
                raise ValueError(f'{self.stem}: {owner} refers to missing {kind} «{value}»')
        sent = {b['inputs']['BROADCAST_INPUT'][1][1] for t in project['targets'] for b in t['blocks'].values()
                if b['opcode'].startswith('event_broadcast')}
        heard = {b['fields']['BROADCAST_OPTION'][0] for t in project['targets'] for b in t['blocks'].values()
                 if b['opcode'] == 'event_whenbroadcastreceived'}
        if sent != heard:
            raise ValueError(f'{self.stem}: broadcasts sent {sorted(sent)} but received {sorted(heard)}')
        for target in project['targets']:
            blocks = target['blocks']
            for bid, block in blocks.items():
                if block['topLevel'] != (block['parent'] is None):
                    raise ValueError(f'{self.stem}: {bid} has a wrong parent')
                if block['next'] and blocks[block['next']]['parent'] != bid:
                    raise ValueError(f'{self.stem}: {bid} has a broken chain')
                for value in block['inputs'].values():
                    if isinstance(value[1], str) and blocks[value[1]]['parent'] != bid:
                        raise ValueError(f'{self.stem}: {bid} has a detached input')

    def stats(self, project):
        counts = {}
        for target in project['targets']:
            for block in target['blocks'].values():
                if not block['shadow']:
                    category = block['opcode'].split('_')[0]
                    counts[category] = counts.get(category, 0) + 1
        return counts


# ───────────────────────────── The eight games ─────────────────────────────

def game_events():
    g = Game('01-events', 1, 'События', 'Солнце и дождь')
    g.variable('Событий', 0, show=(5, 5))
    g.variable('Нажатий', 0, show=(5, 32))
    stage = g.stage([backdrop('Солнечно', events_backdrop('sunny')), backdrop('Дождливо', events_backdrop('rainy')),
                     backdrop('Радуга', events_backdrop('rainbow'))],
                    note='Сцена слушает сообщения и меняет погоду. Клик по небу тоже событие!')
    stage.when(flag(), set_backdrop('Солнечно'), fx_clear(), set_var('Событий', 0), set_var('Нажатий', 0))
    for message, scene in [('Дождь', 'Дождливо'), ('Радуга', 'Радуга'), ('Солнце', 'Солнечно')]:
        stage.when(receive(message), set_backdrop(scene), change_var('Событий', 1))
    stage.when(receive('Ветер'), change_var('Событий', 1))
    stage.when(receive('Гром'), change_var('Событий', 1),
               repeat(2, [fx_to('BRIGHTNESS', 60), wait(0.12), fx_clear(), wait(0.12)]))
    stage.when(stage_clicked(), broadcast('Солнце'))
    stage.when(key('any'), change_var('Нажатий', 1))

    sun = g.sprite('Солнце', [costume('Солнце', sprite_svg('sun'))], x=-158, y=60,
                   note='Пробел — радуга, 1 — солнце, клик по солнцу — ясная погода, ↑ ↓ — восход и закат.\n'
                        'Через 20 секунд сработает событие таймера.')
    sun.when(flag(), show(), goto_xy(-158, 60),
             say_for('Клик по облаку — дождь, пробел — радуга!', 3),
             say_for('Ещё события: клавиши 1, 2, 3, 4, стрелки ↑ ↓ и клик по небу.', 3))
    sun.when(key('up arrow'), dy(10))
    sun.when(key('down arrow'), dy(-10))
    sun.when(receive('Ветер'), think_for('Ветер гонит облако!', 2))
    sun.when(key('space'), broadcast('Радуга'))
    sun.when(key('1'), broadcast('Солнце'))
    sun.when(clicked(), broadcast('Солнце'), say_for('Солнце снова выглянуло!', 2))
    sun.when(receive('Дождь'), hide())
    sun.when(receive('Солнце'), show())
    sun.when(receive('Радуга'), show(), think_for('После дождя бывает радуга!', 2))
    sun.when(timer_gt(20), show(), say_for('Событие таймера: прошло 20 секунд!', 2), broadcast('Радуга'))

    cloud = g.sprite('Облако', [costume('Облачко', CLOUD, 60, 45)], x=135, y=58, rotation_style="don't rotate",
                     note='Клик по облаку или клавиша 2 — дождь, 4 — ветер. Клавиша 3 — гром:\n'
                          'облако ждёт, пока все получат сообщение.')
    cloud.when(flag(), show(), goto_xy(135, 58), say_for('Кликни по мне!', 2))
    cloud.when(clicked(), broadcast('Дождь'), say_for('Кап-кап! Я отправило сообщение «Дождь».', 2))
    cloud.when(key('2'), broadcast('Дождь'), think_for('Клавиша 2 — тоже событие.', 1.5))
    cloud.when(key('3'), say_for('Сейчас грянет гром…', 1), broadcast_wait('Гром'),
               say_for('Гром отгремел: сообщение доставлено!', 2))
    cloud.when(receive('Гром'), repeat(3, [dx(6), wait(0.05), dx(-12), wait(0.05), dx(6)]))
    cloud.when(key('4'), broadcast('Ветер'))
    cloud.when(receive('Ветер'), glide_xy(1, -40, 58), glide_xy(1, 135, 58))
    cloud.when(receive('Солнце'), think_for('Тучи разошлись.', 1.5))
    cloud.when(backdrop_is('Радуга'), think_for('Событие «фон сменился»: радуга!', 2))
    cloud.when(backdrop_is('Дождливо'), think_for('Событие «фон сменился»: дождь.', 2))

    drop = g.sprite('Капля', [costume('Капля', DROP, 24, 28)], x=0, y=150, size=60, visible=False,
                    rotation_style="don't rotate",
                    note='Капля появляется по сообщению «Дождь» и прячется по сообщениям «Солнце» и «Радуга».')
    drop.when(flag(), hide())
    drop.when(receive('Дождь'), show(),
              repeat(12, [goto_xy(rnd(-220, 220), 150), repeat(10, [dy(-22)])]), hide())
    drop.when(receive('Солнце'), stop('other scripts in sprite'), hide())
    drop.when(receive('Радуга'), stop('other scripts in sprite'), hide())
    drop.when(clicked(), broadcast('Радуга'))
    g.add_badge()
    return g


def game_motion():
    g = Game('02-motion', 2, 'Движение', 'Космический маршрут')
    g.variable('Маяки', 0, show=(5, 5))
    g.stage([backdrop('Космос', scene_svg(['#101b46', '#382c78'], SCENES['motion']))])
    start = (-180, -110)
    rocket = g.sprite('Ракета', [costume('Ракета', sprite_svg('rocket'))], x=start[0], y=start[1], size=60,
                      note='Стрелки — полёт. Пробел — гиперпрыжок, 1 — курс на маяк, 2 — сальто,\n'
                           '3 — координаты, 4 — плавно на старт, 5 — разворот, 6 — змейка,\n'
                           '7 — плавно к мыши, 8 — рывок к мыши, 9 — круг, 0 — в центр.')
    steer = [if_(key_down(name), [point(angle), move(6)])
             for name, angle in [('up arrow', 0), ('down arrow', 180), ('right arrow', 90), ('left arrow', -90)]]
    rocket.when(flag(), rotation('all around'), goto_xy(*start), point(90), set_var('Маяки', 0),
                forever(steer + [
                    bounce(),
                    if_(touching('Астероид'), [broadcast('Столкновение'), goto_xy(*start), point(90)]),
                ]))
    rocket.when(flag(), say_for('Лети стрелками к маяку и берегись астероида!', 4))
    rocket.when(receive('Маяк пойман'), say_for(join('Маяков собрано: ', var('Маяки')), 2))
    rocket.when(receive('Столкновение'), say_for('Ой, астероид! Возвращаюсь на старт.', 2))
    rocket.when(key('space'), goto('_random_'), say_for('Гиперпрыжок!', 1))
    rocket.when(key('1'), point_to('Маяк'), say_for('Курс на маяк!', 1))
    rocket.when(key('2'), repeat(12, [right(30)]))
    rocket.when(key('3'), say_for(join('x: ', round_(x_pos()), '   y: ', round_(y_pos())), 2))
    rocket.when(key('4'), glide_xy(1, *start), point(90))
    rocket.when(key('5'), left(180), say_for(join('Направление: ', direction()), 1))
    rocket.when(key('6'), repeat(4, [dx(15), dy(15), dx(15), dy(-15)]))
    rocket.when(key('7'), point_to('_mouse_'), glide_to(1, '_mouse_'))
    rocket.when(key('8'), point_to('_mouse_'), move(40))
    rocket.when(key('9'), repeat(36, [move(8), right(10)]))
    rocket.when(key('0'), set_x(0), set_y(0), point(90))

    beacon = g.sprite('Маяк', [costume('Маяк', sprite_svg('beacon'))], x=160, y=-40, size=80,
                      rotation_style="don't rotate",
                      note='Маяк покачивается и перелетает в случайное место, когда ракета его коснётся.')
    beacon.when(flag(), goto_xy(160, -40), forever([repeat(8, [dy(1)]), repeat(8, [dy(-1)])]))
    beacon.when(flag(), forever([
        if_(touching('Ракета'), [change_var('Маяки', 1), broadcast('Маяк пойман'),
                                 goto_xy(rnd(-200, 200), rnd(-130, 100))])]))

    asteroid = g.sprite('Астероид', [costume('Астероид', sprite_svg('asteroid'))], x=150, y=110, size=55,
                        note='Астероид плавно скользит между случайными точками и вращается.')
    asteroid.when(flag(), goto_xy(150, 110), forever([glide_to(rnd(2, 4), '_random_')]))
    asteroid.when(flag(), forever([right(5)]))
    g.add_badge()
    return g


def game_looks():
    g = Game('03-looks', 3, 'Внешность', 'Театр настроений')
    stage = g.stage([backdrop('Красный занавес', theatre_backdrop('#a83e72', '#e77c9f')),
                     backdrop('Синий занавес', theatre_backdrop('#3a4fa8', '#7c9be7')),
                     backdrop('Зелёный занавес', theatre_backdrop('#2f8a6b', '#7ce0b5'))],
                    note='Клик по сцене меняет декорацию.')
    stage.when(stage_clicked(), next_backdrop())

    light = g.sprite('Прожектор', [costume('Свет', svg(120, 120, SPRITES['spotlight']), 60, 60)], x=0, y=-40,
                     size=150, note='Прожектор светит из-за спины артиста и переливается цветом.')
    light.when(flag(), goto_xy(0, -40), size_to(150), fx_clear(), fx_to('GHOST', 35), show(), layer('back'),
               forever([fx_by('COLOR', 3), wait(0.1)]))
    light.when(clicked(), size_by(25), wait(0.3), size_by(-25))

    hero = g.sprite('Артист', [costume(name, mood_svg(name)) for name in MOODS], x=0, y=-45, size=120,
                    note='Клик — следующий костюм. 1–4 — настроение, стрелки — размер и цвет,\n'
                         '5 — исчезновение, 6 — декорация, 7 — спецэффекты, 8/9 — слои, пробел — сброс.')
    hero.when(flag(), set_costume('Радость'), set_backdrop('Красный занавес'), size_to(120), fx_clear(), show(),
              layer('front'), layers('backward', 1), goto_xy(0, -45),
              say_for('Добро пожаловать в Театр настроений!', 2),
              think_for('Кликни по мне или нажми 1, 2, 3, 4…', 3))
    hero.when(clicked(), next_costume(), say_for(join('Мой костюм: ', costume_info('name')), 2))
    for number, (mood, phrase) in enumerate([('Радость', 'Ура! Я радуюсь!'), ('Грусть', 'Эх… Мне грустно.'),
                                             ('Удивление', 'Ого! Вот это да!'), ('Спокойствие', 'Тс-с… Я спокоен.')], 1):
        hero.when(key(str(number)), set_costume(mood), say_for(phrase, 2))
    # No «for N seconds» here: a key script must finish at once to react to the next key press.
    hero.when(key('up arrow'), size_by(10), think(join('Размер: ', round_(size()))))
    hero.when(key('down arrow'), size_by(-10), think(join('Размер: ', round_(size()))))
    hero.when(key('right arrow'), fx_by('COLOR', 25))
    hero.when(key('left arrow'), fx_by('COLOR', -25))
    hero.when(key('space'), fx_clear(), size_to(120), show(), say_for('Сброс: я снова как новый!', 1.5))
    hero.when(key('5'), repeat(10, [fx_by('GHOST', 10)]), hide(), wait(0.5), show(),
              repeat(10, [fx_by('GHOST', -10)]))
    hero.when(key('6'), next_backdrop())
    hero.when(key('7'), fx_to('PIXELATE', 25), wait(0.6), fx_to('PIXELATE', 0), fx_to('WHIRL', 150), wait(0.6),
              fx_to('WHIRL', 0))
    hero.when(key('8'), layer('back'), think_for('Я спрятался за прожектор.', 1.5))
    hero.when(key('9'), layer('front'), layers('backward', 1), think_for('Я снова впереди!', 1.5))
    hero.when(backdrop_is('Синий занавес'), set_costume('Грусть'),
              say_for(join('Декорация № ', backdrop_info('number'), ': грустная сцена.'), 2))
    hero.when(backdrop_is('Зелёный занавес'), set_costume('Спокойствие'),
              say_for(join('Декорация № ', backdrop_info('number'), ': спокойная сцена.'), 2))
    g.add_badge()
    return g


def game_sound():
    g = Game('04-sound', 4, 'Звук', 'Музыкальный инструмент')
    g.variable('Громкость', 80, show=(5, 5))
    g.variable('Высота', 0, show=(5, 32))
    g.variable('Мелодия', 'тишина', show=(5, 59))
    MUSIC, MARCH, CANTINA, THEME = 'Музыка', 'Имперский марш', 'Cantina Band', 'Главная тема'
    drum = drum_sound()
    stage = g.stage([backdrop('Студия', scene_svg(['#102d47', '#167d87'], SCENES['sound']))], sounds=[drum],
                    note='Клик по сцене — удар барабана.')
    stage.when(stage_clicked(), play('Барабан'))

    notes = [note_sound(name, freq) for name, freq in NOTES]
    synth = g.sprite('Синтезатор', [costume('Синтезатор', sprite_svg('synth'))], sounds=notes,
                     x=-60, y=-95, size=100,
                     note='1–8 — ноты, 9 — барабан, 0 — следующая мелодия из «Звёздных войн».\n'
                          '↑ ↓ — громкость, ← → — высота звука (меняют и мелодии), пробел — тишина,\n'
                          'клик по синтезатору — стерео.')
    synth.when(flag(), vol_to(80), sfx_clear(), fx_clear(), size_to(100), set_var('Громкость', volume()),
               set_var('Высота', 0), set_var('Мелодия', 'тишина'),
               say_for('Клавиши 1–8 — ноты, 9 — барабан, пробел — тишина.', 3),
               say_for('Кнопки справа и клавиша 0 играют музыку из «Звёздных войн».', 3),
               say_for('Стрелки меняют громкость и высоту звука.', 3))
    synth.when(flag(), play_wait('До'), play_wait('Ми'), play_wait('Соль'), play('До высокая'))
    for number, (name, _) in enumerate(NOTES, 1):
        synth.when(key(str(number)), play(name), fx_to('COLOR', number * 22), say(name))
    # «0» switches to the next tune: the buttons listen to «Музыка» and check the variable «Мелодия».
    synth.when(key('0'),
               if_else(eq(var('Мелодия'), MARCH), [set_var('Мелодия', CANTINA)],
                       [if_else(eq(var('Мелодия'), CANTINA), [set_var('Мелодия', THEME)],
                                [set_var('Мелодия', MARCH)])]),
               broadcast(MUSIC))
    synth.when(key('up arrow'), vol_by(10), set_var('Громкость', volume()))
    synth.when(key('down arrow'), vol_by(-10), set_var('Громкость', volume()))
    synth.when(key('right arrow'), if_(lt(var('Высота'), 360), [change_var('Высота', 10)]),
               sfx_to('PITCH', var('Высота')))
    synth.when(key('left arrow'), if_(gt(var('Высота'), -360), [change_var('Высота', -10)]),
               sfx_to('PITCH', var('Высота')))
    synth.when(key('space'), set_var('Мелодия', 'тишина'), broadcast(MUSIC), stop_sounds(), sfx_clear(),
               set_var('Высота', 0), say_for('Тишина…', 1))
    synth.when(clicked(), sfx_to('PAN', -100), say('Звук слева…'), play_wait('До'),
               sfx_to('PAN', 100), say('…и справа!'), play_wait('Соль'), sfx_to('PAN', 0), say(''))

    drums = g.sprite('Барабан', [costume('Барабан', DRUM)], sounds=[drum], x=95, y=-100,
                     size=85, rotation_style="don't rotate",
                     note='Клик — удар со случайной высотой звука. Клавиша 9 — ритм из четырёх ударов.')
    drums.when(flag(), vol_to(90), sfx_clear(), size_to(85))
    drums.when(clicked(), sfx_to('PITCH', rnd(-60, 60)), play('Барабан'), size_by(12), wait(0.1), size_by(-12))
    drums.when(key('9'), sfx_clear(),
               repeat(4, [play_wait('Барабан'), size_by(10), wait(0.12), size_by(-10)]),
               sfx_to('PITCH', 120), play_wait('Барабан'), sfx_clear())
    drums.when(key('up arrow'), vol_by(10))
    drums.when(key('down arrow'), vol_by(-10))
    drums.when(key('space'), stop_sounds(), sfx_clear())

    # ── Three tunes from «Star Wars» (music by John Williams), short excerpts of the melody line ──
    def tune_button(name, y, art, tune, blocks, hint, rhythm):
        button = g.sprite(name, [costume(name, art)], sounds=tune.sounds(), x=196, y=y, size=60,
                          rotation_style="don't rotate",
                          note=f'Клик — «{name}» из «Звёздных войн» (музыка Джона Уильямса), отрывок.\n'
                               f'Каждая нота — «включить звук» и «ждать»: {rhythm}.\n'
                               'Поменяй числа — изменится ритм, поменяй звуки — получится своя мелодия.')
        button.when(flag(), goto_xy(196, y), size_to(60), show(),
                    forever([vol_to(var('Громкость')), sfx_to('PITCH', var('Высота'))]))
        pause = [wait((78 - y) / 30)] if y != 78 else []
        button.when(flag(), *pause, say_for(name, 2))                   # the buttons introduce themselves in turn
        button.when(clicked(), set_var('Мелодия', name), broadcast(MUSIC), say_for(hint, 2))
        # The message restarts this script in every button, so only the chosen tune keeps playing.
        button.when(receive(MUSIC), size_to(60),
                    if_(eq(var('Мелодия'), name), [size_to(75), *blocks, size_to(60)]))
        return button

    march = Tune(0.56)
    tune_button(MARCH, 78, button_svg('#ff7b7b', '#8f1d2c', NOTE_ICON), march, march.bars(
        'G4:1 G4:1 G4:1 Eb4:.75 Bb4:.25',
        'G4:1 Eb4:.75 Bb4:.25 G4:2',
        'D5:1 D5:1 D5:1 Eb5:.75 Bb4:.25',
        'F#4:1 Eb4:.75 Bb4:.25 G4:2',
        'G5:1 G4:.75 G4:.25 G5:1 F#5:.75 F5:.25',
        'E5:.25 Eb5:.25 E5:.5 -:.5 G#4:.5 C#5:1 C5:.75 B4:.25',
        'Bb4:.25 A4:.25 Bb4:.5 -:.5 Eb4:.5 F#4:1 Eb4:.75 Bb4:.25',
        'G4:1 Eb4:.75 Bb4:.25 G4:2',
    ), 'Имперский марш — тема Дарта Вейдера', '0.56 с — четверть, 0.42 и 0.14 — пунктирный ритм марша')

    cantina = Tune(0.25)
    riff = ('A4:1 D5:1 A4:1 D5:1', 'A4:.5 D5:1 A4:.5 -:.5 G#4:.5 A4:1')
    tune_button(CANTINA, 18, button_svg('#ffd36b', '#c9661f', NOTES_ICON), cantina, cantina.bars(
        *riff, 'A4:.5 G#4:.5 A4:.5 G4:.5 -:.5 F#4:.5 G4:.5 F4:.5', 'F4:1 D4:3',
        *riff, 'G4:1.5 G4:1.5 F#4:.5 G4:.5', 'C5:.5 Bb4:1.5 A4:1 G4:1',
        *riff, 'C5:1 C5:1.5 A4:.5 G4:1', 'F4:1.5 D4:2.5',
    ), 'Cantina Band — весёлый оркестр из кантины', '0.25 с — четверть, 0.125 — восьмая, быстрый темп')

    theme = Tune(0.54)
    tune_button(THEME, -42, button_svg('#9cc9ff', '#1f3f8f', STAR_ICON), theme, [repeat(2, [
        *theme.part('F4:1/3 F4:1/3 F4:1/3', 1),
        *theme.part('Bb4:2 F5:2', 4),
        repeat(2, theme.part('Eb5:1/3 D5:1/3 C5:1/3 Bb5:2 F5:1', 4)),
        *theme.part('Eb5:1/3 D5:1/3 Eb5:1/3 C5:2', 3),
    ])], 'Главная тема «Звёздных войн»', '1.08 с — половинная нота, 0.18 — быстрая триоль')
    g.add_badge()
    return g


def game_control():
    g = Game('05-control', 5, 'Управление', 'Метеоритный дождь')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Жизни', 3, show=(5, 32))
    g.variable('Уровень', 1, show=(5, 59))
    stage = g.stage([backdrop('Ночное небо', scene_svg(['#111a3c', '#4c3068'], SCENES['control']))],
                    note='Сцена каждые 8 секунд повышает уровень: метеоры падают быстрее.\n'
                         'Когда остаётся одна жизнь, небо тревожно мигает.')
    stage.when(receive('Старт'),
               repeat_until(lt(var('Жизни'), 1), [wait(8), if_(lt(var('Уровень'), 6), [change_var('Уровень', 1)])]))
    stage.when(flag(), fx_clear())
    stage.when(receive('Старт'), forever([
        wait_until(eq(var('Жизни'), 1)),
        repeat_until(not_(eq(var('Жизни'), 1)), [fx_to('BRIGHTNESS', -25), wait(0.3), fx_clear(), wait(0.3)])]))

    ship = g.sprite('Корабль', [costume('Корабль', sprite_svg('ship'))], x=0, y=-125, size=80,
                    rotation_style="don't rotate",
                    note='Стрелки ← → — уклоняйся от метеоров и лови звёзды (+5). Метеор мимо — очко.\n'
                         'Пробел меняет 10 очков на жизнь. Жизней нет — игра окончена.')
    ship.when(flag(), set_var('Очки', 0), set_var('Жизни', 3), set_var('Уровень', 1), goto_xy(0, -125),
              size_to(80), show(),
              broadcast('Старт'),
              forever([
                  if_(key_down('right arrow'), [dx(8)]),
                  if_(key_down('left arrow'), [dx(-8)]),
                  if_else(gt(x_pos(), 215), [set_x(215)], [if_(lt(x_pos(), -215), [set_x(-215)])]),
              ]))
    ship.when(flag(), repeat(3, [size_by(10), wait(0.15), size_by(-10), wait(0.15)]),
              say_for('Стрелки ← → : уклоняйся от метеоров!', 2), say_for('Лови звёзды: +5 очков.', 2))
    ship.when(receive('Старт'), wait_until(lt(var('Жизни'), 1)),
              say_for(join('Игра окончена! Очки: ', var('Очки')), 3), stop('all'))
    ship.when(receive('Удар'), repeat(3, [hide(), wait(0.1), show(), wait(0.1)]))
    ship.when(key('space'),
              if_(lt(var('Очки'), 10), [say_for('Для бонуса нужно 10 очков.', 1), stop('this script')]),
              change_var('Очки', -10), change_var('Жизни', 1), say_for('Бонус: +1 жизнь!', 1))

    meteor = g.sprite('Метеор', [costume('Метеор', sprite_svg('meteor'))], x=0, y=170, size=55, visible=False,
                      rotation_style="don't rotate",
                      note='Сам метеор спрятан: цикл создаёт его клоны, пока есть жизни.\n'
                           'Каждый клон падает, проверяет столкновение и удаляется.')
    meteor.local('Скорость', 5)
    meteor.when(flag(), hide())
    meteor.when(receive('Старт'), wait(1),
                repeat_until(lt(var('Жизни'), 1), [clone('_myself_'), wait(rnd(0.4, 1.0))]))
    meteor.when(as_clone(), set_var('Скорость', add(rnd(3, 6), var('Уровень'))), goto_xy(rnd(-220, 220), 170),
                show(),
                repeat_until(or_(lt(y_pos(), -165), lt(var('Жизни'), 1)), [
                    dy(sub(0, var('Скорость'))),
                    if_(touching('Корабль'), [
                        if_(gt(var('Жизни'), 0), [change_var('Жизни', -1)]),
                        broadcast('Удар'), delete_clone()]),
                ]),
                if_(gt(var('Жизни'), 0), [change_var('Очки', 1)]),
                delete_clone())

    star = g.sprite('Звезда', [costume('Звезда', STAR, 32, 32)], x=0, y=170, size=70, visible=False,
                    note='Раз в несколько секунд цикл создаёт клон-звезду. Поймаешь — получишь 5 очков.')
    star.when(flag(), hide())
    star.when(receive('Старт'), forever([wait(rnd(4, 8)), clone('_myself_')]))
    star.when(as_clone(), goto_xy(rnd(-200, 200), 170), show(),
              repeat_until(lt(y_pos(), -165), [
                  dy(-4), right(6),
                  if_(touching('Корабль'), [change_var('Очки', 5), delete_clone()]),
              ]),
              delete_clone())
    g.add_badge()
    return g


def game_sensing():
    g = Game('06-sensing', 6, 'Сенсоры', 'Следопыт за мышью')
    g.variable('Подсказка', '…', show=(5, 5))
    g.variable('Найдено', 0, show=(5, 32))
    g.variable('Мышь x', 0, show=(5, 59))
    g.variable('Мышь y', 0, show=(5, 86))
    g.variable('Имя', '')
    stage = g.stage([backdrop('Радар', scene_svg(['#11384a', '#167b77'], SCENES['sensing']))],
                    note='Сцена всё время читает сенсоры мыши и показывает их в переменных «Мышь x» и «Мышь y».')
    stage.when(flag(), forever([set_var('Мышь x', mouse_x()), set_var('Мышь y', mouse_y())]))

    gem = g.sprite('Клад', [costume('Клад', sprite_svg('gem'))], x=120, y=40, size=70,
                   rotation_style="don't rotate",
                   note='Клад невидим (эффект «призрак»), но следопыт чувствует расстояние до него.')
    gem.when(flag(), show(), fx_to('GHOST', 100))
    gem.when(receive('Спрятать'), fx_to('GHOST', 100), goto_xy(rnd(-200, 200), rnd(-140, 100)))
    gem.when(receive('Клад найден'), fx_clear(), repeat(2, [size_by(15), wait(0.1), size_by(-15), wait(0.1)]))
    gem.when(clicked(), if_(lt(distance('Следопыт'), 60), [think_for(join('Меня нашёл следопыт ', answer()), 2)]))

    hero = g.sprite('Следопыт', [costume('Следопыт', sprite_svg('tracker'))], x=0, y=0, size=70,
                    note='Веди следопыта мышью: подсказка «горячо/холодно» зависит от расстояния до клада.\n'
                         'Кнопка мыши — радар. Пробел и 1–9 — показания сенсоров, 0 — перетаскивание.\n'
                         '↑ ↓ — размер, ← → — цвет. Жёлтый центр радара следопыт узнаёт по цвету.')
    hero.when(flag(), drag_mode('not draggable'), set_var('Найдено', 0), set_var('Подсказка', '…'),
              size_to(70), fx_clear(), goto_xy(0, 0),
              ask('Как тебя зовут, следопыт?'), set_var('Имя', answer()),
              say_for(join('Привет, ', answer(), '! Веди меня мышкой к кладу.'), 3),
              broadcast_wait('Спрятать'), reset_timer(),
              forever([
                  point_to('_mouse_'),
                  if_(not_(touching('_mouse_')), [move(div(distance('_mouse_'), 6))]),
                  if_else(lt(distance('Клад'), 45), [set_var('Подсказка', 'Горячо!')], [
                      if_else(lt(distance('Клад'), 130), [set_var('Подсказка', 'Тепло')],
                              [set_var('Подсказка', 'Холодно')])]),
                  if_(touching('Клад'), [
                      change_var('Найдено', 1), broadcast_wait('Клад найден'),
                      say_for(join('Клад найден! Секунд: ', round_(timer())), 2),
                      broadcast_wait('Спрятать'), reset_timer()]),
              ]))
    hero.when(flag(), forever([
        if_(mouse_down(), [think_for(join('Радар: до клада ', round_(distance('Клад'))), 1)]),
        if_(touching('_edge_'), [think_for('Это край сцены!', 1)]),
        if_(key_down('up arrow'), [size_by(2)]),
        if_(key_down('down arrow'), [size_by(-2)]),
        if_(key_down('right arrow'), [fx_by('COLOR', 5)]),
        if_(key_down('left arrow'), [fx_by('COLOR', -5)]),
        if_(touching_color('#fff0a0'), [think_for('Я в жёлтом центре радара!', 1)]),
    ]))
    hero.when(key('space'), say_for(join('Мышь: x = ', mouse_x(), ', y = ', mouse_y()), 2))
    hero.when(key('1'), say_for(join('Сейчас ', current('HOUR'), ' ч ', current('MINUTE'), ' мин'), 2))
    hero.when(key('2'), say_for(join('Подсказка: клад по x = ', prop_of('x position', 'Клад')), 2))
    hero.when(key('3'), say_for(join('С 2000 года прошло дней: ', round_(days2000())), 2))
    hero.when(key('4'), say_for(join('До указателя мыши: ', round_(distance('_mouse_'))), 2))
    hero.when(key('5'), say_for(join('Сегодня ', current('DATE'), '.', current('MONTH'), '.', current('YEAR')), 2))
    hero.when(key('6'), say_for(join('День недели № ', current('DAYOFWEEK'), ', секунда ', current('SECOND')), 2))
    hero.when(key('7'), say_for(join('Таймер поиска, секунд: ', round_(timer())), 2))
    hero.when(key('8'), reset_timer(), say_for('Таймер сброшен!', 1))
    hero.when(key('9'), say_for(join('Мой размер: ', prop_of('size', 'Следопыт'), ', клад по y = ',
                                     prop_of('y position', 'Клад')), 2))
    hero.when(key('0'), drag_mode('draggable'), say_for('Теперь меня можно перетаскивать мышью.', 2))
    hero.when(clicked(), say_for(join('Меня ведёт следопыт ', var('Имя')), 2))
    g.add_badge()
    return g


def game_operators():
    g = Game('07-operators', 7, 'Операторы', 'Математический оракул')
    g.variable('Очки', 0, show=(5, 5))
    g.variable('Вопрос', 0, show=(5, 32))
    for name in ('А', 'Б', 'Знак', 'Правильно'):
        g.variable(name, 0)
    g.stage([backdrop('Зал оракула', scene_svg(['#33234f', '#7550a1'], SCENES['operators']))])

    def question(sign):
        return ask(join(var('А'), f' {sign} ', var('Б'), ' = ?'))

    oracle = g.sprite('Оракул', [costume('Оракул', sprite_svg('oracle'))], x=-70, y=-30, size=110,
                      note='Флаг — пять случайных примеров на +, −, × и :.\n'
                           'Клик по оракулу — он расскажет всё о твоём числе.')
    oracle.when(flag(), set_var('Очки', 0), set_var('Вопрос', 0),
                say_for('Я математический оракул! Реши 5 примеров.', 2),
                repeat(5, [
                    change_var('Вопрос', 1),
                    set_var('А', rnd(2, 9)), set_var('Б', rnd(2, 9)), set_var('Знак', rnd(1, 4)),
                    if_(eq(var('Знак'), 1), [set_var('Правильно', add(var('А'), var('Б'))), question('+')]),
                    if_(eq(var('Знак'), 2), [set_var('А', add(var('А'), var('Б'))),
                                             set_var('Правильно', sub(var('А'), var('Б'))), question('−')]),
                    if_(eq(var('Знак'), 3), [set_var('Правильно', mul(var('А'), var('Б'))), question('×')]),
                    if_(eq(var('Знак'), 4), [set_var('А', mul(var('А'), var('Б'))),
                                             set_var('Правильно', div(var('А'), var('Б'))), question(':')]),
                    if_else(eq(answer(), var('Правильно')),
                            [change_var('Очки', 1), say_for('Верно!', 1)],
                            [if_else(gt(answer(), var('Правильно')),
                                     [say_for(join('Многовато. Правильно: ', var('Правильно')), 2)],
                                     [say_for(join('Маловато. Правильно: ', var('Правильно')), 2)])]),
                ]),
                say_for(join('Результат: ', var('Очки'), ' из 5.'), 2),
                if_(eq(var('Очки'), 5), [say_for('Ты настоящий оракул!', 2)]),
                if_(or_(eq(var('Очки'), 3), eq(var('Очки'), 4)), [say_for('Хороший счёт!', 2)]),
                if_(lt(var('Очки'), 3), [say_for('Потренируйся ещё: нажми флаг.', 2)]),
                if_(not_(eq(var('Очки'), 5)), [think_for('Кликни по мне — расскажу о любом числе.', 3)]))
    oracle.when(clicked(), ask('Напиши любое целое число:'),
                if_(not_(eq(add(answer(), 0), answer())), [say_for('Это не число! Кликни ещё раз.', 2),
                                                          stop('this script')]),
                if_else(eq(mod(answer(), 2), 0), [say_for(join(answer(), ' — чётное число.'), 2)],
                        [say_for(join(answer(), ' — нечётное число.'), 2)]),
                say_for(join('Знаков в записи: ', length(answer()), ', первый: ', letter(1, answer())), 2),
                if_(contains(answer(), '7'), [say_for('В нём есть счастливая семёрка!', 2)]),
                if_(and_(gt(answer(), 9), lt(answer(), 100)), [say_for('Это двузначное число.', 2)]),
                say_for(join('Его модуль: ', mathop('abs', answer()),
                             ', половина ≈ ', round_(div(answer(), 2))), 2),
                say_for(join('Корень из модуля ≈ ',
                             div(round_(mul(mathop('sqrt', mathop('abs', answer())), 100)), 100)), 2))
    g.add_badge()
    return g


def game_data():
    g = Game('08-data', 8, 'Данные', 'Дневник желаний')
    wishes = 'Мои желания'
    g.variable('Счётчик', 0, show=(5, 5))
    g.variable('Номер', 0)
    g.list(wishes, show=(5, 34, 215, 190))
    g.stage([backdrop('Страница', scene_svg(['#203650', '#278b80'], SCENES['data']))])

    count = [set_var('Счётчик', list_length(wishes))]
    diary = g.sprite('Дневник', [costume('Дневник', sprite_svg('diary'))], x=150, y=-95, size=95,
                     rotation_style="don't rotate",
                     note='1 — добавить, 2 — вставить первым, 3 — заменить, 4 — удалить последнее, 5 — найти,\n'
                          '6 — случайное, 7/8 — скрыть/показать, 0 — очистить, пробел — прочитать всё.')
    diary.when(flag(), list_clear(wishes), set_var('Счётчик', 0), set_var('Номер', 0), show_list(wishes),
               show_var('Счётчик'), say_for('Это дневник желаний. Запиши три желания!', 2),
               repeat(3, [
                   ask(join('Желание № ', add(var('Счётчик'), 1), ':')),
                   if_else(list_has(wishes, answer()), [say_for('Такое желание уже записано!', 2)],
                           [list_add(answer(), wishes)] + count),
               ]),
               say_for(join('Записано желаний: ', list_length(wishes)), 2),
               say_for(join('Первое желание: ', list_item(1, wishes)), 2),
               say_for('Клавиши 1–8, 0 и пробел управляют списком.', 3))
    diary.when(key('1'), ask('Новое желание:'), list_add(answer(), wishes), *count)
    diary.when(key('2'), ask('Самое важное желание:'), list_insert(answer(), 1, wishes), *count)
    diary.when(key('3'), ask('Номер желания для замены:'), set_var('Номер', answer()),
               if_else(and_(gt(var('Номер'), 0), not_(gt(var('Номер'), list_length(wishes)))),
                       [ask('Новый текст желания:'), list_replace(var('Номер'), wishes, answer())],
                       [say_for('Желания с таким номером нет.', 2)]))
    diary.when(key('4'), if_(gt(list_length(wishes), 0), [
        say_for(join('Удаляю: ', list_item(list_length(wishes), wishes)), 1.5),
        list_delete(list_length(wishes), wishes)] + count))
    diary.when(key('5'), ask('Что найти в дневнике?'),
               if_else(list_has(wishes, answer()),
                       [say_for(join('Найдено под номером ', list_index(answer(), wishes)), 2)],
                       [say_for('Такого желания нет.', 2)]))
    diary.when(key('6'), if_(gt(list_length(wishes), 0), [
        say_for(join('Сегодня исполним: ', list_item(rnd(1, list_length(wishes)), wishes)), 3)]))
    diary.when(key('7'), hide_list(wishes), hide_var('Счётчик'))
    diary.when(key('8'), show_list(wishes), show_var('Счётчик'))
    diary.when(key('0'), list_clear(wishes), set_var('Счётчик', 0), say_for('Дневник очищен.', 1.5))
    diary.when(key('space'), set_var('Номер', 1),
               repeat(list_length(wishes), [
                   say_for(join(var('Номер'), '. ', list_item(var('Номер'), wishes)), 1.5),
                   change_var('Номер', 1)]))
    g.add_badge()
    return g


GAMES = [game_events, game_motion, game_looks, game_sound, game_control, game_sensing, game_operators, game_data]


def package(project, assets):
    """Deterministic .sb3 archive: the same sources always give byte-identical files."""
    buff = io.BytesIO()
    with zipfile.ZipFile(buff, 'w') as archive:
        files = [('project.json', json.dumps(project, ensure_ascii=False, separators=(',', ':')).encode('utf-8'))]
        files += sorted(assets.items())
        for name, data in files:
            info = zipfile.ZipInfo(name, date_time=(2024, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data, compresslevel=9)
    return buff.getvalue()


def contents(data):
    """Files inside an .sb3, so that --check does not depend on the zip compressor version."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def main():
    check = '--check' in sys.argv[1:]
    OUT.mkdir(parents=True, exist_ok=True)
    stale = []
    for make in GAMES:
        game = make()
        project, assets = game.project()
        data = package(project, assets)
        path = OUT / f'{game.stem}.sb3'
        if check:
            if not path.exists() or contents(path.read_bytes()) != contents(data):
                stale.append(path.name)
        else:
            path.write_bytes(data)
        counts = game.stats(project)
        summary = ', '.join(f'{CATEGORY_NAMES[c]} {n}' for c, n in sorted(counts.items(), key=lambda kv: -kv[1]))
        print(f'{path.relative_to(ROOT)}: {len(data):,} bytes, {sum(counts.values())} blocks ({summary})')
    if stale:
        sys.exit('Out of date, run python3 scripts/build-games.py: ' + ', '.join(stale))


if __name__ == '__main__':
    main()
