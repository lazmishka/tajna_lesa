
import random
from typing import List, Optional, Dict, Any
from enum import Enum


class Gender(Enum):
    MALE = "male"
    FEMALE = "female"


class Effect:
    """Базовый класс эффекта."""
    
    def __init__(self, name: str, duration: int, description: str = ""):
        self.name = name
        self.duration = duration
        self.max_duration = duration
        self.description = description
        self.just_applied = True  # Не срабатывает в раунд наложения
    
    def tick(self, target: 'Character') -> str:
        """Вызывается в начале раунда. Применяет эффект (урон и т.д.)."""
        if self.just_applied:
            self.just_applied = False
            return ""
        return self._apply_effect(target)
    
    # noinspection PyUnusedLocal
    def _apply_effect(self, target: 'Character') -> str:
        """Переопределяется в подклассах для конкретного воздействия."""
        return ""
    
    # noinspection PyUnusedLocal
    def end_round(self, target: 'Character') -> str:
        """Вызывается в конце раунда. Уменьшает duration."""
        self.duration -= 1
        if self.duration <= 0:
            return self.on_expire(target)
        return ""
    
    def is_active(self) -> bool:
        return self.duration > 0
    
    # noinspection PyUnusedLocal
    def on_expire(self, target: 'Character') -> str:
        return f"  ⏰ Эффект «{self.name}» закончился."
    
    def __str__(self) -> str:
        return f"{self.name} ({self.duration} ход.)"


class PoisonEffect(Effect):
    def __init__(self, duration: int = 3, damage: int = 5):
        super().__init__("Отравление", duration)
        self.damage = damage
    
    def _apply_effect(self, target: 'Character') -> str:
        target.hp = max(0, target.hp - self.damage)
        return f"  🤢 {target.name} теряет {self.damage} HP от яда (HP: {target.hp}/{target.max_hp})"


class BurnEffect(Effect):
    def __init__(self, duration: int = 2, damage: int = 8):
        super().__init__("Горение", duration)
        self.damage = damage
    
    def _apply_effect(self, target: 'Character') -> str:
        target.hp = max(0, target.hp - self.damage)
        return f"  🔥 {target.name} получает {self.damage} урона от огня (HP: {target.hp}/{target.max_hp})"


class FreezeEffect(Effect):
    def __init__(self, duration: int = 1):
        super().__init__("Заморозка", duration)
    
    # noinspection PyUnusedLocal
    def _apply_effect(self, target: 'Character') -> str:
        # Сообщение о невозможности действовать выводится в battle.py
        # когда проверяется can_act()
        return ""


class RegenEffect(Effect):
    def __init__(self, duration: int = 3, heal: int = 15):
        super().__init__("Регенерация", duration)
        self.heal = heal
    
    def _apply_effect(self, target: 'Character') -> str:
        old_hp = target.hp
        target.hp = min(target.max_hp, target.hp + self.heal)
        healed = target.hp - old_hp
        if healed > 0:
            return f"  💚 {target.name} восстанавливает {healed} HP (HP: {target.hp}/{target.max_hp})"
        return ""


class StrengthBuff(Effect):
    def __init__(self, duration: int = 3, bonus: int = 5):
        super().__init__("Усиление", duration)
        self.bonus = bonus
        self.applied = False
    
    def apply(self, target: 'Character') -> None:
        if not self.applied:
            target.strength += self.bonus
            self.applied = True
    
    def remove(self, target: 'Character') -> None:
        if self.applied:
            target.strength -= self.bonus
            self.applied = False
    
    def _apply_effect(self, target: 'Character') -> str:
        # Бафф применяется при первом tick (после just_applied)
        self.apply(target)
        return ""
    
    def end_round(self, target: 'Character') -> str:
        self.duration -= 1
        if self.duration <= 0:
            self.remove(target)
            return self.on_expire(target)
        return ""
    
    # noinspection PyUnusedLocal
    def on_expire(self, target: 'Character') -> str:
        return f"  ⏰ Эффект «{self.name}» закончился. Сила вернулась к норме."


