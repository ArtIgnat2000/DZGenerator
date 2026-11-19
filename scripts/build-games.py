#!/usr/bin/env python3
"""Build eight self-contained, illustrated Scratch 3 projects for V-labs lessons."""
import hashlib, json, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'lessons' / 'games'
OUT.mkdir(parents=True, exist_ok=True)

THEMES = [
    ('01-events', 'Солнце и дождь', 'СОБЫТИЯ', 'Кликни по облаку или нажми пробел — сцена отвечает!', ['#132b52','#2679a9'], '☀'),
    ('02-motion', 'Космический маршрут', 'ДВИЖЕНИЕ', 'Проведи исследователя к светящемуся маяку стрелками.', ['#101b46','#382c78'], '🚀'),
    ('03-looks', 'Театр настроений', 'ВНЕШНОСТЬ', 'Нажми на героя: костюм и реплика меняются!', ['#482654','#d45481'], '🎭'),
    ('04-sound', 'Музыкальный инструмент', 'ЗВУК', 'Нажми клавиши 1–4: каждая запускает свою ноту.', ['#102d47','#167d87'], '♫'),
    ('05-control', 'Метеоритный дождь', 'УПРАВЛЕНИЕ', 'Флаг запускает поток клонов-метеоритов. Лови ритм!', ['#111a3c','#4c3068'], '☄'),
    ('06-sensing', 'Следопыт за мышью', 'СЕНСОРЫ', 'Герой следует за курсором и замечает нажатия.', ['#11384a','#167b77'], '✦'),
    ('07-operators', 'Математический оракул', 'ОПЕРАТОРЫ', 'Ответь на вопрос и узнай, больше ли число пяти.', ['#33234f','#7550a1'], '?'),
    ('08-data', 'Дневник желаний', 'ДАННЫЕ', 'Запиши желание: проект сохранит его в список.', ['#203650','#278b80'], '✎'),
]

# Scratch-compatible artwork: only basic SVG shapes supported by Scratch Paint.
# No SVG text, filters, gradients, rounded-rectangle attributes, or external assets.
def backdrop_svg(index, title, kicker, colors, icon):
    a, b = colors
    stars = ''.join(
        f'<circle cx="{(i*73+29)%480}" cy="{(i*47+19)%220}" r="{1+(i%3)*.6}" fill="#ffffff" opacity="{.3+(i%4)*.12}"/>'
        for i in range(24)
    )
    scene = ''
    if index == 1:
        scene = '<path d="M58 230 C120 176 166 270 228 220 S330 176 395 220" fill="none" stroke="#9cefff" stroke-width="4" stroke-dasharray="3 12" stroke-linecap="round"/><circle cx="395" cy="220" r="20" fill="#7cf6d3" opacity=".35"/><path d="M395 194v42m-10-32 10-10 10 10" fill="none" stroke="#b7ffeb" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>'
    elif index == 2:
        scene = '<path d="M0 0h95v250H0Z" fill="#a83e72"/><path d="M385 0h95v250h-95Z" fill="#a83e72"/><path d="M95 0h42v235H95Zm248 0h42v235h-42Z" fill="#e77c9f"/><path d="M0 238q240 54 480 0v34q-240 56-480 0Z" fill="#f5b86e"/>'
    elif index == 3:
        scene = '<path d="M64 224h42v-48H64Zm68 0h42v-96h-42Zm68 0h42V96h-42Zm68 0h42v-72h-42Zm68 0h42v-124h-42Z" fill="#71e4d0" opacity=".75"/><path d="M55 231h334" stroke="#d2fff4" stroke-width="4"/>'
    elif index == 4:
        scene = '<path d="M88 82 112 44l25 38-25 39Z" fill="#ffbf57"/><path d="M88 82 43 100l45 15 24-33Z" fill="#ff755f"/><path d="M137 82 176 62l-22 38-17-18Z" fill="#ffd77b"/><circle cx="113" cy="82" r="10" fill="#fff6c7"/>'
    elif index == 5:
        scene = '<circle cx="360" cy="158" r="68" fill="none" stroke="#68e7ce" stroke-width="3" opacity=".5"/><circle cx="360" cy="158" r="42" fill="none" stroke="#a1fff0" stroke-width="3" opacity=".65"/><circle cx="360" cy="158" r="12" fill="#fff0a0"/>'
    elif index == 6:
        scene = '<circle cx="356" cy="154" r="58" fill="#a98aff" opacity=".8"/><circle cx="356" cy="154" r="42" fill="#f5eaff"/><path d="M335 139c2-17 14-25 27-25 16 0 27 11 27 25 0 11-8 18-17 24-7 5-10 9-10 17" fill="none" stroke="#523c82" stroke-width="8" stroke-linecap="round"/><circle cx="362" cy="198" r="5" fill="#523c82"/>'
    else:
        scene = '<path d="M315 86h78l37 37v133H315Z" fill="#f8fbff"/><path d="M393 86v37h37" fill="#bcefe4"/><path d="M336 157h67m-67 24h67m-67 24h48" stroke="#51b69e" stroke-width="5" stroke-linecap="round"/><path d="m344 261 7-25 60-60 18 18-60 60Z" fill="#ffbd62"/>'
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">'
        f'<rect width="480" height="360" fill="{a}"/><path d="M0 0h480v210H0Z" fill="{b}" opacity=".48"/>'
        f'{stars}{scene}<path d="M0 260Q85 222 170 264T340 249T480 257V360H0Z" fill="#173850" opacity=".58"/>'
        f'<path d="M0 298Q100 275 215 300T480 288V360H0Z" fill="#0f6c6b" opacity=".62"/>'
        f'<path d="M0 315Q92 282 178 315T337 315T480 315V360H0Z" fill="#0b535b" opacity=".5"/></svg>'
    )


