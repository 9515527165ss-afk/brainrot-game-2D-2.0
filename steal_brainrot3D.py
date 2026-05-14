# -*- coding: utf-8 -*-
from ursina import *
import random

app = Ursina(borderless=False)

window.title = 'Steal a Brainrot (3D)'
window.size = (1000, 700)

# МУЗЫКА
music_volume = 0.3
sfx_volume = 0.5
try:
    bg_music = Audio('background.mp3', loop=True, autoplay=True, volume=music_volume)
except:
    bg_music = None

camera.position = (0, 15, -20)
camera.rotation_x = 35

# ЗЕМЛЯ
ground = Entity(model='plane', scale=(50, 1, 50), texture='grass', texture_scale=(25, 25))

# ДОМ
player_base = Entity(model='cube', color=color.brown, scale=(3, 1, 3), position=(0, 0.5, 0))
roof = Entity(model='cube', color=color.red, scale=(2.5, 0.8, 2.5), position=(0, 1.8, 0))

# ДАННЫЕ
brainrot_data = {
    'Ромасик':  (color.blue, 2, 3.0),
    'Рита':    (color.rgb(255, 100, 0), 5, 2.6),
    'Изюм':    (color.green, 8, 2.3),
    'Богдан':  (color.magenta, 12, 2.0),
    'Жакет':   (color.rgb(128, 0, 128), 15, 1.7),
    'Окак':    (color.rgb(0, 200, 200), 18, 1.5),
    '67':      (color.rgb(255, 200, 0), 20, 1.3),
    'Серый':   (color.red, 20, 1.3),
}

brainrots = []
inventory = []
money = 0
rebirth_level = 0
rebirth_bonus = 1.0

upgrades = {'speed': 0, 'range': 0, 'luck': 0}
upgrade_costs = {'speed': 100, 'range': 150, 'luck': 200}
upgrade_max = {'speed': 5, 'range': 3, 'luck': 5}
upgrade_names = {'speed': 'Скорость', 'range': 'Дальность', 'luck': 'Удача'}

# HUD
inventory_text = Text(text='Украдено: 0', position=(-0.85, 0.48), scale=2, color=color.yellow)
money_text = Text(text='Монеты: 0', position=(-0.85, 0.42), scale=1.5, color=color.green)
rebirth_text = Text(text='Перерождение: 0 | Бонус: x1.0', position=(-0.85, 0.36), scale=1.2, color=color.rgb(255, 215, 0))
controls_text = Text(text='E-магазин | R-перерождение | TAB-настройки | M-музыка | ESC-выход', position=(0, -0.47), scale=0.9, color=color.white)

# СОСТОЯНИЯ
ui_open = False
current_window = None

# ВСЕ UI ЭЛЕМЕНТЫ (для удаления)
all_ui_elements = []

def clear_ui():
    global all_ui_elements
    for elem in all_ui_elements:
        destroy(elem)
    all_ui_elements = []

# ============== МАГАЗИН ==============
def create_shop():
    global ui_open, current_window, all_ui_elements
    clear_ui()
    
    # Фон
    bg = Panel(parent=camera.ui, scale=(0.55, 0.7), position=(0, 0), color=color.rgba(30, 30, 60, 250))
    all_ui_elements.append(bg)
    
    # Заголовок
    t = Text(parent=camera.ui, text='🛒 МАГАЗИН', position=(0, 0.28), scale=3.5, color=color.yellow, origin=(0,0))
    all_ui_elements.append(t)
    
    # Монеты
    t = Text(parent=camera.ui, text=f'💰 {money} монет', position=(0, 0.20), scale=2, color=color.green, origin=(0,0))
    all_ui_elements.append(t)
    
    # КНОПКИ УЛУЧШЕНИЙ
    keys = ['speed', 'range', 'luck']
    emojis = ['⚡', '🎯', '🍀']
    y_positions = [0.08, -0.04, -0.16]
    
    for i, key in enumerate(keys):
        y = y_positions[i]
        lvl = upgrades[key]
        max_lvl = upgrade_max[key]
        cost = upgrade_costs[key]
        name = upgrade_names[key]
        
        if lvl < max_lvl:
            btn_text = f'{i+1}. {emojis[i]} {name} (ур.{lvl}/{max_lvl})'
            cost_text = f'{cost} монет'
            btn_color = color.rgba(50, 50, 100, 220)
        else:
            btn_text = f'{i+1}. {emojis[i]} {name} MAX'
            cost_text = '✓'
            btn_color = color.rgba(30, 80, 30, 220)
        
        # Кнопка
        btn = Button(
            parent=camera.ui,
            text=btn_text,
            scale=(0.45, 0.07),
            position=(0, y),
            color=btn_color,
            highlight_color=color.rgba(80, 80, 150, 220),
            pressed_color=color.rgba(20, 20, 50, 220),
            on_click=make_buy_func(key)
        )
        all_ui_elements.append(btn)
        
        # Стоимость справа
        t = Text(parent=camera.ui, text=cost_text, position=(0.23, y), scale=1.3, color=color.yellow, origin=(0,0))
        all_ui_elements.append(t)
    
    # Кнопка ЗАКРЫТЬ
    close_btn = Button(
        parent=camera.ui,
        text='❌ ЗАКРЫТЬ',
        scale=(0.3, 0.06),
        position=(0, -0.28),
        color=color.rgba(150, 50, 50, 220),
        highlight_color=color.red,
        on_click=close_ui
    )
    all_ui_elements.append(close_btn)

