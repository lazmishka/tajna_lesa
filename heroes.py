
import random
from typing import List, Optional, Dict, Any
from core import (Character, Item, RegenEffect, StrengthBuff, 
                  FreezeEffect, PoisonEffect, Gender)


class Hero(Character):
    """Базовый класс игрового персонажа."""
    
    CLASS_ID = ""
    CLASS_NAME = ""
    CLASS_ICON = ""
    
    def __init__(self, name: str, hp: int, strength: int, agility: int, intellect: int,
                 gender: Gender = Gender.MALE):
        super().__init__(name, hp, strength, agility, intellect, gender)
        self.ability_uses = 0
        self.max_abilities = 3
        self.visited_locations: List[str] = []
        self.defeated_bosses: List[str] = []
        self.npc_relations: Dict[str, str] = {}  # "мирно", "враждебно", "нейтрально"
        self.game_flags: Dict[str, Any] = {}
        self.path_taken: str = ""
    
    def get_abilities(self) -> List[tuple]:
        """Возвращает [(имя, описание, доступна), ...]"""
        return []
    
    def use_ability(self, ability_index: int, target: Optional[Character] = None) -> str:
        if self.ability_uses >= self.max_abilities:
            return "  ⚠️ Способности израсходованы!"
        
        abilities = self.get_abilities()
        if ability_index < 0 or ability_index >= len(abilities):
            return "  ⚠️ Неверная способность!"
        
        name, desc, available = abilities[ability_index]
        if not available:
            return "  ⚠️ Эта способность недоступна!"
        
        self.ability_uses += 1
        return self._perform_ability(ability_index, target)
    
    def _perform_ability(self, ability_index: int, target: Optional[Character] = None) -> str:
        return "  Способность не определена."
    
    def can_use_ability(self) -> bool:
        return self.ability_uses < self.max_abilities
    
    def get_ability_status(self) -> str:
        remaining = self.max_abilities - self.ability_uses
        return f"{remaining}/{self.max_abilities}"
    
    def visit_location(self, location: str) -> None:
        if location not in self.visited_locations:
            self.visited_locations.append(location)
    
    def has_visited(self, location: str) -> bool:
        return location in self.visited_locations
    
    def defeat_boss(self, boss_id: str) -> None:
        if boss_id and boss_id not in self.defeated_bosses:
            self.defeated_bosses.append(boss_id)
    
    def is_boss_defeated(self, boss_id: str) -> bool:
        return boss_id in self.defeated_bosses
    
    def set_npc_relation(self, npc: str, relation: str) -> None:
        self.npc_relations[npc] = relation
    
    def get_npc_relation(self, npc: str) -> str:
        return self.npc_relations.get(npc, "нейтрально")
    
    def set_flag(self, flag: str, value: Any = True) -> None:
        self.game_flags[flag] = value
    
    def get_flag(self, flag: str, default: Any = None) -> Any:
        return self.game_flags.get(flag, default)
    
    def restore_after_combat(self) -> str:
        """Восстановление после боя."""
        heal = self.max_hp // 4
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + heal)
        return f"  💚 Восстановлено {self.hp - old_hp} HP после победы (HP: {self.hp}/{self.max_hp})"
    
    def get_full_status(self) -> str:
        lines = [
            f"\n{'═' * 50}",
            f"  {self.CLASS_ICON} {self.name}",
            f"{'═' * 50}",
            f"  ❤️  HP: {self.hp}/{self.max_hp}",
            f"  ⚔️  Сила: {self.strength}",
            f"  🏃 Ловкость: {self.agility}",
            f"  🧠 Интеллект: {self.intellect}",
            f"  ⚡ Способности: {self.get_ability_status()} осталось",
        ]
        
        if self.effects:
            lines.append(f"\n  🔮 АКТИВНЫЕ ЭФФЕКТЫ:")
            for e in self.effects:
                lines.append(f"    • {e}")
        
        if self.inventory:
            lines.append(f"\n  🎒 ПРЕДМЕТЫ ({len(self.inventory)}):")
            for item in self.inventory[:5]:
                effect = item.get_effect_description()
                effect_str = f" ({effect})" if effect else ""
                lines.append(f"    • {item.name}{effect_str}")
            if len(self.inventory) > 5:
                lines.append(f"    ... и ещё {len(self.inventory) - 5}")
        
        if self.artifacts:
            lines.append(f"\n  🏆 АРТЕФАКТЫ ({len(self.artifacts)}):")
            for art in self.artifacts:
                lines.append(f"    • {art.name}")
        
        lines.append(f"{'═' * 50}")
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            "class_id": self.CLASS_ID,
            "ability_uses": self.ability_uses,
            "visited_locations": self.visited_locations,
            "defeated_bosses": self.defeated_bosses,
            "npc_relations": self.npc_relations,
            "game_flags": self.game_flags,
            "path_taken": self.path_taken,
        })
        return data


