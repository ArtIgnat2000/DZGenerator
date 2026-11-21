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

const CSS = `:root{--navy:#142f43;--teal:#168574;--line:#dce4e8;--muted:#647889;--bg:#f0f4f5}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--navy);font:16px/1.6 system-ui,-apple-system,Segoe UI,Arial,sans-serif}
a:focus-visible{outline:3px solid #e9b562;outline-offset:3px}
header{background:var(--navy);color:#fff;padding:12px 24px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px 20px}
.brand{display:flex;align-items:center;gap:12px;color:#fff;text-decoration:none}
.sitenav{display:flex;flex-wrap:wrap;gap:4px;margin-right:auto}
.sitenav a{color:#d7e6ea;text-decoration:none;font-size:14px;font-weight:600;padding:7px 12px;border-radius:7px}
.sitenav a:hover{background:#ffffff1f;color:#fff}
.sitenav a[aria-current]{background:#45c2aa;color:var(--navy)}
.mark{background:#45c2aa;color:var(--navy);width:36px;height:36px;display:grid;place-items:center;font-size:24px;font-weight:800;border-radius:4px}
header b{font-size:19px}
header small{display:block;color:#b8d1dd;font-size:10px;letter-spacing:1.4px}
main{max-width:760px;margin:0 auto;padding:24px 18px 48px}
.steps{display:grid;grid-template-columns:repeat(8,1fr);gap:6px;margin:0 0 4px}
.steps a{display:flex;flex-direction:column;align-items:center;gap:3px;background:#fff;border:1px solid var(--line);border-radius:10px;padding:7px 2px 5px;font-size:12px;line-height:1.3;color:var(--navy);text-decoration:none;overflow:hidden}
.steps b{display:grid;place-items:center;width:26px;height:26px;border-radius:50%;background:#e4eef0;font-size:12px}
.steps a:hover{border-color:var(--teal)}
.steps a[aria-current]{background:var(--teal);border-color:var(--teal);color:#fff}
.steps a[aria-current] b{background:#fff;color:var(--teal)}
h1{font-size:26px;line-height:1.25;margin:14px 0 6px}
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
.game .btn{margin:0 4px 6px 0}
.download-note{margin:8px 0 0;color:var(--muted);font-size:12px}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:22px 0 0}
.pager a{display:block;background:#fff;border:1px solid var(--line);border-radius:10px;padding:12px 16px;text-decoration:none;color:var(--navy);font-weight:600}
.pager a:hover{border-color:var(--teal)}
.pager small{display:block;color:var(--muted);font-size:12px;font-weight:400}
.pager .next{text-align:right}
.keys{display:none;margin:10px 0 0;text-align:center;font-size:12px;color:var(--muted)}
.teacher{margin:18px 0 0;font-size:13px;color:var(--muted)}
.teacher a,.download-note a{color:var(--teal);font-weight:600;text-decoration:none}
.teacher a:hover,.download-note a:hover{text-decoration:underline}
.list{list-style:none;margin:0;padding:0}
.list li{display:flex;align-items:center;gap:8px 16px;background:#fff;border:1px solid var(--line);border-radius:10px;margin:0 0 8px;padding:0 16px 0 0}
.list li:hover{border-color:var(--teal)}
.row{flex:1;min-width:0;display:flex;align-items:center;gap:14px;padding:13px 0 13px 16px;color:var(--navy);text-decoration:none}
.num{flex:none;display:grid;place-items:center;width:34px;height:34px;border-radius:50%;background:#e4eef0;font-weight:700}
.row b{display:block;line-height:1.35}
.row small{display:block;font-size:13px;line-height:1.4;color:var(--muted)}
.dl{flex:none;max-width:42%;text-align:right;font-size:13px;line-height:1.35;color:var(--teal);text-decoration:none;padding:6px 0}
.dl:hover b{text-decoration:underline}
.dl b{display:block}
footer{font-size:12px;color:var(--muted);margin-top:28px}
@media(hover:hover) and (min-width:621px){.keys{display:block}}
@media(max-width:620px){header{padding:12px 14px}.sitenav a{padding:7px 10px}.steps{gap:4px}.steps a{padding:6px 0}.steps span{display:none}.pager{grid-template-columns:1fr}.pager .next{text-align:left}.list li{flex-direction:column;align-items:stretch;gap:0;padding:0 14px 10px}.row{padding:12px 0 6px}.dl{max-width:none;text-align:left;padding:0 0 0 48px}.dl b{display:inline}}
@media print{header,.steps,.pager,.keys,.teacher,.btn,.dl,footer{display:none}body{background:#fff}main{max-width:none;padding:0}.card,.game,.idea{break-inside:avoid;page-break-inside:avoid}.lesson-title{display:block!important;font-size:20px;font-weight:700;margin:0 0 12px}}
.lesson-title{display:none}`;