def make_buy_func(key):
    def buy():
        global money
        if money >= upgrade_costs[key] and upgrades[key] < upgrade_max[key]:
            money -= upgrade_costs[key]
            upgrades[key] += 1
            upgrade_costs[key] = int(upgrade_costs[key] * 1.5)
            money_text.text = f'Монеты: {money}'
            create_shop()  # обновить окно
    return buy

# ============== ПЕРЕРОЖДЕНИЕ ==============
def create_rebirth():
    global ui_open, current_window, all_ui_elements
    clear_ui()
    
    cost = 500 * (rebirth_level + 1)
    next_bonus = rebirth_bonus + 0.5
    
    # Фон
    bg = Panel(parent=camera.ui, scale=(0.5, 0.55), position=(0, 0), color=color.rgba(30, 30, 60, 250))
    all_ui_elements.append(bg)
    
    # Заголовок
    t = Text(parent=camera.ui, text='🌟 ПЕРЕРОЖДЕНИЕ', position=(0, 0.22), scale=3, color=color.rgb(255, 215, 0), origin=(0,0))
    all_ui_elements.append(t)
    
    # Инфо
    info = f'Уровень: {rebirth_level} → {rebirth_level + 1}\n'
    info += f'Бонус: x{rebirth_bonus:.1f} → x{next_bonus:.1f}\n'
    info += f'Стоимость: {cost} монет\n\n'
    info += f'⚠ Улучшения сбросятся!\n⚠ Монеты обнулятся!'
    
    t = Text(parent=camera.ui, text=info, position=(0, 0.02), scale=1.4, color=color.white, origin=(0,0))
    all_ui_elements.append(t)
    
    # КНОПКА ПЕРЕРОДИТЬСЯ
    rebirth_btn = Button(
        parent=camera.ui,
        text='🔥 ПЕРЕРОДИТЬСЯ',
        scale=(0.35, 0.07),
        position=(0, -0.15),
        color=color.rgba(200, 150, 0, 220),
        highlight_color=color.gold,
        pressed_color=color.orange,
        on_click=do_rebirth
    )
    all_ui_elements.append(rebirth_btn)
    
    # КНОПКА ЗАКРЫТЬ
    close_btn = Button(
        parent=camera.ui,
        text='❌ ЗАКРЫТЬ',
        scale=(0.3, 0.06),
        position=(0, -0.25),
        color=color.rgba(150, 50, 50, 220),
        highlight_color=color.red,
        on_click=close_ui
    )
    all_ui_elements.append(close_btn)

def do_rebirth():
    global money, rebirth_level, rebirth_bonus
    cost = 500 * (rebirth_level + 1)
    if money >= cost:
        money = 0
        rebirth_level += 1
        rebirth_bonus = 1.0 + rebirth_level * 0.5
        upgrades['speed'] = 0
        upgrades['range'] = 0
        upgrades['luck'] = 0
        upgrade_costs['speed'] = 100
        upgrade_costs['range'] = 150
        upgrade_costs['luck'] = 200
        inventory.clear()
        inventory_text.text = 'Украдено: 0'
        money_text.text = 'Монеты: 0'
        rebirth_text.text = f'Перерождение: {rebirth_level} | Бонус: x{rebirth_bonus:.1f}'
        create_rebirth()

