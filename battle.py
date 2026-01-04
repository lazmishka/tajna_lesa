import random
from typing import Optional, Tuple
from core import Enemy, Item
from heroes import Hero


def get_input(prompt: str, valid_range: range) -> int:
    """Получить числовой ввод."""
    while True:
        try:
            value = int(input(prompt))
            if value in valid_range:
                return value
            print(f"  ⚠️ Введите число от {valid_range.start} до {valid_range.stop - 1}")
        except ValueError:
            print("  ⚠️ Введите число!")


def show_combat_status(hero: Hero, enemy: Enemy) -> None:
    """Показать статус боя с именами."""
    print(f"\n  {'─' * 50}")
    
    # Герой
    hero_status = f"  {hero.CLASS_ICON} {hero.name}: HP {hero.hp}/{hero.max_hp}"
    if hasattr(hero, 'mp'):
        hero_status += f" | MP {hero.mp}/{hero.max_mp}"
    print(hero_status)
    
    if hero.effects:
        effects = ", ".join(f"{e.name}({e.duration})" for e in hero.effects)
        print(f"     Эффекты {hero.name}: {effects}")
    
    # Враг
    print(f"\n  👹 {enemy.name}: HP {enemy.hp}/{enemy.max_hp}")
    if enemy.effects:
        effects = ", ".join(f"{e.name}({e.duration})" for e in enemy.effects)
        print(f"     Эффекты {enemy.name}: {effects}")
    
    print(f"  {'─' * 50}")


def choose_ability(hero: Hero) -> Optional[int]:
    """Выбор способности из списка."""
    abilities = hero.get_abilities()
    available = [(i, name, desc, avail) for i, (name, desc, avail) in enumerate(abilities)]
    
    if not any(avail for _, _, _, avail in available):
        print("  ⚠️ Нет доступных способностей!")
        return None
    
    print("\n  ⚡ СПОСОБНОСТИ:")
    for i, name, desc, avail in available:
        status = "" if avail else " [использовано]"
        print(f"    {i + 1}. {name}{status}")
        print(f"       {desc}")
    print(f"    0. Отмена")
    
    while True:
        choice = get_input("\n  Выберите способность: ", range(0, len(abilities) + 1))
        if choice == 0:
            return None
        
        idx = choice - 1
        if not available[idx][3]:
            print("  ⚠️ Эта способность уже использована!")
            continue
        return idx


def choose_item(hero: Hero, enemy: Optional[Enemy] = None) -> Optional[Item]:
    """Выбор предмета для использования в бою."""
    usable = hero.get_usable_items(in_combat=True)
    
    if not usable:
        print("  ⚠️ Нет предметов для использования в бою!")
        return None
    
    print("\n  🎒 ПРЕДМЕТЫ:")
    for i, item in enumerate(usable, 1):
        effect = item.get_effect_description()
        effect_str = f" ({effect})" if effect else ""
        target_str = " [на врага]" if item.damage > 0 else " [на себя]"
        print(f"    {i}. {item.name}{effect_str}{target_str}")
    print(f"    0. Отмена")
    
    choice = get_input("\n  Выберите предмет: ", range(0, len(usable) + 1))
    if choice == 0:
        return None
    return usable[choice - 1]