def events_backdrop(scene):
    sky = {'sunny':'#9cdef0', 'rainy':'#617caa', 'rainbow':'#a9dced'}[scene]
    weather = {
        'sunny': '<path d="M294 156c0-18 14-32 32-32 8-18 34-22 48-7 16 0 28 13 28 29 16 3 25 13 25 27H300c-13 0-20-5-20-13Z" fill="#f9fdff"/>',
        'rainy': '<path d="M255 153c0-25 19-44 44-44 8-27 44-34 62-14 28-5 51 15 51 40 23 5 33 17 33 37H273c-14 0-22-8-18-19Z" fill="#8299b8"/><path d="m292 191-9 24m40-24-9 24m40-24-9 24m40-24-9 24" stroke="#c8f3ff" stroke-width="7" stroke-linecap="round"/>',
        'rainbow': '<path d="M267 202a89 89 0 0 1 178 0" fill="none" stroke="#ff6d78" stroke-width="13"/><path d="M280 202a76 76 0 0 1 152 0" fill="none" stroke="#ffb95c" stroke-width="13"/><path d="M293 202a63 63 0 0 1 126 0" fill="none" stroke="#ffe66d" stroke-width="13"/><path d="M306 202a50 50 0 0 1 100 0" fill="none" stroke="#6ed9a7" stroke-width="13"/><path d="M319 202a37 37 0 0 1 74 0" fill="none" stroke="#69baff" stroke-width="13"/><circle cx="352" cy="160" r="22" fill="#ffe478"/>'
    }[scene]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="480" height="360" viewBox="0 0 480 360">'
        f'<rect width="480" height="360" fill="{sky}"/><circle cx="82" cy="89" r="54" fill="#ffffff" opacity=".16"/>'
        f'<circle cx="82" cy="89" r="38" fill="#ffffff" opacity=".1"/>{weather}'
        f'<path d="M0 250q85-62 177 0t160-4q76-50 143 2v112H0Z" fill="#55c998"/>'
        f'<path d="M0 286q98-58 184 0t160-3q69-42 136 1v76H0Z" fill="#167c77" opacity=".7"/>'
        f'<path d="M0 315q92-33 178 0t159 0q75-30 143 0v45H0Z" fill="#126b6e" opacity=".65"/></svg>'
    )


