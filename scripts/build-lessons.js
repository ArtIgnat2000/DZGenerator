#!/usr/bin/env node
/*
 * Собирает страницы уроков (lessons/*.html) из массива LESSONS
 * в V-labs-generator.html — единого источника данных об уроках.
 *
 * Запуск: node scripts/build-lessons.js
 * Проверка в CI: node scripts/build-lessons.js --check
 *   --check ничего не пишет, только сравнивает файлы и выходит с кодом 1 при расхождении.
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const GEN = path.join(ROOT, 'V-labs-generator.html');
const OUT = path.join(ROOT, 'lessons');
const CHECK = process.argv.includes('--check');

const src = fs.readFileSync(GEN, 'utf8');
const start = src.indexOf('const LESSONS=');
const end = src.indexOf('\n];', start);
if (start < 0 || end < 0) {
  console.error('Не найден массив LESSONS в V-labs-generator.html');
  process.exit(1);
}
const LESSONS = new Function(`${src.slice(start, end + 3)}\nreturn LESSONS;`)();

const GAME_DESC = {
  'Солнце и дождь': 'Интерактивная сценка: клики, клавиши, таймер и сообщения меняют погоду — дождь, гром, ветер и радугу.',
  'Космический маршрут': 'Веди ракету стрелками к маяку, уворачивайся от астероида и пробуй манёвры клавишами 0–9.',
  'Театр настроений': 'Артист меняет костюмы, размер, цвет и эффекты; декорации и слои переключаются клавишами.',
  'Следопыт за мышью': 'Герой идёт за указателем и ищет невидимый клад по подсказкам «горячо — холодно».',
  'Математический оракул': 'Пять случайных примеров на +, −, × и : и рассказ оракула о любом числе.',
  'Радуга по сообщению': 'Радуга появляется по пробелу через сообщения.',
  'Лабиринт': 'Герой проходит лабиринт стрелками: стены не пускают, на финише — «Победа!».',
  'Гонки по трассе': 'Гонка по трассе: управление направлением и скоростью.',
  'История с персонажем': 'Персонаж рассказывает историю и меняет костюмы.',
  'Театр костюмов': 'Смена костюмов и реплик — как в театре.',
  'Музыкальный инструмент': 'Клавиши 1–8 играют ноты, 9 — барабан; три кнопки играют мелодии из «Звёздных войн»: Имперский марш, Cantina Band и главную тему.',
  'Мелодия на клавишах': 'Автоплей мелодии и запись своих нот.',
  'Метеоритный дождь': 'Уклоняйся от клонов-метеоритов и лови звёзды: циклы, условия, уровни и жизни.',
  'Салют из клонов': 'Клоны разлетаются салютом по клику.',
  'Викторина': 'Спрашивает имя и проверяет ответ.',
  'Герой следует за мышью': 'Спрайт идёт к курсору мыши.',
  'Калькулятор удачи': 'Случайное число от 1 до 100 — «Ты везунчик!» при > 80.',
  'Угадай число': 'Компьютер загадывает число, ты угадываешь.',
  'Дневник желаний': 'Желания записываются в список: добавляй, вставляй, заменяй, ищи и удаляй клавишами.',
  'Список покупок': 'Собираем список: добавить, показать, выбрать элемент.'
};

const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
const list = s => s.split('; ').map(x => `<li>${esc(x.trim())}</li>`).join('');
const SCRATCH = 'https://scratch.mit.edu/projects/editor/';
const GAME_FILES = {1:'01-events.sb3',2:'02-motion.sb3',3:'03-looks.sb3',4:'04-sound.sb3',5:'05-control.sb3',6:'06-sensing.sb3',7:'07-operators.sb3',8:'08-data.sb3'};

const CSS = `:root{--navy:#142f43;--teal:#168574;--line:#dce4e8;--muted:#647889;--bg:#f0f4f5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--navy);font:16px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif}
header{background:var(--navy);color:#fff;padding:16px 24px;display:flex;align-items:center;gap:12px}
.mark{background:#45c2aa;color:var(--navy);width:36px;height:36px;display:grid;place-items:center;font-size:24px;font-weight:800;border-radius:4px}
header b{font-size:19px}
header small{display:block;color:#b8d1dd;font-size:10px;letter-spacing:1.4px}
main{max-width:760px;margin:0 auto;padding:24px 18px 48px}
.back{font-size:13px;color:var(--teal);text-decoration:none}
h1{font-size:26px;margin:14px 0 6px}
.goal{color:var(--muted);margin:0 0 20px}
.card{background:#fff;border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 14px}
h2{font-size:15px;margin:0 0 10px;color:var(--teal);letter-spacing:.6px;text-transform:uppercase}
ul{margin:0;padding-left:20px}
li{margin:4px 0}
.idea{background:#eff7f5;border-left:4px solid var(--teal);padding:14px 18px;border-radius:0 8px 8px 0;margin:0 0 14px}
.game{border:1px solid var(--line);border-radius:8px;padding:14px 16px;margin:0 0 10px}
.game b{display:block;margin-bottom:4px}
.game p{margin:0 0 10px;color:var(--muted);font-size:14px}
.btn{display:inline-block;background:var(--teal);color:#fff;text-decoration:none;padding:8px 14px;border-radius:6px;font-size:14px;font-weight:600}
.btn.ghost{background:#fff;color:var(--teal);border:1px solid var(--teal)}
.download-note{margin:8px 0 0;color:var(--muted);font-size:12px}
.nav{display:flex;justify-content:space-between;gap:10px;margin:22px 0 0;font-size:14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px}
.grid a{display:block;background:#fff;border:1px solid var(--line);border-radius:10px;padding:16px;text-decoration:none;color:var(--navy)}
.grid a:hover{border-color:var(--teal)}
.grid b{display:block;margin-bottom:4px}
.grid span{font-size:13px;color:var(--muted)}
footer{font-size:12px;color:var(--muted);margin-top:28px}
@media print{header,main>.back,.nav,.btn,footer{display:none}body{background:#fff}main{max-width:none;padding:0}.card,.game,.idea{break-inside:avoid;page-break-inside:avoid}.lesson-title{display:block!important;font-size:20px;font-weight:700;margin:0 0 12px}}
.lesson-title{display:none}`;

const head = (title) => `<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title><style>${CSS}</style></head><body>
<header><div class="mark">V</div><div><b>V-labs</b><small>SCRATCH 3.0 · УЧИМСЯ СОЗДАВАТЬ</small></div></header>
<main>`;

const files = [];

// Страница урока
for (const l of LESSONS) {
  const games = l.games.map((g, i) => `<div class="game"><b>${esc(g)}</b><p>${esc(GAME_DESC[g] || '')}</p>${i === 0 ? `<a class="btn" href="games/${GAME_FILES[l.n]}" download>Скачать игру для Scratch (.sb3)</a><p class="download-note">Открой файл в Scratch 3.0: Файл → Загрузить с компьютера. Проект отмечен знаком V Labs, подсказки по клавишам — в заметках рядом с блоками.</p>` : ''}</div>`).join('');
  const prev = LESSONS.find(x => x.n === l.n - 1);
  const next = LESSONS.find(x => x.n === l.n + 1);
  const nav = `<div class="nav"><span>${prev ? `<a class="back" href="${prev.n}.html">← Урок ${prev.n}. ${esc(prev.title)}</a>` : ''}</span><span>${next ? `<a class="back" href="${next.n}.html">Урок ${next.n}. ${esc(next.title)} →</a>` : ''}</span></div>`;

  const html = `${head(`Урок ${l.n}. ${esc(l.title)} · V-labs`)}
<span class="lesson-title">V-labs · Scratch 3.0 · Урок ${l.n}. ${esc(l.title)}</span>
<a class="back" href="index.html">← Все уроки</a>
<h1>Урок ${l.n}. ${esc(l.title)}</h1>
<p class="goal">${esc(l.goal)}</p>
<div class="card"><h2>Изучаемые блоки</h2><ul>${list(l.blocks)}</ul></div>
<div class="card"><h2>Практика на уроке</h2><ul>${list(l.practice)}</ul></div>
<div class="idea"><b>Ключевая идея:</b> ${esc(l.idea)}</div>
<div class="card"><h2>Игры, которые собираем</h2>${games}</div>
<div class="card"><h2>Открыть Scratch</h2><p style="margin:0 0 10px;color:var(--muted);font-size:14px">Редактор работает в браузере, регистрация не обязательна для тренировки. Сохранение проекта — по кнопке «Сохранить сейчас».</p><a class="btn" href="${SCRATCH}" target="_blank" rel="noopener">Открыть редактор Scratch</a> <a class="btn ghost" href="../V-labs-generator.html">Собрать письмо с заданием</a></div>
${nav}
<footer>V-labs · Scratch 3.0 · Урок ${l.n} из ${LESSONS.length}</footer>
</main></body></html>
`;
  files.push([`${l.n}.html`, html]);
}

// Оглавление
const cards = LESSONS.map(l => `<a href="${l.n}.html"><b>Урок ${l.n}. ${esc(l.title)}</b><span>${esc(l.goal)}</span></a>`).join('');
const gameCards = LESSONS.map(l => `<div class="game"><b>Урок ${l.n}. ${esc(l.title)}</b><p>${esc(l.games[0])}</p><a class="btn" href="games/${GAME_FILES[l.n]}" download>Скачать проект (.sb3)</a> <a class="btn ghost" href="${l.n}.html">Страница урока</a></div>`).join('');
files.push(['index.html', `${head('Уроки Scratch · V-labs')}
<a class="back" href="../V-labs-generator.html">← К генератору заданий</a>
<h1>Уроки Scratch</h1>
<p class="goal">Программа курса: каждый тип блоков разбираем через практику. Выберите урок — там блоки, практика, идея и игры, которые собираем на занятии.</p>
<div class="grid">${cards}</div>
<div class="card"><h2>Все проекты Scratch для скачивания</h2><p class="goal">Загрузите стартовый проект нужного урока. На странице урока кнопка скачивания также находится рядом с описанием игры.</p><div class="grid">${gameCards}</div></div>
<footer>V-labs · Scratch 3.0 · ${LESSONS.length} уроков и стартовых проектов</footer>
</main></body></html>
`]);

let bad = 0;
fs.mkdirSync(OUT, { recursive: true });
for (const [name, html] of files) {
  const target = path.join(OUT, name);
  if (CHECK) {
    const cur = fs.existsSync(target) ? fs.readFileSync(target, 'utf8') : null;
    if (cur !== html) { console.error(`УСТАРЕЛО: lessons/${name}`); bad++; }
  } else {
    fs.writeFileSync(target, html, 'utf-8');
    console.log(`lessons/${name}`);
  }
}
if (CHECK) {
  if (bad) { console.error(`Страниц уроков надо пересобрать: ${bad}. Запустите node scripts/build-lessons.js`); process.exit(1); }
  console.log(`Страницы уроков совпадают с данными: ${files.length} файлов, ${LESSONS.length} уроков.`);
}