class Ivan(Hero):
    """Иван-дурак - удача и простота."""
    
    CLASS_ID = "иван"
    CLASS_NAME = "Иван-дурак"
    CLASS_ICON = "🤪"
    
    def __init__(self):
        super().__init__(
            name="Иван-дурак",
            hp=120,
            strength=14,
            agility=18,
            intellect=5,
            gender=Gender.MALE
        )
        self.max_abilities = 3
        
        # Начальный инвентарь - минимум
        self.inventory = [
            Item("🍞 Краюха хлеба", "Мать дала в дорогу. Можно съесть или отдать кому-то.", 
                 "quest", hp_restore=40, usable=False),  # Сюжетный предмет
        ]
    
    def get_abilities(self) -> List[tuple]:
        remaining = self.max_abilities - self.ability_uses
        return [
            ("🍀 Дурацкое счастье", "Невероятная удача - крит или исцеление", remaining > 0),
            ("😊 Добрая улыбка", "Обезоруживает врага на 1 ход", remaining > 0),
            ("🎲 Авось!", "Случайный мощный эффект", remaining > 0),
        ]
    
    def _perform_ability(self, ability_index: int, target: Optional[Character] = None) -> str:
        if ability_index == 0:
            messages = ["  🍀 ДУРАЦКОЕ СЧАСТЬЕ!"]
            luck = random.random()
            
            if target and luck < 0.5:
                damage = self.strength * 3 + random.randint(10, 25)
                messages.append(f"  💫 «Эх, была не была!»")
                messages.append(target.take_damage(damage, "невероятной удачи"))
            else:
                heal = random.randint(40, 70)
                self.hp = min(self.max_hp, self.hp + heal)
                messages.append(f"  💚 Удача улыбается! +{heal} HP (HP: {self.hp}/{self.max_hp})")
            return "\n".join(messages)
        
        elif ability_index == 1:
            messages = ["  😊 ДОБРАЯ УЛЫБКА!"]
            if target:
                target.add_effect(FreezeEffect(1))
                messages.append(f"  😊 {target.name} растерялся от доброты и пропускает ход!")
            return "\n".join(messages)
        
        else:
            messages = ["  🎲 АВОСЬ!"]
            roll = random.random()
            
            if roll < 0.33 and target:
                damage = self.strength * 4
                messages.append(target.take_damage(damage, "невероятного удара"))
            elif roll < 0.66:
                self.hp = self.max_hp
                messages.append(f"  💚 Полное исцеление! HP: {self.hp}/{self.max_hp}")
            else:
                self.add_effect(StrengthBuff(3, 10))
                messages.append("  💪 Сила +10 на 3 хода!")
            return "\n".join(messages)
    
    def attack(self, target: Character) -> str:
        if random.random() < 0.25:
            damage = self.strength * 2 + random.randint(5, 10)
            target.hp = max(0, target.hp - damage)
            return f"  🍀 КРИТ! {self.name} наносит {damage} урона {target.name}! (HP врага: {target.hp}/{target.max_hp})"
        return super().attack(target)