class Item:
    """Предмет инвентаря."""
    
    def __init__(self, name: str, description: str, item_type: str = "misc", 
                 hp_restore: int = 0, mp_restore: int = 0, damage: int = 0,
                 usable: bool = True, consumable: bool = True):
        self.name = name
        self.description = description
        self.item_type = item_type  # "heal", "mana", "damage", "quest", "key", "artifact"
        self.hp_restore = hp_restore
        self.mp_restore = mp_restore
        self.damage = damage
        self.usable = usable
        self.consumable = consumable
    
    def can_use(self, _user: 'Character', _in_combat: bool = False) -> bool:
        if not self.usable:
            return False
        if self.item_type in ("key", "artifact", "quest"):
            return False
        return True
    
    def use(self, user: 'Character', target: Optional['Character'] = None) -> str:
        messages = []
        
        if self.hp_restore > 0:
            old_hp = user.hp
            user.hp = min(user.max_hp, user.hp + self.hp_restore)
            healed = user.hp - old_hp
            messages.append(f"  💊 {user.name} использует {self.name}: +{healed} HP (HP: {user.hp}/{user.max_hp})")
        
        if self.mp_restore > 0 and hasattr(user, 'mp') and hasattr(user, 'max_mp'):
            old_mp = user.mp
            user.mp = min(user.max_mp, user.mp + self.mp_restore)
            restored = user.mp - old_mp
            messages.append(f"  💙 Восстановлено {restored} MP (MP: {user.mp}/{user.max_mp})")
        
        if self.damage > 0 and target:
            target.hp = max(0, target.hp - self.damage)
            messages.append(f"  💥 {self.name}: {self.damage} урона по {target.name}! (HP врага: {target.hp}/{target.max_hp})")
        
        return "\n".join(messages) if messages else f"  {user.name} использует {self.name}..."
    
    def get_effect_description(self) -> str:
        effects = []
        if self.hp_restore > 0:
            effects.append(f"+{self.hp_restore} HP")
        if self.mp_restore > 0:
            effects.append(f"+{self.mp_restore} MP")
        if self.damage > 0:
            effects.append(f"{self.damage} урона")
        return ", ".join(effects) if effects else ""
    
    def __str__(self) -> str:
        return self.name


class Artifact:
    """Артефакт - сюжетный предмет с особыми свойствами."""
    
    def __init__(self, artifact_id: str, name: str, description: str, 
                 usage: str = "", combat_bonus: Dict[str, int] = None):
        self.id = artifact_id
        self.name = name
        self.description = description
        self.usage = usage  # Как использовать
        self.combat_bonus = combat_bonus or {}  # Бонусы в бою против определённых врагов
    
    def get_full_description(self) -> str:
        lines = [f"  {self.name}", f"    {self.description}"]
        if self.usage:
            lines.append(f"    💡 {self.usage}")
        return "\n".join(lines)
    
    def __str__(self) -> str:
        return self.name


# Определения артефактов
ARTIFACTS = {
    "klubok": Artifact(
        "klubok", "🧶 Клубок-путеводитель",
        "Волшебный клубок, указывающий путь в лесу.",
        "Автоматически показывает верный путь в запутанных местах."
    ),
    "zolotoy_kluch": Artifact(
        "zolotoy_kluch", "🔑 Золотой ключ",
        "Один из трёх ключей к сундуку сокровищ.",
        "Нужен для открытия сундука в Сердце Леса. Нельзя отдавать!"
    ),
    "serebryany_kluch": Artifact(
        "serebryany_kluch", "🔑 Серебряный ключ", 
        "Один из трёх ключей к сундуку сокровищ.",
        "Нужен для открытия сундука в Сердце Леса. Нельзя отдавать!"
    ),
    "kostyanoy_kluch": Artifact(
        "kostyanoy_kluch", "🔑 Костяной ключ",
        "Один из трёх ключей к сундуку сокровищ.",
        "Нужен для открытия сундука в Сердце Леса. Нельзя отдавать!"
    ),
    "dudochka": Artifact(
        "dudochka", "🎵 Дудочка Лешего",
        "Дудочка из старой ивы, дарованная Лешим.",
        "Призывает духов леса на помощь в финальном бою.",
        {"shadow": 20}  # -20 HP тени
    ),
    "yayco": Artifact(
        "yayco", "🥚 Яйцо Соловья",
        "Яйцо из гнезда Соловья-разбойника.",
        "Ослабляет Тень Кощея в финальном бою.",
        {"shadow": 25}
    ),
    "mech": Artifact(
        "mech", "⚔️ Меч-кладенец",
        "Легендарный меч, разящий нечисть.",
        "Даёт +12 к силе в бою с Тенью Кощея.",
        {"shadow_strength": 12}
    ),
    "voda_zhizni": Artifact(
        "voda_zhizni", "💧 Живая вода",
        "Вода из источника Водяного.",
        "Полностью восстанавливает здоровье перед финальным боем."
    ),
    "pero": Artifact(
        "pero", "🔥 Перо Жар-птицы",
        "Сияющее перо, хранящее огонь.",
        "Можно использовать в бою: наносит 40 огненного урона (одноразово)."
    ),
    "zerkalce": Artifact(
        "zerkalce", "🪞 Зеркальце Правды",
        "Показывает истинную суть вещей.",
        "Раскрывает слабости врагов, снижает их уклонение."
    ),
    "persten": Artifact(
        "persten", "💍 Кощеев перстень",
        "Знак слуги Кощея. Холоден как смерть.",
        "Позволяет проходить тайными тропами и пугает NPC."
    )
}


