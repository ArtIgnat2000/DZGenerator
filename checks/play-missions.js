#!/usr/bin/env node
// Проходит миссии писем «Готовимся к уроку» в настоящем движке Scratch — так, как их проходит ученик:
// флажок, клавиши, клики, ответы на вопросы, правка числа в блоке. Проверяет, что после каждого шага
// происходит то, что обещано в письме и в «Ответах для вас».
//
// Нужен, когда меняется игра (scripts/build-games.py) или текст миссии (LESSONS в V-labs-generator.html).
// В CI не запускается: ему нужны движок Scratch и браузер. Быстрая проверка без запуска игр —
// scripts/check-missions.py.
//
// Подготовка (один раз, вне репозитория):
//   mkdir -p /tmp/vlabs-play && cd /tmp/vlabs-play && npm init -y
//   npm install scratch-vm scratch-render scratch-storage puppeteer-core @sparticuz/chromium
// Запуск из корня репозитория:
//   node checks/play-missions.js          — все восемь уроков, около шести минут
//   node checks/play-missions.js 3 6      — только уроки 3 и 6
// Переменные окружения:
//   PLAY_DEPS  — папка, где лежит node_modules (по умолчанию /tmp/vlabs-play)
//   CHROME     — путь к своему Chrome или Chromium; без неё берётся @sparticuz/chromium
//                (ему на обычном Linux нужна ещё AWS_EXECUTION_ENV=AWS_Lambda_nodejs22.x)
//   PLAY_SHOTS — папка для снимков сцены (урок 3 с размером 270, урок 8 с пятью желаниями)
//
// Чего проверка не видит: звук (движок работает без звуковой карты) и то, как игра выглядит в TurboWarp.
const http = require('http'), fs = require('fs'), path = require('path');
const REPO = path.resolve(__dirname, '..');
const DEPS = path.join(process.env.PLAY_DEPS || '/tmp/vlabs-play', 'node_modules');
const dep = require('module').createRequire(path.join(DEPS, 'x.js'));
const PAGE = `<!doctype html><meta charset=utf-8><body style="margin:0;background:#fff"><canvas id=c width=480 height=360 style="width:480px;height:360px"></canvas>
<script src="/lib/scratch-storage/dist/web/scratch-storage.js"></script>
<script src="/lib/scratch-render/dist/web/scratch-render.js"></script>
<script src="/lib/scratch-vm/dist/web/scratch-vm.js"></script>`;
function serve() {
  return new Promise(res => {
    const s = http.createServer((q, r) => {
      const u = decodeURIComponent(q.url.split('?')[0]);
      if (u === '/') { r.writeHead(200, { 'content-type': 'text/html' }); return r.end(PAGE); }
      const f = u.startsWith('/lib/') ? path.join(DEPS, u.slice(5)) : path.join(REPO, 'lessons/games', u.slice(1));
      fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); return r.end(); } r.writeHead(200, { 'content-type': f.endsWith('.js') ? 'text/javascript' : 'application/octet-stream' }); r.end(b); });
    }).listen(0, () => res(s));
  });
}
async function open() {
  const srv = await serve();
  const puppeteer = dep('puppeteer-core'); let args = [], executablePath = process.env.CHROME;
  if (!executablePath) { const chromium = dep('@sparticuz/chromium').default || dep('@sparticuz/chromium'); args = chromium.args; executablePath = await chromium.executablePath() }
  // движку нужен WebGL: в браузере без видеокарты его даёт SwiftShader
  const b = await puppeteer.launch({ args: [...args, '--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'], executablePath, headless: true });
  return { srv, b, base: 'http://localhost:' + srv.address().port + '/' };
}
// Одна игра — одна страница браузера. В странице window.G — помощники «игрока».
async function game(env, file) {
  const p = await env.b.newPage(); await p.setViewport({ width: 480, height: 360 });
  p.on('pageerror', e => console.log('PAGEERR', String(e).slice(0, 300)));
  await p.goto(env.base, { waitUntil: 'load' });
  await p.evaluate(async file => {
    const VMc = window.VirtualMachine.default || window.VirtualMachine;
    const St = window.ScratchStorage.ScratchStorage || window.ScratchStorage.default || window.ScratchStorage;
    const Rn = window.ScratchRender.default || window.ScratchRender;
    const vm = new VMc(); vm.attachStorage(new St());
    const canvas = document.getElementById('c'); const renderer = new Rn(canvas); vm.attachRenderer(renderer);
    renderer.draw();
    const buf = await (await fetch('/' + file)).arrayBuffer();
    await vm.loadProject(buf);
    const G = window.G = { vm, renderer, says: [], asks: [], log: [] };
    vm.runtime.on('SAY', (target, type, text) => { G.lastSay = String(text); if (text) G.says.push({ who: target.getName(), type, text: String(text), t: Date.now() }) });
    // видимый спрайт задаёт вопрос облачком: текст приходит событием SAY, а QUESTION — пустой
    vm.runtime.on('QUESTION', q => { if (q !== null) G.asks.push(q === '' ? G.lastSay : String(q)); G.question = q });
    G.sprite = name => vm.runtime.targets.find(t => t.isOriginal && t.getName() === name);
    G.stage = () => vm.runtime.getTargetForStage();
    G.v = name => { for (const t of vm.runtime.targets) for (const v of Object.values(t.variables)) if (v.name === name) return v.value };
    G.flag = () => vm.greenFlag();
    G.key = (key, ms = 60) => new Promise(r => { vm.postIOData('keyboard', { key, isDown: true }); setTimeout(() => { vm.postIOData('keyboard', { key, isDown: false }); setTimeout(r, 60) }, ms) });
    G.hold = (key, down) => vm.postIOData('keyboard', { key, isDown: down });
    // координаты Scratch: x −240..240, y −180..180
    G.mouse = (x, y, isDown) => vm.postIOData('mouse', Object.assign({ x: x + 240, y: 180 - y, canvasWidth: 480, canvasHeight: 360 }, isDown === undefined ? {} : { isDown }));
    G.click = (x, y) => new Promise(r => { G.mouse(x, y); G.mouse(x, y, true); setTimeout(() => { G.mouse(x, y, false); setTimeout(r, 80) }, 60) });
    G.clickSprite = name => { const t = G.sprite(name); return G.click(t.x, t.y) };
    G.answer = text => vm.runtime.emit('ANSWER', text);
    G.wait = ms => new Promise(r => setTimeout(r, ms));
    G.until = async (fn, ms = 15000) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if (fn()) return true; await G.wait(40) } return false };
    // правка числа в блоке — то же, что делает ученик в редакторе
    G.blocks = (spriteName, opcode) => { const t = spriteName === 'Stage' ? G.stage() : G.sprite(spriteName); return Object.values(t.blocks._blocks).filter(b => b.opcode === opcode && !b.shadow) };
    G.num = (spriteName, block, input) => { const t = spriteName === 'Stage' ? G.stage() : G.sprite(spriteName); const sh = t.blocks._blocks[block.inputs[input].shadow]; const f = Object.values(sh.fields)[0]; return { t, sh, f } };
    G.getNum = (s, b, i) => G.num(s, b, i).f.value;
    G.setNum = (s, b, i, value) => { const { t, sh, f } = G.num(s, b, i); t.blocks.changeBlock({ id: sh.id, element: 'field', name: f.name, value: String(value) }); t.blocks.resetCache() };
    G.backdrop = () => { const s = G.stage(); return s.getCostumes()[s.currentCostume].name };
    G.costume = n => { const s = G.sprite(n); return s.getCostumes()[s.currentCostume].name };
    // как в редакторе Scratch: 30 кадров в секунду
    vm.setCompatibilityMode(true);
    G.frame = 0; const rt = vm.runtime, step = rt._step.bind(rt); rt._step = function () { step(); G.frame++; if (G.onFrame) G.onFrame() };
    G.frames = async n => { const f0 = G.frame; while (G.frame - f0 < n) await new Promise(r => setTimeout(r, 4)) };
    vm.start();
  }, file);
  return p;
}
const results = [];
function ok(c, m, extra) { results.push(!!c); console.log((c ? 'ok   ' : 'FAIL ') + m + (extra !== undefined ? '  → ' + JSON.stringify(extra) : '')) }
const shot = (p, n) => process.env.PLAY_SHOTS ? p.screenshot({ path: path.join(process.env.PLAY_SHOTS, n + '.png') }) : null;
function done() { const f = results.filter(x => !x).length; console.log(f ? 'FAILED ' + f : 'ALL OK ' + results.length); return f }

