#!/usr/bin/env node
// Проходит разгадки практики (lessons/practice/*-solution.sb3) в настоящем движке Scratch:
// делает то, что написано в практике урока, и смотрит, что проект отвечает как надо.
// Заготовки (lessons/practice/*-start.sb3) загружает в движок и проверяет, что в них нет программы
// и что флажок и клавиши ничего не меняют.
//
// Нужен, когда меняется scripts/build-practice.py. В CI не запускается: ему нужны движок Scratch и браузер.
// Стенд тот же, что у checks/play-missions.js — подготовка и переменные окружения описаны там.
//
// Запуск из корня репозитория:
//   node checks/play-practice.js          — все восемь уроков, около двух минут
//   node checks/play-practice.js 2 6      — только уроки 2 и 6
//   PLAY_SHOTS=папка — снимки сцены каждой заготовки и разгадки
//
// Чего проверка не видит: звук (движок работает без звуковой карты, «играть звук до конца» не ждёт).
const { open, game, ok, done, shot } = require('./play-missions.js');
const STEMS = ['01-events', '02-motion', '03-looks', '04-sound', '05-control', '06-sensing', '07-operators', '08-data'];

(async () => {
  const env = await open();
  let p, r; const want = n => process.argv.length < 3 || process.argv.slice(2).includes(String(n));
  const solution = async n => { const page = await game(env, `practice/${STEMS[n - 1]}-solution.sb3`); return page };

  // ---------- Заготовки ----------
  for (let n = 1; n <= 8; n++) if (want(n)) {
    p = await game(env, `practice/${STEMS[n - 1]}-start.sb3`);
    r = await p.evaluate(async () => {
      const state = () => JSON.stringify(G.vm.runtime.targets.map(t => [t.getName(), t.x, t.y, t.visible, t.currentCostume, t.size, t.direction]));
      const before = state();
      G.flag(); await G.wait(300);
      for (const k of [' ', 'ArrowUp', 'ArrowRight', '1']) await G.key(k);
      for (const t of G.vm.runtime.targets) if (!t.isStage) await G.click(t.x, t.y);
      await G.wait(300);
      return {
        blocks: G.vm.runtime.targets.reduce((s, t) => s + Object.keys(t.blocks._blocks).length, 0),
        vars: G.vm.runtime.targets.reduce((s, t) => s + Object.keys(t.variables).length, 0),
        hidden: G.vm.runtime.targets.filter(t => !t.isStage && !t.visible).map(t => t.getName()),
        notes: G.vm.runtime.targets.map(t => Object.values(t.comments).map(c => c.text).join('')),
        same: before === state(), clones: G.vm.runtime.targets.filter(t => !t.isOriginal).length,
      };
    });
    await shot(p, `practice-${n}-start`);
    ok(r.blocks === 0 && r.vars === 0, `урок ${n}, заготовка: программы и переменных нет`, [r.blocks, r.vars]);
    ok(r.hidden.length === 0, `урок ${n}, заготовка: все герои видны на сцене`, r.hidden);
    ok(r.same && r.clones === 0, `урок ${n}, заготовка: флажок, клавиши и клики ничего не меняют`);
    ok(r.notes.every(t => /Заготовка/.test(t)) && r.notes.some(t => /Что собираем на уроке/.test(t)), `урок ${n}, заготовка: в заметке — шаги практики`);
    await p.close();
  }

  // ---------- УРОК 1 ----------
  if (want(1)) {
  console.log('\n== Урок 1. Солнце и дождь');
  p = await solution(1);
  r = await p.evaluate(async () => {
    const o = {};
    G.flag(); await G.wait(700); o.start = [G.backdrop(), G.sprite('Солнце').visible, G.sprite('Капля').visible, G.says.map(s => s.text)];
    let drops = 0; const iv = setInterval(() => { if (G.sprite('Капля').visible) drops++ }, 20);
    await G.wait(2200); await G.clickSprite('Облако'); await G.wait(700); o.rain = [G.backdrop(), G.sprite('Солнце').visible, drops > 0];
    await G.key(' '); await G.wait(500); clearInterval(iv); o.rainbow = [G.backdrop(), G.sprite('Солнце').visible, G.sprite('Капля').visible];
    G.flag(); await G.wait(500); o.again = G.backdrop();
    return o;
  });
  await shot(p, 'practice-1-solution');
  console.log(JSON.stringify(r));
  ok(r.start[0] === 'Солнечно' && r.start[1] && !r.start[2] && r.start[3].includes('Доброе утро!'), 'флажок — солнце выходит и здоровается, капля спрятана');
  ok(r.rain[0] === 'Дождливо' && !r.rain[1] && r.rain[2], 'клик по облаку — дождь: фон «Дождливо», солнце спряталось, падает капля');
  ok(r.rainbow[0] === 'Радуга' && r.rainbow[1] && !r.rainbow[2], 'пробел — радуга: фон «Радуга», солнце вернулось, капля спряталась');
  ok(r.again === 'Солнечно', 'флажок возвращает солнечную погоду');
  await p.close();
  }

  // ---------- УРОК 2 ----------
  if (want(2)) {
  console.log('\n== Урок 2. Лабиринт');
  p = await solution(2);
  r = await p.evaluate(async () => {
    const o = {}, bug = () => G.sprite('Жук'), pos = () => [Math.round(bug().x), Math.round(bug().y)];
    const go = async (key, n) => { for (let i = 0; i < n; i++) { await G.key(key, 40); } await G.frames(2) };
    G.flag(); await G.wait(300); o.start = pos();
    // стены: из стартового угла нельзя уйти вверх и влево, а вниз — только до стены
    await go('ArrowUp', 6); o.up = pos(); await go('ArrowLeft', 6); o.left = pos(); await go('ArrowDown', 12); o.down = pos();
    G.flag(); await G.wait(300);
    // дорога к кристаллу
    const route = [['ArrowRight', 24], ['ArrowDown', 9], ['ArrowLeft', 24], ['ArrowDown', 9], ['ArrowRight', 16], ['ArrowDown', 9], ['ArrowRight', 23]];
    o.path = [];
    for (const [key, n] of route) { await go(key, n); o.path.push(pos()) }
    await G.until(() => G.says.some(s => s.text === 'Победа!'), 3000); o.win = G.says.map(s => s.text); o.touching = bug().isTouchingSprite('Стены');
    return o;
  });
  await shot(p, 'practice-2-solution');
  console.log(JSON.stringify(r));
  ok(r.start.join() === '-196,134', 'флажок — жук на старте', r.start);
  ok(r.up[1] <= 154 && r.left[0] >= -216 && r.down[1] >= 104, 'жук не проходит сквозь стены вокруг старта', [r.up, r.left, r.down]);
  ok(r.path.map(x => x.join()).join(' ') === '44,134 44,44 -196,44 -196,-46 -36,-46 -36,-136 194,-136', 'жук проходит дорогу к кристаллу', r.path);
  ok(r.win.includes('Победа!') && !r.touching, 'у кристалла жук говорит «Победа!»', r.win);
  await p.close();
  }

  // ---------- УРОК 3 ----------
  if (want(3)) {
  console.log('\n== Урок 3. История с персонажем');
  p = await solution(3);
  r = await p.evaluate(async () => {
    const o = { costumes: [], star: [] }; let last = '';
    const iv = setInterval(() => { const c = G.costume('Кубик'); if (c !== last) { last = c; o.costumes.push(c) } }, 20);
    G.flag(); await G.wait(400); o.star.push(G.sprite('Звёздочка').visible); o.backdrop0 = G.backdrop();
    await G.until(() => G.says.some(s => s.text === 'Я здесь!'), 15000); await G.wait(200); o.star.push(G.sprite('Звёздочка').visible); o.atCall = G.costume('Кубик');
    await G.until(() => G.says.some(s => /снова вместе/.test(s.text)), 10000); await G.wait(2300); clearInterval(iv);
    o.says = G.says.map(s => s.who + ': ' + s.text); o.backdrop = G.backdrop(); o.size = Math.round(G.sprite('Кубик').size);
    return o;
  });
  await shot(p, 'practice-3-solution');
  console.log(JSON.stringify(r));
  ok(r.costumes.join() === 'Радость,Грусть,Удивление,Радость', 'Кубик меняет костюмы: радость → грусть → удивление → радость', r.costumes);
  ok(r.star.join() === 'false,true' && r.atCall === 'Грусть', 'Звёздочка спрятана и появляется по сообщению; Кубик ждёт её ответа', r.star);
  ok(r.says.length === 6 && r.says[3] === 'Звёздочка: Я здесь!', 'история рассказана по порядку', r.says);
  ok(r.backdrop0 === 'Поляна' && r.backdrop === 'Радуга' && r.size === 110, 'в конце фон «Радуга», размер Кубика вернулся', [r.backdrop0, r.backdrop, r.size]);
  await p.close();
  }

  // ---------- УРОК 4 ----------
  if (want(4)) {
  console.log('\n== Урок 4. Мелодия на клавишах');
  p = await solution(4);
  r = await p.evaluate(async () => {
    const o = {}, robot = G.sprite('Робот');
    G.flag(); await G.wait(300); o.start = [robot.volume, G.costume('Робот'), robot.sprite.sounds.map(s => s.name)];
    o.keys = [];
    for (const k of ['1', '2', '3', '4', '5']) { let sang = false; const iv = setInterval(() => { if (G.costume('Робот') === 'Поёт') sang = true }, 2); await G.key(k); await G.wait(250); clearInterval(iv); o.keys.push([sang, G.costume('Робот')]) }
    for (let i = 0; i < 3; i++) await G.key('ArrowDown'); o.quiet = robot.volume;
    for (let i = 0; i < 5; i++) await G.key('ArrowUp'); o.loud = robot.volume;
    await G.key(' '); await G.wait(1500); o.song = G.costume('Робот');
    o.plays = Object.values(robot.blocks._blocks).filter(b => b.opcode === 'sound_playuntildone').length;
    return o;
  });
  await shot(p, 'practice-4-solution');
  console.log(JSON.stringify(r));
  ok(r.start[0] === 100 && r.start[1] === 'Молчит' && r.start[2].join() === 'До,Ре,Ми,Фа,Соль', 'флажок: громкость 100, робот молчит, у него пять нот', r.start);
  ok(r.keys.every(k => k[1] === 'Молчит'), 'клавиши 1–5: после ноты робот снова молчит', r.keys);
  ok(r.quiet === 70 && r.loud === 100, 'стрелки меняют громкость на 10', [r.quiet, r.loud]);
  ok(r.song === 'Молчит' && r.plays === 12, 'пробел: после песенки робот замолкает; блоков «играть звук до конца» — 12', [r.song, r.plays]);
  await p.close();
  }

  // ---------- УРОК 5 ----------
  if (want(5)) {
  console.log('\n== Урок 5. Салют из клонов');
  p = await solution(5);
  r = await p.evaluate(async () => {
    const o = {}, clones = () => G.vm.runtime.targets.filter(t => !t.isOriginal);
    G.flag(); await G.wait(300); o.hidden = !G.sprite('Искра').visible;
    let top = -999, most = 0, ghost = 0, low = 999; const colors = new Set();
    const iv = setInterval(() => { const c = clones(); most = Math.max(most, c.length); for (const t of c) { top = Math.max(top, t.y); low = Math.min(low, t.y); ghost = Math.max(ghost, t.effects.ghost); colors.add(Math.round(t.effects.color)) } }, 15);
    await G.wait(6000); clearInterval(iv);
    Object.assign(o, { top, low, most, ghost, colors: colors.size, now: clones().length });
    return o;
  });
  await shot(p, 'practice-5-solution');
  console.log(JSON.stringify(r));
  ok(r.hidden && r.now >= 2, 'флажок: сама искра спрятана, клоны появляются', r.now);
  ok(r.low <= -124 && r.top > 60 && r.top <= 68, 'клоны летят снизу вверх и не поднимаются выше вспышки', [r.low, r.top]);
  ok(r.ghost >= 90 && r.colors >= 5, 'клон вспыхивает (прозрачность растёт), цвета разные', [r.ghost, r.colors]);
  ok(r.most <= 8, 'клоны удаляются: на сцене их не больше восьми', r.most);
  await p.close();
  }

  // ---------- УРОК 6 ----------
  if (want(6)) {
  console.log('\n== Урок 6. Викторина');
  p = await solution(6);
  r = await p.evaluate(async () => {
    const round = async answers => { G.says.length = 0; G.asks.length = 0; G.flag(); for (let i = 0; i < answers.length; i++) { await G.until(() => G.asks.length > i, 8000); G.answer(answers[i]) } await G.until(() => G.says.some(s => /окончена/.test(s.text)), 9000); return { asks: G.asks.slice(), says: G.says.filter(s => s.type === 'say' && !G.asks.includes(s.text)).map(s => s.text) } };
    const o = {};
    o.right = await round(['Аня', 'Париж', '8']);
    o.lower = await round(['Аня', 'париж', '8']);
    o.wrong = await round(['Боря', 'Лондон', '6']);
    G.mouse(100, 50); await G.frames(3); const s = G.sprite('Звёздочка'); o.star = [Math.round(s.x), Math.round(s.y)];
    return o;
  });
  await shot(p, 'practice-6-solution');
  console.log(JSON.stringify(r));
  ok(r.right.asks.join('|') === 'Как тебя зовут?|Столица Франции?|Сколько ног у паука?', 'робот спрашивает имя и задаёт два вопроса', r.right.asks);
  ok(r.right.says.join('|') === 'Привет, Аня! Начинаем викторину.|Верно!|Верно!|Викторина окончена. Спасибо за игру!', 'верные ответы — «Верно!», приветствие по имени', r.right.says);
  ok(r.lower.says.filter(s => s === 'Верно!').length === 2, '«париж» с маленькой буквы тоже верно', r.lower.says);
  ok(r.wrong.says.join('|') === 'Привет, Боря! Начинаем викторину.|Нет. Столица Франции — Париж.|Нет. У паука 8 ног.|Викторина окончена. Спасибо за игру!', 'неверные ответы — робот называет правильный', r.wrong.says);
  ok(r.star.join() === '100,50', 'Звёздочка переходит к указателю мыши', r.star);
  await p.close();
  }

  // ---------- УРОК 7 ----------
  if (want(7)) {
  console.log('\n== Урок 7. Калькулятор удачи');
  p = await solution(7);
  r = await p.evaluate(async () => {
    const o = { rounds: [] };
    for (let i = 0; i < 4; i++) {
      G.says.length = 0; G.asks.length = 0; G.flag(); await G.until(() => G.asks.length > 0, 5000); G.answer('Аня');
      await G.until(() => G.says.filter(s => !G.asks.includes(s.text)).length > 1, 8000);
      o.rounds.push({ says: G.says.filter(s => !G.asks.includes(s.text)).map(s => s.text), luck: +G.v('Удача') });
    }
    // проверка порога: подставляем удачу сами
    const set = G.blocks('Кристалл', 'data_setvariableto')[0], rnd = G.sprite('Кристалл').blocks._blocks[set.inputs.VALUE.block];
    o.range = [G.getNum('Кристалл', rnd, 'FROM'), G.getNum('Кристалл', rnd, 'TO')];
    o.edge = {};
    for (const v of [80, 81]) {
      G.setNum('Кристалл', rnd, 'FROM', v); G.setNum('Кристалл', rnd, 'TO', v);
      G.says.length = 0; G.asks.length = 0; G.flag(); await G.until(() => G.asks.length > 0, 5000); G.answer('Аня');
      await G.until(() => G.says.filter(s => !G.asks.includes(s.text)).length > 1, 8000); o.edge[v] = G.says.filter(s => !G.asks.includes(s.text)).map(s => s.text);
    }
    return o;
  });
  await shot(p, 'practice-7-solution');
  console.log(JSON.stringify(r));
  ok(r.rounds.every(x => x.says[0] === `Аня, твоя удача: ${x.luck}` && x.luck >= 1 && x.luck <= 100 && Number.isInteger(x.luck)), 'кристалл называет имя и удачу — то же число, что в переменной', r.rounds.map(x => x.luck));
  ok(r.rounds.every(x => (x.luck > 80) === (x.says[1] === 'Ты везунчик!')), '«Ты везунчик!» — только когда удача больше 80');
  ok(r.range.join() === '1,100', 'случайное число — от 1 до 100', r.range);
  ok(r.edge[80][1] !== 'Ты везунчик!' && r.edge[81][1] === 'Ты везунчик!', 'граница: 80 — ещё нет, 81 — везунчик', r.edge);
  await p.close();
  }

  // ---------- УРОК 8 ----------
  if (want(8)) {
  console.log('\n== Урок 8. Список покупок');
  p = await solution(8);
  r = await p.evaluate(async () => {
    const o = {}, list = () => G.v('Покупки').slice();
    const shown = () => { const m = [...G.vm.runtime.getMonitorState().values()].find(m => m.params && m.params.LIST === 'Покупки'); return !!(m && m.visible) };
    G.flag(); await G.until(() => G.asks.length > 0, 6000); o.hiddenAtStart = !shown();
    const items = ['хлеб', 'молоко', 'яблоки'];
    for (let i = 0; i < 3; i++) { await G.until(() => G.asks.length > i, 4000); G.answer(items[i]) }
    await G.until(() => G.says.some(s => /Сначала купим/.test(s.text)), 8000);
    o.asks = G.asks.slice(); o.list = list(); o.shown = shown(); o.says = G.says.filter(s => !G.asks.includes(s.text)).map(s => s.text);
    await G.wait(2300); G.asks.length = 0; await G.key(' '); await G.until(() => G.asks.length > 0, 3000); o.more = G.asks[0]; G.answer('сыр'); await G.wait(300); o.list4 = list();
    G.asks.length = 0; G.flag(); await G.until(() => G.asks.length > 0, 6000); o.cleared = list();
    return o;
  });
  await shot(p, 'practice-8-solution');
  console.log(JSON.stringify(r));
  ok(r.asks.length === 3 && r.asks.every(a => a === 'Что купить?') && r.list.join('|') === 'хлеб|молоко|яблоки', 'корзина три раза спрашивает и добавляет ответы в список', r.list);
  ok(r.hiddenAtStart && r.shown, 'список спрятан в начале и показан в конце');
  ok(r.says.includes('В списке покупок: 3') && r.says.includes('Сначала купим: хлеб'), 'корзина говорит, сколько покупок и какая первая', r.says);
  ok(r.more === 'Что ещё купить?' && r.list4.join('|') === 'хлеб|молоко|яблоки|сыр', 'пробел добавляет ещё одну покупку', r.list4);
  ok(r.cleared.length === 0, 'флажок очищает список');
  await p.close();
  }

  await env.b.close(); env.srv.close(); process.exit(done() ? 1 : 0);
})().catch(e => { console.error('ERR', e); process.exit(1) });