class Character:
    """Базовый класс персонажа."""
    
    def __init__(self, name: str, hp: int, strength: int, agility: int, intellect: int,
                 gender: Gender = Gender.MALE):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.strength = strength
        self.base_strength = strength
        self.agility = agility
        self.intellect = intellect
        self.gender = gender
        self.effects: List[Effect] = []
        self.inventory: List[Item] = []
        self.artifacts: List[Artifact] = []
    
    def is_alive(self) -> bool:
        return self.hp > 0
    
    def can_act(self) -> bool:
        for effect in self.effects:
            if isinstance(effect, FreezeEffect) and effect.is_active():
                return False
        return self.is_alive()
    
    def add_effect(self, effect: Effect) -> str:
        # Удаляем старый эффект того же типа
        self.effects = [e for e in self.effects if type(e) != type(effect)]
        self.effects.append(effect)
        # НЕ применяем StrengthBuff сразу - он применится в следующем раунде через tick()
        return f"  🔮 Эффект «{effect.name}» наложен на {effect.duration} ходов!"
    
    def process_effects(self) -> List[str]:
        """Обработка эффектов в начале раунда - применяет воздействие."""
        messages = []
        
        for effect in self.effects:
            msg = effect.tick(self)
            if msg:
                messages.append(msg)
        
        return messages
    
    def end_round_effects(self) -> List[str]:
        """Обработка эффектов в конце раунда - уменьшает duration."""
        messages = []
        
        for effect in self.effects:
            msg = effect.end_round(self)
            if msg:
                messages.append(msg)
        
        # Удаляем истёкшие эффекты
        self.effects = [e for e in self.effects if e.is_active()]
        
        return messages
    
    def take_damage(self, damage: int, _source: str = "") -> str:
        if random.randint(1, 100) <= self.agility:
            return f"  🌀 {self.name} уворачивается от атаки!"
        
        actual_damage = max(1, damage)
        self.hp = max(0, self.hp - actual_damage)
        
        return f"  💥 {self.name} получает {actual_damage} урона (HP: {self.hp}/{self.max_hp})"
    
    def heal(self, amount: int) -> str:
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        healed = self.hp - old_hp
        return f"  💚 {self.name} восстанавливает {healed} HP (HP: {self.hp}/{self.max_hp})"
    
    def attack(self, target: 'Character') -> str:
        damage = self.strength + random.randint(-2, 3)
        return target.take_damage(damage, self.name)
    
    def add_item(self, item: Item) -> str:
        self.inventory.append(item)
        effect = item.get_effect_description()
        effect_str = f" ({effect})" if effect else ""
        return f"  🎒 Получено: {item.name}{effect_str}"
    
    def remove_item(self, item: Item) -> None:
        if item in self.inventory:
            self.inventory.remove(item)
    
    def find_item(self, name_part: str) -> Optional[Item]:
        for item in self.inventory:
            if name_part.lower() in item.name.lower():
                return item
        return None
    
    def use_item(self, item: Item, target: Optional['Character'] = None) -> str:
        if item not in self.inventory:
            return "  ⚠️ Предмета нет в инвентаре!"
        if not item.can_use(self):
            return f"  ⚠️ {item.name} нельзя использовать!"
        
        result = item.use(self, target)
        if item.consumable:
            self.remove_item(item)
        return result
    
    def get_usable_items(self, in_combat: bool = False) -> List[Item]:
        return [item for item in self.inventory if item.can_use(self, in_combat)]
    
    def add_artifact(self, artifact_id: str) -> str:
        if artifact_id in ARTIFACTS:
            artifact = ARTIFACTS[artifact_id]
            if not self.has_artifact(artifact_id):
                self.artifacts.append(artifact)
                return f"  🏆 Получен артефакт: {artifact.name}\n    {artifact.description}"
        return ""
    
    def has_artifact(self, artifact_id: str) -> bool:
        return any(a.id == artifact_id for a in self.artifacts)
    
    def get_artifact(self, artifact_id: str) -> Optional[Artifact]:
        for a in self.artifacts:
            if a.id == artifact_id:
                return a
        return None
    
    def count_keys(self) -> int:
        count = 0
        if self.has_artifact("zolotoy_kluch"):
            count += 1
        if self.has_artifact("serebryany_kluch"):
            count += 1
        if self.has_artifact("kostyanoy_kluch"):
            count += 1
        return count
    
    def show_inventory(self) -> str:
        lines = ["\n  🎒 ИНВЕНТАРЬ:"]
        
        if self.inventory:
            lines.append("\n  📦 Предметы:")
            for i, item in enumerate(self.inventory, 1):
                effect = item.get_effect_description()
                effect_str = f" ({effect})" if effect else ""
                use_str = "" if item.usable and item.item_type not in ("key", "artifact", "quest") else " [сюжетный]"
                lines.append(f"    {i}. {item.name}{effect_str}{use_str}")
        else:
            lines.append("  📦 Предметы: нет")
        
        if self.artifacts:
            lines.append("\n  🏆 Артефакты:")
            for artifact in self.artifacts:
                lines.append(f"    • {artifact.name}")
                lines.append(f"      {artifact.description}")
        else:
            lines.append("\n  🏆 Артефакты: нет")
        
        return "\n".join(lines)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "strength": self.strength,
            "base_strength": self.base_strength,
            "agility": self.agility,
            "intellect": self.intellect,
            "gender": self.gender.value,
            "effects": [(type(e).__name__, e.duration) for e in self.effects],
            "inventory": [{"name": item.name, "desc": item.description, "type": item.item_type,
                          "hp": item.hp_restore, "mp": item.mp_restore, "damage": item.damage,
                          "usable": item.usable, "consumable": item.consumable}
                         for item in self.inventory],
            "artifacts": [a.id for a in self.artifacts]
        }