def battle(hero: Hero, enemy: Enemy, 
           can_flee: bool = True) -> Tuple[bool, str]:
    """
    Пошаговый бой.
    Возвращает: (победа: bool, результат: str)
    """
    
    print("\n" + "⚔️" * 25)
    print(f"\n  ⚔️ НАЧИНАЕТСЯ БОЙ!")
    print(f"\n  {hero.CLASS_ICON} {hero.name} (HP: {hero.hp}/{hero.max_hp})")
    print(f"  против")
    print(f"  👹 {enemy.name} (HP: {enemy.hp}/{enemy.max_hp})")
    print(f"\n  {enemy.description}")
    print("\n" + "⚔️" * 25)
    
    round_num = 1
    fled = False
    
    while hero.is_alive() and enemy.is_alive() and not fled:
        print(f"\n{'═' * 55}")
        print(f"  ══ РАУНД {round_num} ══")
        print(f"{'═' * 55}")
        
        # Показываем текущий статус (эффекты ДО их срабатывания)
        show_combat_status(hero, enemy)
        
        # Обработка эффектов героя - применяем воздействие (урон от яда и т.д.)
        hero_effect_msgs = hero.process_effects()
        if hero_effect_msgs:
            print(f"\n  📍 Эффекты {hero.name}:")
            for msg in hero_effect_msgs:
                if msg:
                    print(msg)
        
        if not hero.is_alive():
            break
        
        # Ход героя
        if hero.can_act():
            action_done = False
            
            while not action_done:
                print(f"\n  📋 ДЕЙСТВИЯ {hero.name}:")
                print(f"    1. ⚔️ Атаковать")
                print(f"    2. ⚡ Способность ({hero.get_ability_status()})")
                print(f"    3. 🎒 Предмет")
                if can_flee:
                    print(f"    4. 🏃 Бежать")
                
                max_choice = 4 if can_flee else 3
                choice = get_input(f"\n  Действие {hero.name}: ", range(1, max_choice + 1))
                
                if choice == 1:
                    print()
                    print(hero.attack(enemy))
                    action_done = True
                
                elif choice == 2:
                    if not hero.can_use_ability():
                        print("  ⚠️ Способности израсходованы!")
                        continue
                    
                    ability_idx = choose_ability(hero)
                    if ability_idx is not None:
                        print()
                        print(hero.use_ability(ability_idx, enemy))
                        action_done = True
                
                elif choice == 3:
                    item = choose_item(hero, enemy)
                    if item:
                        print()
                        target = enemy if item.damage > 0 else None
                        print(hero.use_item(item, target))
                        action_done = True
                
                elif choice == 4 and can_flee:
                    flee_chance = min(80, 30 + hero.agility)
                    if random.randint(1, 100) <= flee_chance:
                        print(f"\n  🏃 {hero.name} сбегает с поля боя!")
                        fled = True
                        action_done = True
                    else:
                        print(f"\n  ❌ Побег не удался! {enemy.name} преграждает путь!")
                        action_done = True
        else:
            print(f"\n  ❄️ {hero.name} не может действовать в этом раунде!")
        
        if fled or not enemy.is_alive():
            break
        
        # Обработка эффектов врага - применяем воздействие
        enemy_effect_msgs = enemy.process_effects()
        if enemy_effect_msgs:
            print(f"\n  📍 Эффекты {enemy.name}:")
            for msg in enemy_effect_msgs:
                if msg:
                    print(msg)
        
        if not enemy.is_alive():
            break
        
        # Ход врага
        if enemy.can_act():
            print(f"\n  👹 Ход {enemy.name}:")
            print(enemy.choose_action(hero))
        else:
            print(f"\n  ❄️ {enemy.name} не может действовать в этом раунде!")
        
        # КОНЕЦ РАУНДА - уменьшаем duration эффектов
        hero_end_msgs = hero.end_round_effects()
        enemy_end_msgs = enemy.end_round_effects()
        
        if hero_end_msgs or enemy_end_msgs:
            print(f"\n  ⏱️ Конец раунда:")
            for msg in hero_end_msgs:
                if msg:
                    print(msg)
            for msg in enemy_end_msgs:
                if msg:
                    print(msg)
        
        round_num += 1
        
        if round_num > 50:
            print("\n  ⚠️ Бой затянулся...")
            break
    
    # Результат
    print("\n" + "═" * 55)
    
    if fled:
        return False, "побег"
    
    if hero.is_alive() and not enemy.is_alive():
        print(f"\n  🏆 ПОБЕДА!")
        print(f"\n  {enemy.name} повержен!")
        
        if enemy.boss_id:
            hero.defeat_boss(enemy.boss_id)
        
        # Восстановление
        print(hero.restore_after_combat())
        
        return True, "победа"
    
    else:
        verb = "пала" if hero.gender.value == "female" else "пал"
        print(f"\n  💀 ПОРАЖЕНИЕ...")
        print(f"\n  {hero.name} {verb} в бою...")
        
        return False, "поражение"


def boss_battle(hero: Hero, boss: Enemy, intro_text: str = "") -> Tuple[bool, str]:
    """Битва с боссом - нельзя сбежать."""
    
    if intro_text:
        print(f"\n{intro_text}")
    
    print("\n" + "💀" * 25)
    print(f"\n  ⚠️ БИТВА С БОССОМ!")
    print(f"\n  👹 {boss.name} (HP: {boss.hp}/{boss.max_hp})")
    print("\n" + "💀" * 25)
    
    return battle(hero, boss, can_flee=False)


def use_item_outside_combat(hero: Hero) -> bool:
    """Использовать предмет вне боя."""
    usable = [item for item in hero.inventory if item.can_use(hero) and item.damage == 0]
    
    if not usable:
        print("\n  ⚠️ Нет предметов для использования вне боя.")
        return False
    
    print(f"\n  🎒 ПРЕДМЕТЫ {hero.name} (вне боя):")
    for i, item in enumerate(usable, 1):
        effect = item.get_effect_description()
        effect_str = f" ({effect})" if effect else ""
        print(f"    {i}. {item.name}{effect_str}")
        print(f"       {item.description}")
    print(f"    0. Отмена")
    
    choice = get_input("\n  Выберите предмет: ", range(0, len(usable) + 1))
    
    if choice == 0:
        return False
    
    item = usable[choice - 1]
    print()
    print(hero.use_item(item))
    return True