// Шапка с двумя разделами сайта — одинаковая на всех страницах уроков (и такая же в генераторе).
// На странице урока пункт «Уроки и игры» подсвечен и ведёт на уровень выше — к списку уроков.
const GENERATOR = '../V-labs-generator.html';
const head = (title, home) => `<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title><style>${CSS}</style></head><body>
<header><a class="brand" href="${GENERATOR}" title="Генератор заданий — стартовая страница"><div class="mark">V</div><div><b>V-labs</b><small>SCRATCH 3.0 · УЧИМСЯ СОЗДАВАТЬ</small></div></a><nav class="sitenav" aria-label="Разделы сайта"><a href="${GENERATOR}">Генератор заданий</a><a href="index.html" aria-current="${home ? 'page' : 'true'}">Уроки и игры</a></nav></header>
<main>`;
const short = (title) => title.replace(/\s*\(.*\)$/, '');
// Переключатель уроков: все восемь всегда под рукой, текущий подсвечен.
const steps = (current) => `<nav class="steps" aria-label="Уроки курса">${LESSONS.map(x => `<a href="${x.n}.html" title="Урок ${x.n}. ${esc(x.title)}"${x.n === current ? ' aria-current="page"' : ''}><b>${x.n}</b><span>${esc(short(x.title))}</span></a>`).join('')}</nav>`;

const files = [];

// Страница урока
for (const l of LESSONS) {
  const games = l.games.map((g, i) => `<div class="game"><b>${esc(g)}</b><p>${esc(GAME_DESC[g] || '')}</p>${i === 0 ? `<a class="btn" href="games/${l.file}" download>Скачать игру для Scratch (.sb3)</a><p class="download-note">Открой файл в Scratch 3.0: Файл → Загрузить с компьютера. Проект отмечен знаком V Labs, подсказки по клавишам — в заметках рядом с блоками.</p>` : ''}</div>`).join('');
  const prev = LESSONS.find(x => x.n === l.n - 1);
  const next = LESSONS.find(x => x.n === l.n + 1);
  const nav = `<nav class="pager" aria-label="Соседние уроки">${prev ? `<a rel="prev" href="${prev.n}.html"><small>← Предыдущий урок</small>Урок ${prev.n}. ${esc(prev.title)}</a>` : `<a href="index.html"><small>← К списку</small>Все уроки и игры</a>`}${next ? `<a class="next" rel="next" href="${next.n}.html"><small>Следующий урок →</small>Урок ${next.n}. ${esc(next.title)}</a>` : `<a class="next" href="index.html"><small>Курс пройден →</small>Все уроки и игры</a>`}</nav>
<p class="keys">Клавиши ← и → на клавиатуре листают уроки</p>
<script>document.addEventListener('keydown',function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey)return;var rel=e.key==='ArrowLeft'?'prev':e.key==='ArrowRight'?'next':'';var a=rel&&document.querySelector('a[rel='+rel+']');if(a)location.href=a.href});</script>`;

  const html = `${head(`Урок ${l.n}. ${esc(l.title)} · V-labs`)}
<span class="lesson-title">V-labs · Scratch 3.0 · Урок ${l.n}. ${esc(l.title)}</span>
${steps(l.n)}
<h1>Урок ${l.n}. ${esc(l.title)}</h1>
<p class="goal">${esc(l.goal)}</p>
<div class="card"><h2>Изучаемые блоки</h2><ul>${list(l.blocks)}</ul></div>
<div class="card"><h2>Практика на уроке</h2><ul>${list(l.practice)}</ul></div>
<div class="idea"><b>Ключевая идея:</b> ${esc(l.idea)}</div>
<div class="card"><h2>Игры, которые собираем</h2>${games}</div>
<div class="card"><h2>Открыть Scratch</h2><p style="margin:0 0 10px;color:var(--muted);font-size:14px">Редактор работает в браузере, регистрация не обязательна для тренировки. Сохранение проекта — по кнопке «Сохранить сейчас».</p><a class="btn" href="${SCRATCH}" target="_blank" rel="noopener">Открыть редактор Scratch</a></div>
${nav}
<p class="teacher">Преподавателю: <a href="${GENERATOR}?lesson=${l.n}">собрать письмо по уроку ${l.n}</a></p>
<footer>V-labs · Scratch 3.0 · Урок ${l.n} из ${LESSONS.length}</footer>
</main></body></html>
`;
  files.push([`${l.n}.html`, html]);
}

// Оглавление: один список. Урок и его игра — одна строка, потому что они идут парой.
const rows = LESSONS.map(l => `<li><a class="row" href="${l.n}.html"><span class="num">${l.n}</span><span><b>${esc(l.title)}</b><small>${esc(l.goal)}</small></span></a><a class="dl" href="games/${l.file}" download title="${esc(GAME_DESC[l.games[0]] || '')}">Скачать игру <b>«${esc(l.games[0])}»</b></a></li>`).join('');
files.push(['index.html', `${head('Уроки и игры Scratch · V-labs', true)}
<h1>Уроки и игры Scratch</h1>
<p class="goal">${LESSONS.length} уроков курса. У каждого — страница с блоками и практикой и готовая игра для Scratch 3.0.</p>
<ol class="list" id="games">${rows}</ol>
<p class="download-note">Игра — это файл .sb3. Откройте его в Scratch 3.0: Файл → Загрузить с компьютера. <a href="${SCRATCH}" target="_blank" rel="noopener">Открыть редактор Scratch</a></p>
<footer>V-labs · Scratch 3.0 · ${LESSONS.length} уроков и ${LESSONS.length} игр</footer>
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