class Vasilisa(Hero):
    """Василиса Премудрая - магия и мудрость."""
    
    CLASS_ID = "василиса"
    CLASS_NAME = "Василиса Премудрая"
    CLASS_ICON = "✨"
    
    def __init__(self):
        super().__init__(
            name="Василиса Премудрая",
            hp=100,
            strength=10,
            agility=12,
            intellect=25,
            gender=Gender.FEMALE
        )
        self.mp = 80
        self.max_mp = 80
        self.spells_used = [False, False, False]
        
        # Начальный инвентарь - минимум
        self.inventory = [
            Item("💧 Зелье маны", "Восстанавливает 30 MP", "mana", mp_restore=30),
        ]
        
        # Начальный артефакт
        self.add_artifact("zerkalce")
    
    def get_abilities(self) -> List[tuple]:
        return [
            ("💡 Свет-светоч", "Урон + сильное исцеление + регенерация", not self.spells_used[0]),
            ("👣 Тихий шаг", "Ловкость +40 (почти невозможно попасть)", not self.spells_used[1]),
            ("👁️ Вещий взор", "Сильный урон + заморозка 2 хода", not self.spells_used[2]),
        ]
    
    def can_use_ability(self) -> bool:
        return any(not used for used in self.spells_used)
    
    def get_ability_status(self) -> str:
        remaining = sum(1 for used in self.spells_used if not used)
        return f"{remaining}/3"
    
    def _perform_ability(self, ability_index: int, target: Optional[Character] = None) -> str:
        if ability_index < 0 or ability_index > 2:
            return "  ⚠️ Неверное заклинание!"
        
        if self.spells_used[ability_index]:
            return "  ⚠️ Это заклинание уже использовано!"
        
        self.spells_used[ability_index] = True
        
        if ability_index == 0:
            messages = ["  💡 СВЕТ-СВЕТОЧ!"]
            if target:
                damage = self.intellect * 2
                messages.append(target.take_damage(damage, "священного света"))
            
            heal = self.intellect * 2
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + heal)
            messages.append(f"  ✨ Василиса восстанавливает {self.hp - old_hp} HP (HP: {self.hp}/{self.max_hp})")
            
            self.add_effect(RegenEffect(3, 15))
            messages.append("  💚 Регенерация на 3 хода!")
            return "\n".join(messages)
        
        elif ability_index == 1:
            messages = ["  👣 ТИХИЙ ШАГ!"]
            self.agility += 40
            messages.append("  🌫️ Василиса становится почти невидимой!")
            messages.append("  🏃 Ловкость +40 (эффект постоянный)")
            return "\n".join(messages)
        
        else:
            messages = ["  👁️ ВЕЩИЙ ВЗОР!"]
            if target:
                damage = self.intellect * 3
                messages.append(target.take_damage(damage, "ледяного взгляда"))
                target.add_effect(FreezeEffect(2))
                messages.append(f"  ❄️ {target.name} заморожен на 2 хода!")
            return "\n".join(messages)
    
    def attack(self, target: Character) -> str:
        if self.mp >= 8:
            self.mp -= 8
            damage = self.intellect + random.randint(8, 18)
            target.hp = max(0, target.hp - damage)
            return f"  ✨ Магическая атака! {damage} урона {target.name} (HP врага: {target.hp}/{target.max_hp}, MP: {self.mp}/{self.max_mp})"
        else:
            damage = self.strength + random.randint(0, 3)
            target.hp = max(0, target.hp - damage)
            return f"  👊 Атака посохом: {damage} урона {target.name} (мана истощена!)"
    
    def restore_mp(self, amount: int) -> str:
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        restored = self.mp - old_mp
        return f"  💙 Восстановлено {restored} MP (MP: {self.mp}/{self.max_mp})"
    
    def get_full_status(self) -> str:
        status = super().get_full_status()
        lines = status.split("\n")
        for i, line in enumerate(lines):
            if "❤️  HP:" in line:
                lines.insert(i + 1, f"  💙 MP: {self.mp}/{self.max_mp}")
                break
        return "\n".join(lines)
    
    def restore_after_combat(self) -> str:
        result = super().restore_after_combat()
        mp_restore = self.max_mp // 4
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + mp_restore)
        return result + f"\n  💙 Восстановлено {self.mp - old_mp} MP (MP: {self.mp}/{self.max_mp})"
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["mp"] = self.mp
        data["max_mp"] = self.max_mp
        data["spells_used"] = self.spells_used
        return data