(async () => {
  const env = await open();
  let p, r; const want = n => process.argv.length < 3 || process.argv.slice(2).includes(String(n));

  // ---------- УРОК 1 ----------
  if (want(1)) {
  console.log('\n== Урок 1. Управляй погодой');
  p = await game(env, '01-events.sb3');
  r = await p.evaluate(async () => {
    const o = {};
    G.flag(); await G.wait(900); o.start = G.backdrop();
    await G.clickSprite('Облако'); await G.wait(500); o.cloud = G.backdrop(); o.sunHidden = !G.sprite('Солнце').visible; o.drops = G.sprite('Капля').visible;
    await G.key(' '); await G.wait(500); o.space = G.backdrop(); o.sunBack = G.sprite('Солнце').visible;
    const e0 = G.v('Событий'); G.says.length = 0; let flash = 0; const iv = setInterval(() => { flash = Math.max(flash, G.stage().effects.brightness) }, 15);
    await G.key('3'); await G.wait(2500); clearInterval(iv); o.thunder = { flash, says: G.says.map(s => s.text), events: G.v('Событий') - e0, backdrop: G.backdrop() };
    // шаг 2: блок
    const hats = G.blocks('Солнце', 'event_whengreaterthan'); o.hats = hats.length; o.hatValue = G.getNum('Солнце', hats[0], 'VALUE'); o.hatMenu = hats[0].fields.WHENGREATERTHANMENU.value;
    // «Хочу ещё»: какая клавиша устраивает ветер
    o.wind = {};
    for (const k of ['1', '2', '3', '4']) { const c = G.sprite('Облако'); const x0 = c.x; let far = 0; const iv2 = setInterval(() => { far = Math.max(far, Math.abs(c.x - x0)) }, 20); G.says.length = 0; await G.key(k); await G.wait(2400); clearInterval(iv2); o.wind[k] = { moved: Math.round(far), backdrop: G.backdrop(), says: G.says.map(s => s.text) } }
    // шаг 3 до правки: когда срабатывает таймер
    const sayAt = t0 => { const s = G.says.find(s => /Событие таймера/.test(s.text)); return s ? (s.t - t0) / 1000 : null };
    G.says.length = 0; G.flag(); let t0 = Date.now(); o.at6 = null; await G.wait(6000); o.at6 = G.backdrop();
    await G.until(() => G.backdrop() === 'Радуга', 20000); o.base = (Date.now() - t0) / 1000; o.baseSay = sayAt(t0);
    // правка 20 → 5
    G.setNum('Солнце', hats[0], 'VALUE', 5); G.says.length = 0; G.flag(); t0 = Date.now(); await G.wait(300); o.afterFlag = G.backdrop();
    await G.until(() => G.backdrop() === 'Радуга', 12000); o.changed = (Date.now() - t0) / 1000; o.changedSay = sayAt(t0); await G.wait(300); o.changedSays = G.says.map(s => s.text);
    return o;
  });
  console.log(JSON.stringify(r));
  ok(r.start === 'Солнечно' && r.cloud === 'Дождливо' && r.sunHidden && r.drops, 'шаг 1: клик по облаку — дождь (фон, капли, солнце спряталось)');
  ok(r.space === 'Радуга' && r.sunBack, 'шаг 1: пробел — радуга');
  ok(r.thunder.flash === 60 && r.thunder.events === 1 && r.thunder.says.some(s => /гром/i.test(s)), 'шаг 1: клавиша 3 — гром (вспышка, реплика облака)', r.thunder.says);
  ok(r.hats === 1 && r.hatValue === '20' && r.hatMenu === 'TIMER', 'шаг 2: у «Солнца» один блок «когда таймер > 20»');
  ok(r.at6 === 'Солнечно' && r.baseSay > 19.8 && r.baseSay < 20.6 && r.base > 21.8 && r.base < 22.6, 'шаг 3 до правки: на 20-й секунде реплика солнца, на 22-й радуга', [r.baseSay, r.base]);
  ok(r.afterFlag === 'Солнечно' && r.changedSay > 4.8 && r.changedSay < 5.6 && r.changed > 6.8 && r.changed < 7.6, 'шаг 3 после правки 20 → 5: на 5-й секунде реплика солнца, на 7-й радуга', [r.changedSay, r.changed]);
  ok(r.changedSays.includes('Событие таймера: прошло 20 секунд!'), 'реплика солнца по-прежнему говорит «прошло 20 секунд» — так и сказано в ответах');
  ok(r.wind['4'].moved > 100 && r.wind['1'].moved < 20 && r.wind['2'].moved < 20 && r.wind['3'].moved < 20, '«Хочу ещё»: ветер (облако улетает) только по клавише 4', Object.fromEntries(Object.entries(r.wind).map(([k, v]) => [k, v.moved])));
  await p.close();
  }

  // ---------- УРОК 2 ----------
  if (want(2)) {
  console.log('\n== Урок 2. Проведи ракету к маяку');
  p = await game(env, '02-motion.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const R = G.sprite('Ракета'), M = G.sprite('Маяк');
    const keys = { 'ArrowUp': [0, 1], 'ArrowDown': [0, -1], 'ArrowRight': [1, 0], 'ArrowLeft': [-1, 0] };
    G.flag(); await G.wait(400);
    // шаг 1: летим стрелками к маяку, пока не соберём 5
    const t0 = Date.now(); let held = null; o.crashes = 0;
    while (G.v('Маяки') < 5 && Date.now() - t0 < 120000) {
      const dx = M.x - R.x, dy = M.y - R.y; const want = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'ArrowRight' : 'ArrowLeft') : (dy > 0 ? 'ArrowUp' : 'ArrowDown');
      if (want !== held) { if (held) G.hold(held, false); G.hold(want, true); held = want }
      await G.wait(30);
    }
    if (held) G.hold(held, false);
    o.beacons = G.v('Маяки'); o.secs = Math.round((Date.now() - t0) / 1000); o.crashes = G.says.filter(s => /астероид! Возвращаюсь/.test(s.text)).length; o.lastSay = G.says.filter(s => /Маяков собрано/.test(s.text)).pop();
    // шаг 2
    const moves = G.blocks('Ракета', 'motion_movesteps'); o.steps = moves.map(b => b.inputs.STEPS.block === b.inputs.STEPS.shadow ? G.getNum('Ракета', b, 'STEPS') : 'выражение');
    const six = moves.filter(b => G.getNum('Ракета', b, 'STEPS') === '6'); o.six = six.length;
    // скорость по направлениям: смещение за 8 кадров
    const frames = G.frames;
    const speed = async key => { for (let i = 0; i < 6; i++) { const c0 = G.says.filter(s => /астероид! Возвращаюсь/.test(s.text)).length; R.setXY(0, 0); await frames(2); const x0 = R.x, y0 = R.y; const f0 = G.frame; G.hold(key, true); await frames(8); const d = Math.hypot(R.x - x0, R.y - y0), n = G.frame - f0; G.hold(key, false); await frames(2); if (G.says.filter(s => /астероид! Возвращаюсь/.test(s.text)).length === c0) return Math.round(d / n) } return null };
    o.before = {}; for (const k in keys) o.before[k] = await speed(k);
    // шаг 3: в одном блоке 6 → 20 (берём блок под «стрелка вправо»)
    const parentKey = b => { let par = R.blocks._blocks[b.parent]; while (!(par.inputs && par.inputs.CONDITION)) par = R.blocks._blocks[par.parent]; const cond = R.blocks._blocks[par.inputs.CONDITION.block]; const menu = R.blocks._blocks[cond.inputs.KEY_OPTION.block]; return menu.fields.KEY_OPTION.value };
    o.sixKeys = six.map(parentKey); const right = six.find(b => parentKey(b) === 'right arrow'); G.setNum('Ракета', right, 'STEPS', 20);
    o.after = {}; for (const k in keys) o.after[k] = await speed(k);
    // «Хочу ещё»: пробел и клавиши 0–9
    o.tricks = {}; G.mouse(120, 90);
    for (const k of [' ', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']) { R.setXY(-60, -60); await frames(2); const s0 = [R.x, R.y, R.direction]; let ch = 0; const f = () => { if (Math.abs(R.x - s0[0]) > 1 || Math.abs(R.y - s0[1]) > 1 || Math.abs(R.direction - s0[2]) > 1) ch++ }; G.onFrame = f; G.says.length = 0; await G.key(k); await G.wait(1500); G.onFrame = null; o.tricks[k === ' ' ? 'пробел' : k] = { moved: ch > 0, says: G.says.filter(s => s.who === 'Ракета').map(s => s.text) } }
    return o;
  });
  console.log(JSON.stringify(r));
  ok(r.beacons >= 5, 'шаг 1: стрелками можно собрать 5 маяков', { секунд: r.secs, столкновений: r.crashes, реплика: r.lastSay && r.lastSay.text });
  ok(r.six === 4 && r.sixKeys.slice().sort().join() === 'down arrow,left arrow,right arrow,up arrow', 'шаг 2: блок «идти 6 шагов» встречается 4 раза — по одному на стрелку', r.steps);
  ok(Object.values(r.before).every(v => v === 6), 'до правки: по 6 шагов за кадр в каждую сторону', r.before);
  ok(r.after.ArrowRight === 20 && r.after.ArrowLeft === 6 && r.after.ArrowUp === 6 && r.after.ArrowDown === 6, 'шаг 3: после 6 → 20 быстрее только та сторона, чей блок изменён', r.after);
  ok(Object.values(r.tricks).every(v => v.moved || v.says.length), '«Хочу ещё»: пробел и каждая клавиша 0–9 что-то делают', Object.fromEntries(Object.entries(r.tricks).map(([k, v]) => [k, v.says[0] || (v.moved ? 'движение' : '—')])));
  await p.close();
  }

  // ---------- УРОК 3 ----------
  if (want(3)) {
  console.log('\n== Урок 3. Театр одного артиста');
  p = await game(env, '03-looks.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const A = G.sprite('Артист');
    G.flag(); await G.wait(700);
    o.moods = {}; for (const k of ['1', '2', '3', '4']) { G.says.length = 0; await G.key(k); await G.wait(250); o.moods[k] = [G.costume('Артист'), (G.says.pop() || {}).text] }
    let hidden = false, ghost = 0; const iv = setInterval(() => { hidden = hidden || !A.visible; ghost = Math.max(ghost, A.effects.ghost) }, 10); await G.key('5'); await G.wait(1800); clearInterval(iv); o.trick = { hidden, ghost, visibleAfter: A.visible, ghostAfter: A.effects.ghost };
    // шаг 2
    const bs = G.blocks('Артист', 'looks_changesizeby'); o.sizes = bs.map(b => G.getNum('Артист', b, 'CHANGE')); const ten = bs.filter(b => G.getNum('Артист', b, 'CHANGE') === '10'); o.ten = ten.length;
    o.hat = A.blocks._blocks[ten[0].parent].fields.KEY_OPTION.value;
    G.flag(); await G.wait(500); const s0 = A.size; await G.key('ArrowUp'); await G.wait(200); o.up = [s0, A.size];
    // шаг 3: 10 → 50, три нажатия
    G.setNum('Артист', ten[0], 'CHANGE', 50);
    const run = async flag => { if (flag) { G.flag(); await G.wait(500) } const from = A.size; for (let i = 0; i < 3; i++) { await G.key('ArrowUp'); await G.wait(200) } const b = G.renderer.getBounds(A.drawableID); return { from, to: A.size, bounds: { left: Math.round(b.left), right: Math.round(b.right), top: Math.round(b.top), bottom: Math.round(b.bottom) }, think: (G.says.filter(s => s.who === 'Артист' && /Размер/.test(s.text)).pop() || {}).text } };
    o.noFlag = await run(false); o.withFlag = await run(true);
    return o;
  });
  await shot(p, 'l3-size');
  const r3b = await p.evaluate(async () => {
    const o = {}; const A = G.sprite('Артист');
    await G.key(' '); await G.wait(300); o.reset = A.size;
    // «Хочу ещё»: куда попадает клик
    const who = (x, y) => { const id = G.renderer.pick(x + 240, 180 - y); const t = G.vm.runtime.targets.find(t => t.drawableID === id); return t ? t.getName() : 'сцена' };
    G.flag(); await G.wait(6500);
    o.clicks = [];
    for (const [x, y, name] of [[75, -40, 'вплотную справа от артиста'], [0, 30, 'прямо над артистом'], [0, 70, 'высоко над артистом'], [-200, 0, 'занавес слева'], [200, -20, 'занавес справа']]) { const b0 = G.backdrop(); const hit = who(x, y); await G.click(x, y); await G.wait(500); o.clicks.push({ name, x, y, hit, changed: G.backdrop() !== b0, backdrop: G.backdrop(), costume: G.costume('Артист') }) }
    let pix = 0, whirl = 0; const iv = setInterval(() => { pix = Math.max(pix, A.effects.pixelate); whirl = Math.max(whirl, A.effects.whirl) }, 10); await G.key('7'); await G.wait(1600); clearInterval(iv); o.fx = { pix, whirl };
    const b0 = G.backdrop(); await G.key('6'); await G.wait(300); o.key6 = [b0, G.backdrop()];
    return o;
  });
  console.log(JSON.stringify(r), JSON.stringify(r3b));
  ok(r.moods['1'][0] === 'Радость' && r.moods['2'][0] === 'Грусть' && r.moods['3'][0] === 'Удивление' && r.moods['4'][0] === 'Спокойствие', 'шаг 1: клавиши 1–4 меняют настроение', Object.values(r.moods).map(x => x[0]));
  ok(r.trick.hidden && r.trick.ghost === 100 && r.trick.visibleAfter && r.trick.ghostAfter === 0, 'шаг 1: клавиша 5 — артист исчезает и возвращается');
  ok(r.ten === 1 && r.hat === 'up arrow' && r.up[0] === 120 && r.up[1] === 130, 'шаг 2: блок «изменить размер на 10» один, запускается стрелкой вверх', r.sizes);
  ok(r.withFlag.from === 120 && r.withFlag.to === 270, 'шаг 3: после флажка три нажатия дают размер 270', r.withFlag);
  ok(r.noFlag.to === r.noFlag.from + 150, 'без флажка размер растёт на 150 от того, что было, — поэтому в письме «нажми флажок»', r.noFlag);
  ok(r3b.reset === 120, 'пробел возвращает размер 120');
  ok(r3b.clicks.filter(c => /артист/.test(c.name) && c.hit === 'Прожектор' && !c.changed).length === 2, 'клик рядом с артистом попадает в прожектор и декорацию не меняет — поэтому в письме «кликни по занавесу сбоку»', r3b.clicks.map(c => c.name + ': ' + c.hit));
  ok(r3b.clicks.find(c => c.name === 'занавес слева').changed && r3b.clicks.find(c => c.name === 'занавес справа').changed, '«Хочу ещё»: клик по занавесу сбоку меняет декорацию');
  ok(r3b.fx.pix === 25 && r3b.fx.whirl === 150, '«Хочу ещё»: клавиша 7 включает спецэффекты');
  ok(r3b.key6[0] !== r3b.key6[1], 'клавиша 6 тоже меняет декорацию');
  await p.close();
  }

  // ---------- УРОК 4 ----------
  if (want(4)) {
  console.log('\n== Урок 4. Музыка из «Звёздных войн»');
  p = await game(env, '04-sound.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const S = G.sprite('Синтезатор'), D = G.sprite('Барабан');
    G.flag(); await G.wait(600); o.vol = [S.volume, D.volume, G.v('Громкость')];
    o.notes = []; for (const k of '12345678') { G.says.length = 0; await G.key(k); await G.wait(150); o.notes.push((G.says.filter(s => s.who === 'Синтезатор').pop() || {}).text) }
    o.buttons = []; for (const n of ['Имперский марш', 'Cantina Band', 'Главная тема']) { const t = G.sprite(n); G.says.length = 0; await G.click(t.x, t.y); await G.wait(400); o.buttons.push({ n, x: t.x, y: t.y, melody: G.v('Мелодия'), say: (G.says.filter(s => s.who === n).pop() || {}).text }) }
    await G.key(' '); await G.wait(300);
    const bs = G.blocks('Синтезатор', 'sound_changevolumeby'); o.vals = bs.map(b => G.getNum('Синтезатор', b, 'VOLUME')); const m10 = bs.filter(b => G.getNum('Синтезатор', b, 'VOLUME') === '-10'); o.m10 = m10.length; o.hat = S.blocks._blocks[m10[0].parent].fields.KEY_OPTION.value;
    o.drumVals = G.blocks('Барабан', 'sound_changevolumeby').map(b => G.getNum('Барабан', b, 'VOLUME'));
    const presses = async () => { G.flag(); await G.wait(600); let s = null, d = null; for (let i = 1; i <= 15; i++) { await G.key('ArrowDown'); await G.wait(120); if (s === null && S.volume === 0) s = i; if (d === null && D.volume === 0) d = i } return { synth: s, drum: d, shown: G.v('Громкость') } };
    o.before = await presses();
    G.setNum('Синтезатор', m10[0], 'VOLUME', -40);
    o.after = await presses();
    // мелодии берут громкость из переменной «Громкость»
    o.melodyVol = G.sprite('Имперский марш').volume;
    return o;
  });
  console.log(JSON.stringify(r));
  ok(r.vol[0] === 80 && r.vol[2] === 80, 'после флажка громкость синтезатора 80', r.vol);
  ok(r.notes.join() === 'До,Ре,Ми,Фа,Соль,Ля,Си,До высокая', 'шаг 1: клавиши 1–8 — восемь нот', r.notes);
  ok(r.buttons.every(b => b.melody === b.n && b.x > 150), 'шаг 1: три кнопки справа включают три мелодии', r.buttons.map(b => b.say));
  ok(r.m10 === 1 && r.hat === 'down arrow', 'шаг 2: блок «изменить громкость на -10» у синтезатора один, под стрелкой вниз', r.vals);
  ok(r.before.synth === 8, 'до правки: ноты замолкают за 8 нажатий', r.before);
  ok(r.after.synth === 2 && r.after.shown === 0, 'шаг 3: с числом −40 — за 2 нажатия', r.after);
  ok(r.before.drum === 9 && r.after.drum === 9, 'барабан затихает за 9 нажатий и до, и после правки: его громкость 90 и блок у него свой', { before: r.before.drum, after: r.after.drum });
  ok(r.melodyVol === 0, 'мелодии «Звёздных войн» замолкают вместе с нотами');
  await p.close();
  }

  // ---------- УРОК 5 ----------
  if (want(5)) {
  console.log('\n== Урок 5. Метеоритный дождь');
  p = await game(env, '05-control.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const S = G.sprite('Корабль'); const rt = G.vm.runtime;
    // игрок: уходит от ближайшего метеора, иначе идёт к звезде
    let held = null; const press = k => { if (k !== held) { if (held) G.hold(held, false); if (k) G.hold(k, true); held = k } };
    const play = () => { const cl = rt.targets.filter(t => !t.isOriginal && t.visible); const met = cl.filter(t => t.sprite.name === 'Метеор' && t.y < 90 && t.y > -160 && Math.abs(t.x - S.x) < 62).sort((a, b) => a.y - b.y)[0];
      if (met) return press(met.x >= S.x ? (S.x > -190 ? 'ArrowLeft' : 'ArrowRight') : (S.x < 190 ? 'ArrowRight' : 'ArrowLeft'));
      const star = cl.filter(t => t.sprite.name === 'Звезда' && t.y < 60)[0]; if (star && Math.abs(star.x - S.x) > 8) return press(star.x > S.x ? 'ArrowRight' : 'ArrowLeft'); press(null) };
    const session = async (secs, bonus) => { const res = { levels: [], bonus: null, minLives: 3 }; G.says.length = 0; G.flag(); const t0 = Date.now(); let lv = 1; await G.wait(100); const num = n => +G.v(n);
      while (Date.now() - t0 < secs * 1000 && G.v('Жизни') > 0) { play(); const l = num('Уровень'); if (l !== lv) { lv = l; res.levels.push([+l, Math.round((Date.now() - t0) / 100) / 10]) } res.minLives = Math.min(res.minLives, G.v('Жизни'));
        if (bonus && !res.bonus && G.v('Очки') >= 10) { const b = [num('Очки'), num('Жизни')]; await G.key(' '); await G.wait(150); res.bonus = { before: b, after: [num('Очки'), num('Жизни')] } }
        await G.wait(25) }
      press(null); res.score = num('Очки'); res.lives = num('Жизни'); res.level = num('Уровень'); res.secs = Math.round((Date.now() - t0) / 1000); return res };
    // бонус рано: очков меньше 10
    G.flag(); await G.wait(300); G.says.length = 0; await G.key(' '); await G.wait(300); o.early = [G.says.map(s => s.text), +G.v('Жизни')];
    o.base = await session(27, true);
    // шаг 2
    const ws = G.blocks('Stage', 'control_wait'); o.waits = ws.map(b => G.getNum('Stage', b, 'DURATION')); const w8 = ws.filter(b => G.getNum('Stage', b, 'DURATION') === '8'); o.w8 = w8.length; o.parent = G.stage().blocks._blocks[w8[0].parent].opcode;
    // шаг 3: 8 → 2
    G.setNum('Stage', w8[0], 'DURATION', 2); o.fast = await session(14, false);
    // игра кончается, если не уклоняться
    G.says.length = 0; G.flag(); await G.until(() => G.v('Жизни') < 1, 60000); await G.wait(500); o.over = G.says.filter(s => /Игра окончена/.test(s.text)).map(s => s.text);
    return o;
  });
  console.log(JSON.stringify(r));
  ok(r.base.levels.length === 3 && r.base.levels.every(([l, t], i) => l === i + 2 && Math.abs(t - 8 * (i + 1)) < 0.6), 'шаг 1 и до правки: уровень растёт каждые 8 секунд', r.base.levels);
  ok(r.w8 === 1 && r.parent === 'control_repeat_until', 'шаг 2: у сцены один блок «ждать 8 секунд», стоит внутри «повторять пока не»', r.waits);
  ok(r.fast.levels.length === 5 && r.fast.levels.every(([l, t], i) => l === i + 2 && Math.abs(t - 2 * (i + 1)) < 0.6), 'шаг 3: с числом 2 уровень растёт каждые 2 секунды и за 10 секунд доходит до 6', r.fast.levels);
  ok(/Для бонуса нужно 10 очков/.test(r.early[0].join()) && r.early[1] === 3, '«Хочу ещё»: без 10 очков пробел ничего не даёт', r.early[0]);
  // пока нажимается пробел, игра идёт дальше: за это время может прилететь очко за метеор или пять за звезду
  ok(r.base.bonus && r.base.bonus.after[0] >= r.base.bonus.before[0] - 10 && r.base.bonus.after[0] <= r.base.bonus.before[0] - 4 && r.base.bonus.after[1] === r.base.bonus.before[1] + 1, '«Хочу ещё»: пробел меняет 10 очков на одну жизнь', r.base.bonus);
  ok(r.over.length === 1, 'если не уклоняться, игра заканчивается сообщением с очками', r.over);
  console.log('   игра за 27 секунд:', JSON.stringify({ очки: r.base.score, жизни: r.base.lives, уровень: r.base.level }), '· быстрая:', JSON.stringify({ очки: r.fast.score, жизни: r.fast.lives }));
  await p.close();
  }

  // ---------- УРОК 6 ----------
  if (want(6)) {
  console.log('\n== Урок 6. Научи героя чувствовать');
  p = await game(env, '06-sensing.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const T = G.sprite('Следопыт'), K = G.sprite('Клад');
    const dist = () => Math.hypot(T.x - K.x, T.y - K.y);
    // мышь стоит на самом следопыте, чтобы он не пошёл искать раньше времени; если клад случайно оказался под ним — начинаем заново
    const start = async () => { for (;;) { G.says.length = 0; G.asks.length = 0; G.mouse(0, 0); G.flag(); await G.until(() => G.asks.length > 0, 5000); const q = G.asks[0]; G.answer('Аня'); await G.until(() => G.says.some(s => /Веди меня мышкой/.test(s.text)), 3000); const hi = G.says.find(s => /Веди меня/.test(s.text)).text; await G.wait(3500); if (+G.v('Найдено') === 0 && dist() > 150) return [q, hi] } };
    // точка на расстоянии d от клада, в сторону центра сцены
    const at = d => { const a = Math.atan2(-K.y, -K.x - 0.001); return [K.x + d * Math.cos(a), K.y + d * Math.sin(a)] };
    // подводим следопыта к кладу и записываем (расстояние, подсказка) на каждом кадре
    const approach = async () => { const log = []; const found0 = G.v('Найдено'); G.mouse(...at(200)); await G.wait(1200);
      G.onFrame = () => log.push([Math.round(dist() * 10) / 10, G.v('Подсказка'), G.v('Найдено')]);
      for (let d = 200; d >= 0 && G.v('Найдено') === found0; d -= 2) { G.mouse(...at(d)); await G.frames(3) }
      G.onFrame = null; return log.filter(x => x[2] === found0) };
    o.intro = await start(); o.kghost = K.effects.ghost; o.kvisible = K.visible;
    const log = await approach(); await G.wait(900);
    o.found = +G.v('Найдено'); o.kghostFound = K.effects.ghost; o.foundSay = (G.says.filter(s => /Клад найден/.test(s.text)).pop() || {}).text;
    o.minDist = Math.min(...log.map(x => x[0])); o.hints = [...new Set(log.map(x => x[1]))];
    // подсказка считается до шага следующего кадра, поэтому допускаем сдвиг на один кадр
    const expect = (d, a, b) => d < a ? 'Горячо!' : d < b ? 'Тепло' : 'Холодно';
    o.wrong = log.filter(([d, h]) => h !== expect(d, 80, 130)).length; o.n = log.length;
    o.hotFrames = log.filter(x => x[1] === 'Горячо!').length; o.hotFrom = Math.max(0, ...log.filter(x => x[1] === 'Горячо!').map(x => x[0])); o.warmFrom = Math.max(0, ...log.filter(x => x[1] === 'Тепло').map(x => x[0]));
    // шаг 2
    const ds = G.blocks('Следопыт', 'sensing_distanceto'); const menu = b => T.blocks._blocks[b.inputs.DISTANCETOMENU.block].fields.DISTANCETOMENU.value; o.dists = ds.map(menu);
    const lts = G.blocks('Следопыт', 'operator_lt'); o.thresholds = lts.map(b => G.getNum('Следопыт', b, 'OPERAND2'));
    // шаг 3: 45 → 150
    G.setNum('Следопыт', lts.find(b => G.getNum('Следопыт', b, 'OPERAND2') === '80'), 'OPERAND2', 150);
    await start(); G.mouse(...at(230)); await G.wait(1200); const log2 = await approach(); o.hints2 = [...new Set(log2.map(x => x[1]))]; o.hotFrom2 = Math.max(0, ...log2.filter(x => x[1] === 'Горячо!').map(x => x[0])); o.wrong2 = log2.filter(([d, h]) => h !== (d < 150 ? 'Горячо!' : 'Холодно')).length;
    // «Хочу ещё»: в блоке «идти» 6 → 2
    const mv = G.blocks('Следопыт', 'motion_movesteps'); o.moves = mv.length; const div = T.blocks._blocks[mv[0].inputs.STEPS.block]; o.div = [div.opcode, G.getNum('Следопыт', div, 'NUM2')];
    const race = async () => { await start(); G.mouse(-200, -150); await G.wait(1200); const f0 = G.frame; G.mouse(200, 120); let n = null; const x0 = T.x, y0 = T.y; const total = Math.hypot(200 - x0, 120 - y0); await G.until(() => { if (Math.hypot(200 - T.x, 120 - T.y) < total * 0.2) { n = G.frame - f0; return true } }, 4000); return n };
    o.slow = await race(); G.setNum('Следопыт', div, 'NUM2', 2); o.fastRace = await race();
    // с какого расстояния следопыт касается клада, если подходить с разных сторон
    G.vm.stopAll(); await G.wait(100); K.setXY(0, 0); K.setSize(70); T.setSize(70); o.touch = [];
    for (let a = 0; a < 360; a += 30) { const rad = a * Math.PI / 180; let at0 = 0; for (let d = 120; d > 0; d--) { T.setXY(d * Math.cos(rad), d * Math.sin(rad)); T.setDirection(90 - (a + 180)); if (T.isTouchingSprite('Клад')) { at0 = d; break } } o.touch.push([a, at0]) }
    return o;
  });
  console.log(JSON.stringify(r));
  ok(/Как тебя зовут/.test(r.intro[0]) && /Привет, Аня!/.test(r.intro[1]), 'шаг 1: игра спрашивает имя и здоровается', r.intro);
  ok(r.kghost === 100 && r.kvisible && r.found === 1 && r.kghostFound === 0 && /Клад найден! Секунд: \d+/.test(r.foundSay || ''), 'шаг 1: невидимый клад находится касанием, игра называет секунды', r.foundSay);
  ok(r.wrong === 0 && r.hints.slice().sort().join() === 'Горячо!,Тепло,Холодно', 'до правки: «Холодно» дальше 130, «Тепло» от 130 до 80, «Горячо!» ближе 80', { 'Тепло с': r.warmFrom, 'Горячо с': r.hotFrom, 'кадров Горячо': r.hotFrames, 'клад взят на расстоянии': r.minDist });
  ok(r.dists.filter(x => x === 'Клад').length === 3, 'шаг 2: блок «расстояние до Клад» встречается у следопыта 3 раза', r.dists);
  ok(r.thresholds.slice().sort().join() === '130,80', 'шаг 3: число 80 стоит рядом с одним из этих блоков, второе число — 130', r.thresholds);
  ok(r.hotFrames > 0 && Math.max(...r.touch.map(x => x[1])) < 70, '«Горячо!» видно до находки с любой стороны: клад берётся с расстояния меньше 80', { 'касание по сторонам, шагов': r.touch.map(x => x[1]) });
  ok(r.wrong2 === 0 && r.hints2.slice().sort().join() === 'Горячо!,Холодно' && r.hotFrom2 > 140, 'шаг 3: с числом 150 «Горячо!» появляется уже со 150, «Тепло» пропадает', { подсказки: r.hints2, 'Горячо с': r.hotFrom2 });
  ok(r.moves === 1 && r.div[0] === 'operator_divide' && r.div[1] === '6', '«Хочу ещё»: блок «идти» у следопыта один, в нём деление на 6', r.div);
  ok(r.fastRace < r.slow, '«Хочу ещё»: с числом 2 следопыт идёт быстрее', { 'кадров с 6': r.slow, 'кадров с 2': r.fastRace });
  await p.close();
  }

  // ---------- УРОК 7 ----------
  if (want(7)) {
  console.log('\n== Урок 7. Обыграй оракула');
  p = await game(env, '07-operators.sb3');
  r = await p.evaluate(async () => {
    const o = {};
    const solve = q => { const m = /^(\d+) (.) (\d+) = \?$/.exec(q); if (!m) return null; const a = +m[1], b = +m[3]; return { q, a, b, op: m[2], res: m[2] === '+' ? a + b : m[2] === '−' ? a - b : m[2] === '×' ? a * b : a / b } };
    const round = async wrongAt => { const ex = []; G.says.length = 0; G.asks.length = 0; G.flag(); for (let i = 0; i < 5; i++) { await G.until(() => G.asks.length > i, 8000); const s = solve(G.asks[i]); ex.push(s); G.answer(String(i === wrongAt ? s.res + 1 : s.res)) } await G.until(() => G.says.some(x => /Результат/.test(x.text)), 8000); await G.wait(300); return { ex, score: G.v('Очки'), says: G.says.map(x => x.text) } };
    o.r1 = await round(-1); o.r2 = await round(2); o.r3 = await round(-1);
    // шаг 2
    const rs = G.blocks('Оракул', 'operator_random'); o.rands = rs.map(b => [G.getNum('Оракул', b, 'FROM'), G.getNum('Оракул', b, 'TO')]);
    // шаг 3: в одном 9 → 99
    G.setNum('Оракул', rs.find(b => G.getNum('Оракул', b, 'TO') === '9'), 'TO', 99);
    o.c1 = await round(-1); o.c2 = await round(-1); o.c3 = await round(-1);
    // «Хочу ещё»
    await G.wait(5500); G.says.length = 0; G.asks.length = 0; await G.clickSprite('Оракул'); await G.until(() => G.asks.length > 0, 3000); o.ask = G.asks[0]; G.answer('47'); await G.wait(11500); o.about = G.says.map(x => x.text);
    G.says.length = 0; G.asks.length = 0; await G.clickSprite('Оракул'); await G.until(() => G.asks.length > 0, 3000); G.answer('кот'); await G.wait(800); o.notNumber = G.says.map(x => x.text);
    return o;
  });
  const exs = x => x.ex.map(e => e.q.replace(' = ?', ''));
  const base = [...r.r1.ex, ...r.r2.ex, ...r.r3.ex], ch = [...r.c1.ex, ...r.c2.ex, ...r.c3.ex];
  console.log(JSON.stringify({ до: [r.r1, r.r2, r.r3].map(exs), после: [r.c1, r.c2, r.c3].map(exs), about: r.about, notNumber: r.notNumber, rands: r.rands, says2: r.r2.says }));
  ok(r.r1.score === 5 && r.r1.says.some(s => s === 'Результат: 5 из 5.') && base.every(e => e && Number.isInteger(e.res)), 'шаг 1: пять примеров, все решаются в целых числах, счёт «5 из 5»');
  ok(r.r2.score === 4 && r.r2.says.some(s => /^Многовато\. Правильно: \d+$/.test(s)), 'шаг 1: ошибку оракул замечает и называет правильный ответ', r.r2.says.filter(s => /Правильно|Результат/.test(s)));
  ok(r.rands.filter(x => x.join() === '2,9').length === 2 && r.rands.length === 3, 'шаг 2: блоков «выдать случайное от 2 до 9» два (третий — от 1 до 4)', r.rands);
  ok(base.every(e => e.b <= 9 && (e.op === '+' || e.op === '×' ? e.a <= 9 : true)), 'до правки: слагаемые и множители от 2 до 9', { 'самое большое число': Math.max(...base.map(e => Math.max(e.a, e.b))) });
  ok(Math.max(...ch.map(e => Math.max(e.a, e.b))) > 18 && ch.every(e => Number.isInteger(e.res)), 'шаг 3: с числом 99 примеры становятся заметно труднее', { 'самое большое число': Math.max(...ch.map(e => Math.max(e.a, e.b))) });
  ok(/целое число/.test(r.ask) && r.about.some(s => s === '47 — нечётное число.') && r.about.some(s => /семёрка/.test(s)) && r.about.some(s => /двузначное/.test(s)), '«Хочу ещё»: клик по оракулу — рассказ о числе', r.about);
  ok(r.notNumber.some(s => /Это не число/.test(s)), 'если написать не число, оракул просит попробовать ещё раз');
  await p.close();
  }

  // ---------- УРОК 8 ----------
  if (want(8)) {
  console.log('\n== Урок 8. Дневник желаний');
  p = await game(env, '08-data.sb3');
  r = await p.evaluate(async () => {
    const o = {}; const list = () => { for (const t of G.vm.runtime.targets) for (const v of Object.values(t.variables)) if (v.name === 'Мои желания') return v.value.slice() };
    const wishes = ['собака', 'новый велосипед', 'полететь на Луну', 'мороженое', 'своя игра', 'лишнее'];
    const fill = async () => { G.says.length = 0; G.asks.length = 0; G.flag(); let i = 0; while (i < 6) { const okq = await G.until(() => G.asks.length > i, 3500); if (!okq) break; G.answer(wishes[i]); i++ } await G.wait(300); return { asked: G.asks.slice(), list: list() } };
    o.base = await fill(); await G.wait(7200);
    G.says.length = 0; await G.key('6'); await G.wait(300); o.key6 = G.says.map(s => s.text);
    // шаг 2
    const D = G.sprite('Дневник'); const hatOf = b => { let x = b; while (x.parent) x = D.blocks._blocks[x.parent]; return x.opcode + (x.fields.KEY_OPTION ? ':' + x.fields.KEY_OPTION.value : '') };
    o.adds = G.blocks('Дневник', 'data_addtolist').map(hatOf); o.inserts = G.blocks('Дневник', 'data_insertatlist').map(hatOf);
    const reps = G.blocks('Дневник', 'control_repeat'); o.reps = reps.map(b => [hatOf(b), b.inputs.TIMES.block === b.inputs.TIMES.shadow ? G.getNum('Дневник', b, 'TIMES') : 'выражение']);
    // «Хочу ещё»: поиск и очистка
    const find = async w => { G.says.length = 0; G.asks.length = 0; await G.key('5'); await G.until(() => G.asks.length > 0, 2000); const q = G.asks[0]; G.answer(w); await G.wait(300); return [q, G.says.map(s => s.text)] };
    o.findWhole = await find('новый велосипед'); await G.wait(2000); o.findPart = await find('велосипед'); await G.wait(2000);
    G.says.length = 0; await G.key('0'); await G.wait(300); o.cleared = [list(), G.says.map(s => s.text), G.v('Счётчик')];
    // шаг 3: 3 → 5
    G.setNum('Дневник', reps.find(b => hatOf(b) === 'event_whenflagclicked'), 'TIMES', 5); await G.wait(1500);
    o.changed = await fill();
    return o;
  });
  await shot(p, 'l8-five');
  console.log(JSON.stringify(r));
  ok(r.base.asked.length === 3 && r.base.list.join('|') === 'собака|новый велосипед|полететь на Луну', 'шаг 1: дневник спрашивает три желания и записывает их в список', r.base.asked);
  ok(r.key6.length === 1 && /^Сегодня исполним: (собака|новый велосипед|полететь на Луну)$/.test(r.key6[0]), 'шаг 1: клавиша 6 выбирает одно желание из списка', r.key6);
  ok(r.adds.slice().sort().join() === 'event_whenflagclicked,event_whenkeypressed:1', 'шаг 2: блок «добавить ответ к Мои желания» встречается 2 раза — под флажком и под клавишей 1', { 'похожий блок «вставить»': r.inserts });
  ok(r.reps.find(x => x[0] === 'event_whenflagclicked')[1] === '3', 'шаг 3: под флажком стоит «повторить 3 раз»', r.reps);
  ok(r.changed.asked.length === 5 && r.changed.list.length === 5, 'шаг 3: с числом 5 дневник спрашивает пять желаний', r.changed.list);
  ok(/Найдено под номером 2/.test(r.findWhole[1].join()), '«Хочу ещё»: клавиша 5 находит желание, если написать его целиком', r.findWhole);
  ok(/Такого желания нет/.test(r.findPart[1].join()), 'по одному слову из желания поиск не находит — поэтому в письме «напиши его целиком»', r.findPart[1]);
  ok(r.cleared[0].length === 0 && /Дневник очищен/.test(r.cleared[1].join()) && r.cleared[2] == 0, '«Хочу ещё»: клавиша 0 стирает всё');
  await p.close();
  }

  await env.b.close(); env.srv.close(); process.exit(done() ? 1 : 0);
})().catch(e => { console.error('ERR', e); process.exit(1) });