class Enemy(Character):
    """Базовый класс врага."""
    
    def __init__(self, name: str, hp: int, strength: int, agility: int = 5, 
                 intellect: int = 5, description: str = "", gender: Gender = Gender.MALE):
        super().__init__(name, hp, strength, agility, intellect, gender)
        self.description = description
        self.phase = 1
        self.is_defeated = False
        self.boss_id = ""
    
    def choose_action(self, target: Character) -> str:
        return self.attack(target)


class Boss(Enemy):
    """Босс с фазами."""
    
    def __init__(self, name: str, hp: int, strength: int, agility: int = 10,
                 intellect: int = 10, description: str = "", phase_threshold: float = 0.5,
                 gender: Gender = Gender.MALE, boss_id: str = ""):
        super().__init__(name, hp, strength, agility, intellect, description, gender)
        self.phase_threshold = phase_threshold
        self.phase_changed = False
        self.boss_id = boss_id
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            self.strength += 3
            messages.append(f"\n  ⚠️ {self.name} переходит в ЯРОСТЬ!")
        
        if self.phase == 2 and random.random() < 0.25:
            damage = self.strength + random.randint(2, 6)
            messages.append(f"  ⚡ {self.name} наносит мощный удар!")
            messages.append(target.take_damage(damage, self.name))
        else:
            messages.append(self.attack(target))
        
        return "\n".join(messages)