# ============== НАСТРОЙКИ ==============
def create_settings():
    global ui_open, current_window, all_ui_elements
    clear_ui()
    
    # Фон
    bg = Panel(parent=camera.ui, scale=(0.55, 0.55), position=(0, 0), color=color.rgba(30, 30, 60, 250))
    all_ui_elements.append(bg)
    
    # Заголовок
    t = Text(parent=camera.ui, text='⚙ НАСТРОЙКИ', position=(0, 0.22), scale=3.5, color=color.cyan, origin=(0,0))
    all_ui_elements.append(t)
    
    # === МУЗЫКА ===
    t = Text(parent=camera.ui, text=f'♪ Музыка: {int(music_volume*100)}%', position=(-0.10, 0.10), scale=2, color=color.white, origin=(0,0))
    all_ui_elements.append(t)
    
    # Кнопка -
    minus_btn = Button(
        parent=camera.ui,
        text='-',
        scale=(0.06, 0.06),
        position=(-0.20, 0.02),
        color=color.rgba(180, 60, 60, 220),
        highlight_color=color.red,
        on_click=music_vol_down
    )
    all_ui_elements.append(minus_btn)
    
    # Кнопка +
    plus_btn = Button(
        parent=camera.ui,
        text='+',
        scale=(0.06, 0.06),
        position=(-0.08, 0.02),
        color=color.rgba(60, 180, 60, 220),
        highlight_color=color.green,
        on_click=music_vol_up
    )
    all_ui_elements.append(plus_btn)
    
    # Полоска громкости
    bar_bg = Panel(parent=camera.ui, scale=(0.12 * music_volume, 0.02), position=(-0.14, 0.02), color=color.lime, origin=(-0.5, 0))
    all_ui_elements.append(bar_bg)
    
    # === ЗВУКИ ===
    t = Text(parent=camera.ui, text=f'🔊 Звуки: {int(sfx_volume*100)}%', position=(-0.10, -0.05), scale=2, color=color.white, origin=(0,0))
    all_ui_elements.append(t)
    
    # Кнопка -
    minus_btn2 = Button(
        parent=camera.ui,
        text='-',
        scale=(0.06, 0.06),
        position=(-0.20, -0.13),
        color=color.rgba(180, 60, 60, 220),
        highlight_color=color.red,
        on_click=sfx_vol_down
    )
    all_ui_elements.append(minus_btn2)
    
    # Кнопка +
    plus_btn2 = Button(
        parent=camera.ui,
        text='+',
        scale=(0.06, 0.06),
        position=(-0.08, -0.13),
        color=color.rgba(60, 180, 60, 220),
        highlight_color=color.green,
        on_click=sfx_vol_up
    )
    all_ui_elements.append(plus_btn2)
    
    # Полоска громкости
    bar_bg2 = Panel(parent=camera.ui, scale=(0.12 * sfx_volume, 0.02), position=(-0.14, -0.13), color=color.lime, origin=(-0.5, 0))
    all_ui_elements.append(bar_bg2)
    
    # Кнопка ЗАКРЫТЬ
    close_btn = Button(
        parent=camera.ui,
        text='❌ ЗАКРЫТЬ',
        scale=(0.3, 0.06),
        position=(0, -0.24),
        color=color.rgba(150, 50, 50, 220),
        highlight_color=color.red,
        on_click=close_ui
    )
    all_ui_elements.append(close_btn)

def music_vol_up():
    global music_volume
    music_volume = min(1.0, music_volume + 0.1)
    if bg_music: bg_music.volume = music_volume
    create_settings()

def music_vol_down():
    global music_volume
    music_volume = max(0.0, music_volume - 0.1)
    if bg_music: bg_music.volume = music_volume
    create_settings()

def sfx_vol_up():
    global sfx_volume
    sfx_volume = min(1.0, sfx_volume + 0.1)
    create_settings()

def sfx_vol_down():
    global sfx_volume
    sfx_volume = max(0.0, sfx_volume - 0.1)
    create_settings()

def close_ui():
    global ui_open, current_window
    clear_ui()
    ui_open = False
    current_window = None

# ФУНКЦИИ ИГРЫ
def choose_brainrot():
    names = list(brainrot_data.keys())
    luck = upgrades['luck'] * 3
    weights = [max(1, brainrot_data[n][1] - luck) for n in names]
    return random.choices(names, weights=weights, k=1)[0]

def spawn_brot():
    x, z = random.uniform(-18, 18), random.uniform(-18, 18)
    name = choose_brainrot()
    col, rarity, size = brainrot_data[name]
    brot = Entity(model='cube', color=col, scale=(size,size,size), position=(x, size/2, z), collider='box')
    Text(text=name, parent=brot, position=(0, size/2+0.5, 0), scale=40, color=color.white, billboard=True, origin=(0,0))
    brot.brainrot_name, brot.rarity = name, rarity
    brainrots.append(brot)

for _ in range(12):
    spawn_brot()

player = Entity(model='cube', color=color.azure, scale=(1,2,1), position=(0,1.5,0), collider='box')
player.speed = 8

def update():
    global money, ui_open
    if ui_open:
        return
    
    speed = 8 + upgrades['speed'] * 1.5
    player.x += (held_keys['d'] - held_keys['a']) * speed * time.dt
    player.z += (held_keys['w'] - held_keys['s']) * speed * time.dt
    player.x, player.z = clamp(player.x, -22, 22), clamp(player.z, -22, 22)
    camera.position = Vec3(player.x, 15, player.z - 20)
    
    for brot in brainrots[:]:
        if distance(player, brot) < (3.0 + upgrades['range']):
            money += int((100 - brot.rarity) * 2 * rebirth_bonus)
            inventory.append(brot.brainrot_name)
            brainrots.remove(brot)
            destroy(brot)
            spawn_brot()
            inventory_text.text = f'Украдено: {len(inventory)}'
            money_text.text = f'Монеты: {money}'

def input(key):
    global music_volume, ui_open, current_window
    
    if key == 'escape':
        if ui_open:
            close_ui()
        else:
            application.quit()
        return
    
    if not ui_open:
        if key == 'e':
            ui_open = True
            current_window = 'shop'
            create_shop()
        elif key == 'r':
            ui_open = True
            current_window = 'rebirth'
            create_rebirth()
        elif key == 'tab':
            ui_open = True
            current_window = 'settings'
            create_settings()
        elif key == 'm' and bg_music:
            if bg_music.volume > 0:
                bg_music.volume = 0
            else:
                bg_music.volume = music_volume

app.run()