def cloud_svg():
    return b'<svg xmlns="http://www.w3.org/2000/svg" width="120" height="90" viewBox="0 0 120 90"><path d="M22 67c-8-3-11-9-9-17 2-9 10-14 20-13 4-17 17-25 31-21 10 3 16 10 18 20 14-5 29 4 30 18 1 8-4 14-12 17H22Z" fill="#eaf6ff" stroke="#ffffff" stroke-width="3"/><circle cx="48" cy="52" r="3" fill="#36536e"/><circle cx="72" cy="52" r="3" fill="#36536e"/><path d="M52 64q8 7 16 0" fill="none" stroke="#36536e" stroke-width="3" stroke-linecap="round"/></svg>'


def sprite_svg(kind, alt=False):
    if kind == 0:
        body = '<circle cx="48" cy="48" r="25" fill="#ffbf38"/><circle cx="48" cy="48" r="18" fill="#ffe98a"/><path d="M48 5v10M48 81v10M5 48h10M81 48h10M18 18l8 8m44 44 8 8M78 18l-8 8M26 70l-8 8" stroke="#ffdc67" stroke-width="7" stroke-linecap="round"/><circle cx="41" cy="45" r="2.5" fill="#24395c"/><circle cx="56" cy="45" r="2.5" fill="#24395c"/><path d="M41 55q7 8 14 0" fill="none" stroke="#24395c" stroke-width="2.5" stroke-linecap="round"/>'
    elif kind == 1:
        body = '<path d="M48 4 75 76 49 65 23 76Z" fill="#e8f4ff"/><path d="m48 8 1 57-22 10Z" fill="#f7fbff"/><path d="m48 8 25 67-23-10Z" fill="#79d9e5"/><path d="m23 76 25-11 26 11-16 15H38Z" fill="#ff8b60"/><circle cx="48" cy="43" r="6" fill="#192c55"/><path d="M30 75 14 87M66 75l16 12" stroke="#ffc863" stroke-width="5" stroke-linecap="round"/>'
    elif kind == 2:
        body = '<path d="M48 7 84 28v40L48 89 12 68V28Z" fill="#ef8bb7"/><path d="M48 7v39L12 28ZM48 46l36-18v40L48 89Z" fill="#8fe3d0"/><path d="m48 7 36 21-36 18-36-18Z" fill="#ffe08a"/><circle cx="37" cy="44" r="3" fill="#513060"/><circle cx="58" cy="44" r="3" fill="#513060"/><path d="M39 57q9 8 18 0" fill="none" stroke="#513060" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 3:
        body = '<circle cx="48" cy="48" r="37" fill="#102840" stroke="#74eed9" stroke-width="3"/><circle cx="48" cy="48" r="28" fill="#17415b" stroke="#c2fff2" stroke-opacity=".55"/><path d="M48 21v27l18 12" fill="none" stroke="#ffe36d" stroke-width="6" stroke-linecap="round"/><circle cx="48" cy="48" r="5" fill="#ff7692"/><path d="M17 48h7m48 0h7M48 17v7m0 48v7" stroke="#fff" stroke-width="3" stroke-linecap="round"/>'
    elif kind == 4:
        body = '<path d="M48 8 83 72H13Z" fill="#ff7c63" stroke="#ffe0a1" stroke-width="3"/><path d="m48 23 22 41H26Z" fill="#ffc94f"/><circle cx="48" cy="49" r="9" fill="#fff1ba"/><path d="M31 75q17 14 34 0" fill="none" stroke="#ffad5b" stroke-width="5" stroke-linecap="round"/>'
    elif kind == 5:
        body = '<path d="M48 10 59 38 89 30 68 51 83 77 55 66 39 91 38 62 9 56 36 44Z" fill="#ffe37a" stroke="#fff4bc" stroke-width="2"/><circle cx="48" cy="49" r="9" fill="#fff"/><path d="M20 20 9 12m72 8 10-8M14 79 4 85" stroke="#77efdb" stroke-width="4" stroke-linecap="round"/>'
    elif kind == 6:
        body = '<circle cx="48" cy="48" r="37" fill="#a98aff"/><circle cx="48" cy="48" r="26" fill="#f5eaff"/><path d="M34 36c1-10 7-16 16-16 10 0 16 7 16 15 0 7-5 11-11 15-5 3-7 6-7 12" fill="none" stroke="#523c82" stroke-width="6" stroke-linecap="round"/><circle cx="48" cy="72" r="3.5" fill="#523c82"/><path d="M28 15q20-16 40 0" fill="none" stroke="#ffe78a" stroke-width="5" stroke-linecap="round"/>'
    else:
        body = '<path d="M23 8h34l18 18v50q0 8-8 8H23q-8 0-8-8V16q0-8 8-8Z" fill="#f8fbff"/><path d="M57 8v20h18" fill="#bcefe4"/><path d="M28 43h37M28 54h37M28 65h26" stroke="#51b69e" stroke-width="4" stroke-linecap="round"/><path d="m20 79 4-13 33-33 9 9-33 33Z" fill="#ffbd62"/><path d="m57 33 9 9" stroke="#fff" stroke-width="3"/>'
    if alt and kind == 2:
        body = '<path d="M48 7 84 28v40L48 89 12 68V28Z" fill="#a1a7ff"/><path d="M48 7v39L12 28ZM48 46l36-18v40L48 89Z" fill="#ffc27f"/><path d="m48 7 36 21-36 18-36-18Z" fill="#f7f2ff"/><circle cx="37" cy="44" r="3" fill="#513060"/><circle cx="58" cy="44" r="3" fill="#513060"/><path d="M39 58q9-8 18 0" fill="none" stroke="#513060" stroke-width="3" stroke-linecap="round"/>'
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96">{body}</svg>'

