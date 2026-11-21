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
const end = src.indexOf('\nconst $=id=>', start);
if (start < 0 || end < 0) {
  console.error('Не найдены данные уроков и курсов в V-labs-generator.html');
  process.exit(1);
}
// В блоке данных — LESSONS (курс 1), GAME_LESSONS (курс 2) и COURSES.
const { LESSONS, COURSES } = new Function(`${src.slice(start, end)}\nreturn {LESSONS, COURSES};`)();

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
  'Мелодия на клавишах': 'Робот поёт ноты по клавишам 1–5, а по пробелу — песенку целиком.',
  'Метеоритный дождь': 'Уклоняйся от клонов-метеоритов и лови звёзды: циклы, условия, уровни и жизни.',
  'Салют из клонов': 'Клоны искры взлетают, вспыхивают и исчезают.',
  'Викторина': 'Спрашивает имя и проверяет ответ.',
  'Герой следует за мышью': 'Спрайт идёт к курсору мыши.',
  'Калькулятор удачи': 'Случайное число от 1 до 100 — «Ты везунчик!» при > 80.',
  'Угадай число': 'Компьютер загадывает число, ты угадываешь.',
  'Дневник желаний': 'Желания записываются в список: добавляй, вставляй, заменяй, ищи и удаляй клавишами.',
  'Список покупок': 'Корзина спрашивает покупки и собирает их в список.'
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
.lesson-title{display:none}
.course{margin:28px 0 0;padding-top:18px;border-top:1px solid var(--line)}
.course:first-of-type{border-top:0;padding-top:0;margin-top:18px}
.course h2{font-size:19px;text-transform:none;letter-spacing:0;margin:0 0 4px;color:var(--navy)}
.course .goal{margin:0 0 12px;font-size:14px}
.badge{display:inline-block;background:#e4eef0;color:var(--teal);font-size:11px;font-weight:700;letter-spacing:.4px;padding:2px 7px;border-radius:20px;vertical-align:2px;margin-left:7px;text-transform:uppercase}
.list li.plain{cursor:default;background:#f7fbfa}
.list li.plain .row{cursor:default}
.dl.soon{color:var(--muted);font-weight:500}
`;

// Шапка с двумя разделами сайта — одинаковая на всех страницах уроков (и такая же в генераторе).
// На странице урока пункт «Уроки и игры» подсвечен и ведёт к общему списку курсов.
const short = (title) => title.replace(/\s*\(.*\)$/, '');
const head = (title, { prefix = '../', homeHref = 'index.html', current = true } = {}) => `<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${title}</title><style>${CSS}</style></head><body>
<header><a class="brand" href="${prefix}V-labs-generator.html" title="Генератор заданий — стартовая страница"><div class="mark">V</div><div><b>V-labs</b><small>SCRATCH 3.0 · УЧИМСЯ СОЗДАВАТЬ</small></div></a><nav class="sitenav" aria-label="Разделы сайта"><a href="${prefix}V-labs-generator.html">Генератор заданий</a><a href="${homeHref}" aria-current="${current ? 'page' : 'true'}">Уроки и игры</a></nav></header>
<main>`;
// Переключатель уроков: все уроки курса всегда под рукой, текущий подсвечен.
const steps = (course, current) => `<nav class="steps" aria-label="Уроки курса">${course.lessons.map(x => `<a href="${x.n}.html" title="Урок ${x.n}. ${esc(x.title)}"${x.n === current ? ' aria-current="page"' : ''}><b>${x.n}</b><span>${esc(short(x.title))}</span></a>`).join('')}</nav>`;

const files = [];
const dirOf = (course) => course.n === 1 ? '' : `course-${course.n}/`;
const prefixOf = (course) => course.n === 1 ? '../' : '../../';
const teacherHref = (course, l) => `${prefixOf(course)}V-labs-generator.html?${course.n === 1 ? '' : `course=${course.n}&`}lesson=${l.n}`;

// Страница урока.
function lessonPage(course, l) {
  const i = course.lessons.indexOf(l);
  const prev = course.lessons[i - 1];
  const next = course.lessons[i + 1];
  const gameHref = (file) => course.n === 1 ? `games/${file}` : `../games/${file}`;
  const practiceHref = (tail) => course.n === 1 ? `practice/${tail}` : `../practice/${tail}`;
  const near = (x) => course.n === 1 ? `${x}.html` : `${x}.html`;

  const ownGame = !!(l.file && l.games && l.games.length);
  const warm = l.warmup ? LESSONS.find(x => x.n === l.warmup.n) : null;
  const gameCards = [];
  if (ownGame) {
    l.games.forEach((g, gi) => {
      gameCards.push(`<div class="game"><b>${esc(g)}</b><p>${esc(GAME_DESC[g] || '')}</p>${gi === 0 ? `<a class="btn" href="${gameHref(l.file)}" download>Скачать игру для Scratch (.sb3)</a><p class="download-note">Открой файл в Scratch 3.0: Файл → Загрузить с компьютера. Проект отмечен знаком V Labs, подсказки по клавишам — в заметках рядом с блоками.</p>` : ''}</div>`);
    });
  } else if (warm) {
    const g = warm.games[Math.max(0, +l.warmup.game || 0)] || warm.games[0];
    gameCards.push(`<div class="game"><b>Разминка: «${esc(g)}»</b><p>${esc(GAME_DESC[g] || '')}</p><a class="btn ghost" href="${gameHref(warm.file)}" download>Скачать игру «${esc(g)}» (.sb3)</a><p class="download-note">Это игра курса 1. С неё начинается письмо «Готовимся к уроку»: ребёнок вспоминает механику, а новую игру собирает на уроке.</p></div>`);
  }

  const practice = l.file && l.work
    ? `<div class="card"><h2>Практика на уроке</h2><ul>${list(l.practice)}</ul><a class="btn" href="${practiceHref(`${l.file.replace('.sb3', '')}-start.sb3`)}" download>Скачать заготовку «${esc(l.work)}» (.sb3)</a><p class="download-note">В заготовке есть герои, фоны и звуки, программы нет. Шаги практики записаны в заметке — там, где собирают блоки. Готовый проект ученик получает после урока, если попросит: преподаватель отправляет ему письмо «Разгадка».</p></div>`
    : `<div class="card"><h2>Практика на уроке</h2><ul>${list(l.practice)}</ul><p class="download-note">Практику собираем на уроке в Scratch. Заготовка и разгадка появятся вместе с демо-игрой этого урока.</p></div>`;

  const nav = `<nav class="pager" aria-label="Соседние уроки">${prev ? `<a rel="prev" href="${near(prev.n)}"><small>← Предыдущий урок</small>Урок ${prev.n}. ${esc(prev.title)}</a>` : `<a href="index.html"><small>← К началу курса</small>${esc(course.title)}</a>`}${next ? `<a class="next" rel="next" href="${near(next.n)}"><small>Следующий урок →</small>Урок ${next.n}. ${esc(next.title)}</a>` : `<a class="next" href="${course.n === 1 ? 'index.html' : '../index.html'}"><small>${course.n === 1 ? 'Курс пройден →' : 'К списку курсов →'}</small>${course.n === 1 ? 'Все уроки и игры' : 'Уроки и игры'}</a>`}</nav>
<p class="keys">Клавиши ← и → на клавиатуре листают уроки</p>
<script>document.addEventListener('keydown',function(e){if(e.altKey||e.ctrlKey||e.metaKey||e.shiftKey)return;var rel=e.key==='ArrowLeft'?'prev':e.key==='ArrowRight'?'next':'';var a=rel&&document.querySelector('a[rel='+rel+']');if(a)location.href=a.href});</script>`;

  const title = course.n === 1 ? `Урок ${l.n}. ${esc(l.title)} · V-labs` : `Урок ${l.n}. ${esc(l.title)} · ${esc(course.title)} · V-labs`;
  const h1 = course.n === 1 ? `Урок ${l.n}. ${esc(l.title)}` : `Урок ${l.n}. ${esc(l.title)} <span class="badge">${esc(course.short)}</span>`;
  const gamesHeading = ownGame ? 'Игры, которые собираем' : warm ? 'Разминка перед уроком' : 'Игра урока';
  const gamesBlock = gameCards.length
    ? `<div class="card"><h2>${gamesHeading}</h2>${gameCards.join('')}</div>`
    : `<div class="card"><h2>Игра урока</h2><p style="margin:0;color:var(--muted);font-size:14px">Демо-игра этого урока ещё не опубликована: в письме «Готовимся к уроку» пока используется разминка из курса 1.</p></div>`;
  const footer = course.n === 1
    ? `V-labs · Scratch 3.0 · Урок ${l.n} из ${course.lessons.length}`
    : `V-labs · Scratch 3.0 · ${esc(course.title)} · Урок ${l.n} из ${course.lessons.length}`;

  return `${head(title, { prefix: prefixOf(course), homeHref: course.n === 1 ? 'index.html' : '../index.html' })}
<span class="lesson-title">V-labs · Scratch 3.0 · ${esc(course.title)} · Урок ${l.n}. ${esc(l.title)}</span>
${steps(course, l.n)}
<h1>${h1}</h1>
<p class="goal">${esc(l.goal)}</p>
<div class="card"><h2>Изучаемые блоки</h2><ul>${list(l.blocks)}</ul></div>
${practice}
<div class="idea"><b>Ключевая идея:</b> ${esc(l.idea)}</div>
${gamesBlock}
<div class="card"><h2>Открыть Scratch</h2><p style="margin:0 0 10px;color:var(--muted);font-size:14px">Редактор работает в браузере, регистрация не обязательна для тренировки. Сохранение проекта — по кнопке «Сохранить сейчас».</p><a class="btn" href="${SCRATCH}" target="_blank" rel="noopener">Открыть редактор Scratch</a></div>
${nav}
<p class="teacher">Преподавателю: <a href="${teacherHref(course, l)}">собрать письмо по уроку ${l.n}</a></p>
<footer>${footer}</footer>
</main></body></html>
`;
}

for (const course of COURSES) {
  for (const l of course.lessons) files.push([`${dirOf(course)}${l.n}.html`, lessonPage(course, l)]);
}

// Страница курса 2: программа без скачиваемых игр — они появятся отдельным релизом.
const course2 = COURSES.find(c => c.n === 2);
if (course2) {
  const rows = course2.lessons.map(l => `<li class="plain"><a class="row" href="${l.n}.html"><span class="num">${l.n}</span><span><b>${esc(l.title)}</b><small>${esc(l.goal)}</small></span></a><span class="dl soon">Практика <b>«${esc(l.work)}»</b></span></li>`).join('');
  files.push([`course-2/index.html`, `${head('Курс 2. Разработка игр · V-labs', { prefix: '../../', homeHref: '../index.html' })}
<h1>Курс 2. Разработка игр</h1>
<p class="goal">Восемь уроков — восемь игровых механик. На каждом уроке новая мини-игра, а в письме «Готовимся к уроку» — разминка в игре курса 1 и три шага подготовки.</p>
<ol class="list" id="games">${rows}</ol>
<p class="download-note">Демо-игры и заготовки курса 2 появятся отдельным релизом. Пока на страницах уроков — блоки, практика и ключевая идея, а письма собираются из текстов уроков и разминки.</p>
<p class="download-note"><a href="../1.html">← Курс 1. Основы Scratch</a></p>
<footer>V-labs · Scratch 3.0 · ${esc(course2.title)} · ${course2.lessons.length} уроков</footer>
</main></body></html>
`]);
}

// Оглавление: три курса. Курс 1 — игры и страницы уроков, курс 2 — программа, курс 3 — следующий этап.
const course1 = COURSES.find(c => c.n === 1);
const rows1 = course1.lessons.map(l => `<li><a class="row" href="${l.n}.html"><span class="num">${l.n}</span><span><b>${esc(l.title)}</b><small>${esc(l.goal)}</small></span></a><a class="dl" href="games/${l.file}" download title="${esc(GAME_DESC[l.games[0]] || '')}">Скачать игру <b>«${esc(l.games[0])}»</b></a></li>`).join('');
const rows2 = course2 ? course2.lessons.map(l => `<li class="plain"><a class="row" href="course-2/${l.n}.html"><span class="num">${l.n}</span><span><b>${esc(l.title)}</b><small>${esc(l.goal)}</small></span></a><span class="dl soon">Практика <b>«${esc(l.work)}»</b></span></li>`).join('') : '';
const course3 = COURSES.find(c => c.n === 3);
files.push(['index.html', `${head('Уроки и игры Scratch · V-labs', { prefix: '../', homeHref: 'index.html' })}
<h1>Уроки и игры Scratch</h1>
<p class="goal">Три курса: основы Scratch, разработка игр и своя игра. Уроки курса 1 — со скачиваемыми играми и страницами; курс 2 пока в виде программы.</p>
<section class="course">
<h2>Курс 1. Основы Scratch</h2>
<p class="goal">Восемь групп блоков. У каждого урока — страница с блоками и практикой и готовая игра для Scratch 3.0.</p>
<ol class="list" id="games">${rows1}</ol>
<p class="download-note">Игра — это файл .sb3. Откройте его в Scratch 3.0: Файл → Загрузить с компьютера. <a href="${SCRATCH}" target="_blank" rel="noopener">Открыть редактор Scratch</a></p>
</section>
<section class="course">
<h2>Курс 2. Разработка игр</h2>
<p class="goal">Восемь игровых механик: догонялки, платформер, лабиринт, ловец, погоня, тир, приключение и своя игра. <a href="course-2/index.html">Программа курса →</a></p>
<ol class="list">${rows2}</ol>
</section>
<section class="course">
<h2>Курс 3. Своя игра</h2>
<p class="goal">${course3 ? esc(course3.note) : 'Спринты по своей игре'}. Следующий этап: замысел на одной карточке, прототип, три-четыре спринта и показ игр. Уроки появятся после курса 2.</p>
</section>
<footer>V-labs · Scratch 3.0 · ${course1.lessons.length + (course2 ? course2.lessons.length : 0)} уроков в двух курсах</footer>
</main></body></html>
`]);

let bad = 0;
fs.mkdirSync(OUT, { recursive: true });
for (const [name, html] of files) {
  const target = path.join(OUT, name);
  fs.mkdirSync(path.dirname(target), { recursive: true });
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
  console.log(`Страницы уроков совпадают с данными: ${files.length} файлов, ${COURSES.reduce((n, c) => n + c.lessons.length, 0)} уроков.`);
}