class Sluga(Hero):
    """Кощеев слуга - хитрость и тёмные знания."""
    
    CLASS_ID = "слуга"
    CLASS_NAME = "Кощеев слуга"
    CLASS_ICON = "🗡️"
    
    def __init__(self):
        super().__init__(
            name="Кощеев слуга",
            hp=110,
            strength=18,
            agility=15,
            intellect=12,
            gender=Gender.MALE
        )
        self.max_abilities = 2
        
        # Начальный инвентарь - минимум
        self.inventory = [
            Item("☠️ Яд Кощея", "Отравленный кинжал. Наносит 35 урона + яд.", "damage", damage=35),
        ]
        
        # Начальный артефакт
        self.add_artifact("persten")
    
    def get_abilities(self) -> List[tuple]:
        remaining = self.max_abilities - self.ability_uses
        return [
            ("🌑 Удар в спину", "Огромный урон + отравление", remaining > 0),
            ("💀 Тёмное знание", "Ослабляет врага (-10 силы)", remaining > 0),
        ]
    
    def _perform_ability(self, ability_index: int, target: Optional[Character] = None) -> str:
        if ability_index == 0:
            messages = ["  🌑 УДАР В СПИНУ!"]
            if target:
                damage = self.strength * 3 + random.randint(15, 30)
                messages.append(f"  🗡️ «Кощей научил меня кое-чему...»")
                messages.append(target.take_damage(damage, "предательского удара"))
                target.add_effect(PoisonEffect(3, 10))
                messages.append(f"  ☠️ {target.name} отравлен!")
            return "\n".join(messages)
        
        else:
            messages = ["  💀 ТЁМНОЕ ЗНАНИЕ!"]
            if target:
                target.strength = max(1, target.strength - 10)
                messages.append(f"  💀 «Я знаю твои слабости...»")
                messages.append(f"  ⬇️ Сила {target.name} снижена на 10!")
            return "\n".join(messages)
    
    def attack(self, target: Character) -> str:
        if random.random() < 0.30:
            damage = self.strength * 2 + random.randint(5, 15)
            target.hp = max(0, target.hp - damage)
            return f"  🗡️ УДАР В ТЕНЬ! {damage} урона {target.name}! (HP врага: {target.hp}/{target.max_hp})"
        return super().attack(target)


def create_hero(class_id: str) -> Hero:
    classes = {
        "иван": Ivan,
        "василиса": Vasilisa,
        "слуга": Sluga
    }
    hero_class = classes.get(class_id)
    if hero_class:
        return hero_class()
    raise ValueError(f"Неизвестный класс: {class_id}")


def get_class_description(class_id: str) -> str:
    descriptions = {
        "иван": """
    🤪 ИВАН-ДУРАК
    
    Младший сын крестьянина. Удача сама идёт ему в руки.
    
    ❤️ HP: 120 | ⚔️ Сила: 14 | 🏃 Ловкость: 18 | 🧠 Интеллект: 5
    
    ⚡ СПОСОБНОСТИ (выбор любой, всего 3 раза):
       🍀 Дурацкое счастье — крит или исцеление
       😊 Добрая улыбка — враг пропускает ход
       🎲 Авось! — случайный мощный эффект
    
    💡 ОСОБЕННОСТИ:
       • 25% шанс критического удара
       • Доброта открывает мирные пути
       • Начинает с краюхой хлеба (сюжетный предмет)
""",
        "василиса": """
    ✨ ВАСИЛИСА ПРЕМУДРАЯ
    
    Дочь колдуна, сбежавшая из плена Кощея. Магия в её крови.
    
    ❤️ HP: 100 | 💙 MP: 80 | ⚔️ Сила: 10 | 🏃 Ловкость: 12 | 🧠 Интеллект: 25
    
    ⚡ ЗАКЛИНАНИЯ (каждое один раз):
       💡 Свет-светоч — урон + сильное исцеление + регенерация
       👣 Тихий шаг — ловкость +40 (постоянно)
       👁️ Вещий взор — сильный урон + заморозка 2 хода
    
    💡 ОСОБЕННОСТИ:
       • Магические атаки (расход MP)
       • Автоматически решает загадки
       • Начинает с зеркальцем (артефакт) и зельем маны
""",
        "слуга": """
    🗡️ КОЩЕЕВ СЛУГА
    
    Бывший раб Кощея. Знает его секреты и тайные тропы.
    
    ❤️ HP: 110 | ⚔️ Сила: 18 | 🏃 Ловкость: 15 | 🧠 Интеллект: 12
    
    ⚡ СПОСОБНОСТИ (всего 2 раза):
       🌑 Удар в спину — огромный урон + отравление
       💀 Тёмное знание — ослабляет врага (-10 силы)
    
    💡 ОСОБЕННОСТИ:
       • 30% шанс скрытной атаки (x2 урон)
       • Доступ к тайной тропе
       • Начинает с перстнем Кощея (артефакт) и ядом
"""
    }
    return descriptions.get(class_id, "Описание недоступно")