class Project:
    def __init__(self): self.blocks={}; self.counter=0
    def add(self, opcode, inputs=None, fields=None, parent=None, top=False, x=30, y=30, shadow=False):
        self.counter += 1; bid=f'b{self.counter:04d}'
        b={'opcode':opcode,'next':None,'parent':parent,'inputs':inputs or {},'fields':fields or {},'shadow':shadow,'topLevel':top}
        if top: b.update({'x':x,'y':y})
        self.blocks[bid]=b; return bid
    def chain(self, ids):
        for a,b in zip(ids,ids[1:]): self.blocks[a]['next']=b; self.blocks[b]['parent']=a
        return ids[0] if ids else None
    def num(self, value, parent=None): return self.add('math_number', fields={'NUM':[str(value),None]}, parent=parent, shadow=True)
    def text(self, value, parent=None): return self.add('text', fields={'TEXT':[value,None]}, parent=parent, shadow=True)
    def key(self, key, parent=None): return self.add('sensing_keyoptions', fields={'KEY_OPTION':[key,None]}, parent=parent, shadow=True)
    def bool_key(self, key, parent):
        menu=self.key(key,parent)
        return self.add('sensing_keypressed', {'KEY_OPTION':[1,menu]}, parent=parent)
    def say(self, value, parent=None):
        t=self.text(value)
        b=self.add('looks_say', {'MESSAGE':[1,t]}, parent=parent); self.blocks[t]['parent']=b
        return b
    def move(self, op, field, value, parent=None):
        n=self.num(value)
        b=self.add(op,{field:[1,n]},parent=parent); self.blocks[n]['parent']=b
        return b
    def if_key(self, key, op, val, parent):
        cond=self.bool_key(key,None)
        b=self.add('control_if', {'CONDITION':[2,cond]}, parent=parent)
        self.blocks[cond]['parent']=b
        stmt=self.move(op, 'DX' if op=='motion_changexby' else 'DY', val, parent=b)
        self.blocks[b]['inputs']['SUBSTACK']=[2,stmt]
        return b
    def hat(self, opcode, fields=None, x=30, y=30): return self.add(opcode,fields=fields or {},top=True,x=x,y=y)

def menu_block(p, opcode, field, value, parent):
    return p.add(opcode,fields={field:[value,None]},parent=parent,shadow=True)

def build(index, lesson):
    stem,title,kicker,tagline,colors,icon=lesson
    p=Project(); stagep=Project() if index==0 else None; cloudp=Project() if index==0 else None; kind=index
    # main actor
    flag=p.hat('event_whenflagclicked',x=32,y=30)
    scripts=[]
    if index==0:
        # Stage reacts to two custom broadcasts: cloud click -> rain; Space -> rainbow.
        stage_flag=stagep.hat('event_whenflagclicked',x=30,y=30)
        backdrop=menu_block(stagep,'looks_backdrops','BACKDROP','Солнечно',None)
        show=stagep.add('looks_switchbackdropto',{'BACKDROP':[1,backdrop]},parent=stage_flag);stagep.blocks[backdrop]['parent']=show
        stagep.chain([stage_flag,show])
        for n,(msg,bg,y) in enumerate([('Дождь','Дождливо',145),('Радуга','Радуга',260)],1):
            receive=stagep.hat('event_whenbroadcastreceived',{'BROADCAST_OPTION':[msg,f'msg{n}']},x=30,y=y)
            menu=menu_block(stagep,'looks_backdrops','BACKDROP',bg,None)
            change=stagep.add('looks_switchbackdropto',{'BACKDROP':[1,menu]},parent=receive);stagep.blocks[menu]['parent']=change
            stagep.chain([receive,change])
        # Sunny sprite explains the controls, while the separate cloud handles click events.
        s1=p.say('Солнце и дождь: нажми на облако — пойдёт дождь. Пробел вызовет радугу!'); p.chain([flag,s1])
        space=p.hat('event_whenkeypressed',{'KEY_OPTION':['space',None]},x=32,y=180)
        broadcast=menu_block(p,'event_broadcast_menu','BROADCAST_OPTION','Радуга',None)
        send=p.add('event_broadcast',{'BROADCAST_INPUT':[1,broadcast]},parent=space);p.blocks[broadcast]['parent']=send;p.chain([space,send])
        cloudflag=cloudp.hat('event_whenflagclicked',x=30,y=30)
        cloudp.chain([cloudflag,cloudp.say('Кликни по облаку!',parent=cloudflag)])
        cloudclick=cloudp.hat('event_whenthisspriteclicked',x=30,y=150)
        rainmenu=menu_block(cloudp,'event_broadcast_menu','BROADCAST_OPTION','Дождь',None)
        rainsend=cloudp.add('event_broadcast',{'BROADCAST_INPUT':[1,rainmenu]},parent=cloudclick);cloudp.blocks[rainmenu]['parent']=rainsend
        raintalk=cloudp.say('Кап-кап! Облако отправило сообщение «Дождь».',parent=rainsend)
        cloudp.chain([cloudclick,rainsend,raintalk])
    elif index==1:
        # Four-arrow movement with edge bounce, all directly visible in the code.
        xpos=p.num(-150); ypos=p.num(-100)
        goto=p.add('motion_gotoxy',{'X':[1,xpos],'Y':[1,ypos]},parent=flag)
        p.blocks[xpos]['parent']=goto; p.blocks[ypos]['parent']=goto
        forever=p.add('control_forever',parent=goto)
        checks=[p.if_key('up arrow','motion_changeyby',8,forever),p.if_key('down arrow','motion_changeyby',-8,forever),p.if_key('right arrow','motion_changexby',8,forever),p.if_key('left arrow','motion_changexby',-8,forever),p.add('motion_ifonedgebounce',parent=forever)]
        # Reaching the beacon is the little win condition.
        menu=menu_block(p,'sensing_touchingobjectmenu','TOUCHINGOBJECTMENU','Маяк',None)
        touching=p.add('sensing_touchingobject',{'TOUCHINGOBJECTMENU':[1,menu]}); p.blocks[menu]['parent']=touching
        win=p.add('control_if',{'CONDITION':[2,touching]},parent=forever); p.blocks[touching]['parent']=win
        wintext=p.say('Маршрут пройден! Отличная навигация!',parent=win)
        stop=p.add('control_stop',fields={'STOP_OPTION':['this script',None]},parent=wintext)
        p.blocks[win]['inputs']['SUBSTACK']=[2,p.chain([wintext,stop])]
        checks.append(win)
        p.blocks[forever]['inputs']['SUBSTACK']=[2,p.chain(checks)]
        p.blocks[goto]['next']=forever
    elif index==2:
        say=p.say('Добро пожаловать в театр! Нажми на сцену, чтобы сменить костюм и настроение.')
        p.chain([flag,say])
        click=p.hat('event_whenthisspriteclicked',x=32,y=160)
        nxt=p.add('looks_nextcostume',parent=click)
        speak=p.say('Новый костюм — новая роль! Попробуй ещё раз.',parent=nxt)
        p.chain([click,nxt,speak])
        # costume switch points at provided costume assets
    elif index==3:
        p.chain([flag,p.say('Синтезатор готов. Нажми клавишу 1, 2, 3 или 4 и смотри на пульс!')])
        for i,keyname in enumerate(['1','2','3','4']):
            hat=p.hat('event_whenkeypressed',{'KEY_OPTION':[keyname,None]},x=32,y=120+i*100)
            msg=p.say(f'Нота {i+1}! Звук — тоже событие.',parent=hat)
            # Each key plays its own generated note asset.
            sndname=f'Нота {i+1}'
            menu=menu_block(p,'sound_sounds_menu','SOUND_MENU',sndname,None)
            sound=p.add('sound_playuntildone',{'SOUND_MENU':[1,menu]},parent=msg)
            p.blocks[menu]['parent']=sound
            p.chain([hat,msg,sound])
    elif index==4:
        # Actual clone flow, continuous meteor shower, with a clone falling until it leaves screen.
        p.chain([flag,p.say('Метеоритный поток начинается! Наблюдай, как цикл создаёт клоны.')])
        forever=p.add('control_forever',parent=p.blocks[flag]['next'])
        waitnum=p.num(.7); wait=p.add('control_wait',{'DURATION':[1,waitnum]},parent=forever); p.blocks[waitnum]['parent']=wait
        clone_menu=menu_block(p,'control_create_clone_of_menu','CLONE_OPTION','_myself_',None)
        clone=p.add('control_create_clone_of',{'CLONE_OPTION':[1,clone_menu]},parent=wait); p.blocks[clone_menu]['parent']=clone
        p.blocks[forever]['inputs']['SUBSTACK']=[2,p.chain([wait,clone])]
        p.blocks[p.blocks[flag]['next']]['next']=forever
        clonehat=p.hat('control_start_as_clone',x=280,y=40)
        lo=p.num(-220); hi=p.num(220); rnd=p.add('operator_random',{'FROM':[1,lo],'TO':[1,hi]})
        xpos=p.num(175); place=p.add('motion_gotoxy',{'X':[2,rnd],'Y':[1,xpos]},parent=clonehat)
        p.blocks[rnd]['parent']=place;p.blocks[lo]['parent']=rnd;p.blocks[hi]['parent']=rnd;p.blocks[xpos]['parent']=place
        times=p.num(42); forever2=p.add('control_repeat',{'TIMES':[1,times]},parent=place);p.blocks[times]['parent']=forever2
        n=p.num(-8); step=p.add('motion_changeyby',{'DY':[1,n]},parent=forever2);p.blocks[n]['parent']=step;p.blocks[forever2]['inputs']['SUBSTACK']=[2,step]
        dele=p.add('control_delete_this_clone',parent=forever2); p.chain([clonehat,place,forever2,dele])
    elif index==5:
        # go-to mouse pointer inside forever; mouse button sensing changes speech
        p.chain([flag,p.say('Я следопыт! Двигай мышью: я найду курсор. Нажми кнопку — и я замечу!')])
        menu=menu_block(p,'motion_goto_menu','TO','_mouse_',None)
        goto=p.add('motion_goto',{'TO':[1,menu]},parent=p.blocks[flag]['next']); p.blocks[menu]['parent']=goto
        forever=p.add('control_forever',parent=goto)
        mdown=p.add('sensing_mousedown',parent=None)
        cond=p.add('control_if',{'CONDITION':[2,mdown]},parent=forever);p.blocks[mdown]['parent']=cond
        say=p.say('Клик замечен! Это сенсор мыши.',parent=cond);p.blocks[cond]['inputs']['SUBSTACK']=[2,say]
        p.blocks[forever]['inputs']['SUBSTACK']=[2,cond];p.blocks[goto]['next']=forever
    elif index==6:
        # ask, evaluate answer using an Operators comparison, branches via nested substacks
        ask=p.add('sensing_askandwait',{'QUESTION':[1,p.text('Сколько будет 2 + 3? Введи число:')]},parent=flag); p.blocks[list(p.blocks[ask]['inputs'].values())[0][1]]['parent']=ask
        ans=p.add('sensing_answer',parent=None); five=p.num(5)
        gt=p.add('operator_equals',{'OPERAND1':[2,ans],'OPERAND2':[1,five]});p.blocks[ans]['parent']=gt;p.blocks[five]['parent']=gt
        branch=p.add('control_if_else',{'CONDITION':[2,gt]},parent=ask);p.blocks[gt]['parent']=branch
        good=p.say('Точно! Операторы сравнили твой ответ. Ты — математический оракул!',parent=branch)
        bad=p.say('Почти! Подсказка: сложи 2 и 3, затем попробуй снова.',parent=branch)
        p.blocks[branch]['inputs']['SUBSTACK']=[2,good];p.blocks[branch]['inputs']['SUBSTACK2']=[2,bad]
        p.chain([flag,ask,branch])
    else:
        # Initialize list and capture three ideas; all saved to the native Scratch list monitor.
        listname='Мои желания'
        clear=p.add('data_deletealloflist',fields={'LIST':[listname,None]},parent=flag)
        p.chain([flag,clear])
        ask1=p.add('sensing_askandwait',{'QUESTION':[1,p.text('Запиши одно желание:')]},parent=clear)
        # Use the built-in answer reporter as the list item.
        ans=p.add('sensing_answer')
        add=p.add('data_addtolist',{'ITEM':[2,ans]},fields={'LIST':[listname,None]},parent=ask1);p.blocks[ans]['parent']=add
        ask2=p.add('sensing_askandwait',{'QUESTION':[1,p.text('Ещё одно желание:')]},parent=add)
        ans2=p.add('sensing_answer');add2=p.add('data_addtolist',{'ITEM':[2,ans2]},fields={'LIST':[listname,None]},parent=ask2);p.blocks[ans2]['parent']=add2
        done=p.say('Готово! Открой список «Мои желания» слева — ответы сохранены.',parent=add2)
        p.chain([clear,ask1,add,ask2,add2,done])
    # Choose stage backdrop and actor costumes; lesson 1 has three event-driven scenes.
    assets=[]
    def asset(name,data,fmt,cx=48,cy=48):
        aid=hashlib.md5(data).hexdigest(); assets.append((aid+'.'+fmt,data)); return {'assetId':aid,'name':name,'md5ext':aid+'.'+fmt,'dataFormat':fmt,'bitmapResolution':1,'rotationCenterX':cx,'rotationCenterY':cy}
    if index==0:
        bgcostumes=[asset(name,events_backdrop(scene).encode(),'svg',240,180) for name,scene in [('Солнечно','sunny'),('Дождливо','rainy'),('Радуга','rainbow')]]
        bgcost=bgcostumes[0]
    else:
        back=backdrop_svg(index,title,kicker,colors,icon).encode()
        bgcost=asset('Иллюстрированная сцена',back,'svg',240,180); bgcostumes=[bgcost]
    costumes=[asset('Герой',sprite_svg(index).encode(),'svg')]
    if index==2: costumes.append(asset('Новая роль',sprite_svg(index,True).encode(),'svg'))
    cloudcost=asset('Облачко',cloud_svg(),'svg',60,45) if index==0 else None
    beacon_svg=b'<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><circle cx="48" cy="48" r="43" fill="#ffe875" opacity=".28"/><circle cx="48" cy="48" r="29" fill="#ffe875" opacity=".42"/><path d="M48 18v57M34 37l14-18 14 18" fill="none" stroke="#baffed" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/><circle cx="48" cy="46" r="7" fill="#fff"/><path d="M29 76h38" stroke="#fff" stroke-width="4" stroke-linecap="round"/></svg>'
    beacon_cost=asset('Маяк',beacon_svg,'svg') if index==1 else None
    sounds=[]
    if index==3:
        import math, struct
        for note,freq in enumerate([261.63,329.63,392.0,523.25],1):
            rate=22050; frames=[]
            for j in range(int(rate*.42)):
                env=min(1,j/500,(rate*.42-j)/2400)
                val=int(10500*max(0,env)*math.sin(2*math.pi*freq*j/rate))
                frames.append(struct.pack('<h',val))
            import io,wave
            buff=io.BytesIO()
            with wave.open(buff,'wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(b''.join(frames))
            data=buff.getvalue(); aid=hashlib.md5(data).hexdigest(); assets.append((aid+'.wav',data))
            sounds.append({'name':f'Нота {note}','assetId':aid,'dataFormat':'wav','format':'','rate':rate,'sampleCount':len(frames),'md5ext':aid+'.wav'})
    broadcasts={'msg1':'Дождь','msg2':'Радуга'} if index==0 else {}
    stage={'isStage':True,'name':'Stage','variables':{},'lists':{},'broadcasts':broadcasts,'blocks':stagep.blocks if index==0 else {},'comments':{},'currentCostume':0,'costumes':bgcostumes,'sounds':[],'volume':100,'layerOrder':0,'tempo':60,'videoTransparency':50,'videoState':'on','textToSpeechLanguage':None}
    if index==7: stage['lists']={'list0':['Мои желания',[]]}
    # Scratch parents every reporter/menu block to the block whose input contains it.
    for graph in [p, stagep, cloudp]:
        if graph is None: continue
        for bid, block in graph.blocks.items():
            for value in block['inputs'].values():
                if len(value) > 1 and isinstance(value[1], str) and value[1] in graph.blocks:
                    graph.blocks[value[1]]['parent'] = bid
    actor={'isStage':False,'name':'Солнце' if index==0 else 'Спрайт1','variables':{},'lists':{},'broadcasts':broadcasts,'blocks':p.blocks,'comments':{},'currentCostume':0,'costumes':costumes,'sounds':sounds,'volume':100,'layerOrder':1,'visible':True,'x':-100 if index==1 else 0,'y':-55 if index==1 else -35,'size':75 if index in (1,4,5) else 100,'direction':90,'draggable':False,'rotationStyle':'all around'}
    targets=[stage,actor]
    if index==0:
        targets.append({'isStage':False,'name':'Облако','variables':{},'lists':{},'broadcasts':broadcasts,'blocks':cloudp.blocks,'comments':{},'currentCostume':0,'costumes':[cloudcost],'sounds':[],'volume':100,'layerOrder':2,'visible':True,'x':135,'y':58,'size':100,'direction':90,'draggable':False,'rotationStyle':"don't rotate"})
    if index==1:
        targets.append({'isStage':False,'name':'Маяк','variables':{},'lists':{},'broadcasts':{},'blocks':{},'comments':{},'currentCostume':0,'costumes':[beacon_cost],'sounds':[],'volume':100,'layerOrder':2,'visible':True,'x':159,'y':-41,'size':80,'direction':90,'draggable':False,'rotationStyle':"don't rotate"})
    monitors=[]
    if index==7:
        monitors.append({'id':'list0','mode':'list','opcode':'data_listcontents','params':{'LIST':'Мои желания'},'spriteName':'Stage','value':[],'width':220,'height':180,'x':5,'y':5,'visible':True})
    project={'targets':targets,'monitors':monitors,'extensions':[],'meta':{'semver':'3.0.0','vm':'0.2.0','agent':'V-labs lesson game builder'}}
    filename=OUT/(stem+'.sb3')
    with zipfile.ZipFile(filename,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        z.writestr('project.json',json.dumps(project,ensure_ascii=False,separators=(',',':')))
        for name,data in assets: z.writestr(name,data)
    return filename

for i, lesson in enumerate(THEMES):
    f=build(i,lesson)
    print(f'{f.relative_to(ROOT)} ({f.stat().st_size:,} bytes)')
