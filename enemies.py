
import random
from core import Character, Enemy, Boss, PoisonEffect, BurnEffect, FreezeEffect, Gender


class Vodyanoy(Boss):
    """Водяной - хозяин омута."""
    
    def __init__(self):
        super().__init__(
            name="Водяной",
            hp=100,
            strength=15,
            agility=8,
            intellect=15,
            description="Владыка тёмных вод, древний дух реки.",
            phase_threshold=0.4,
            gender=Gender.MALE,
            boss_id="водяной"
        )
        self.drown_used = False
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            self.strength += 5
            messages.append(f"\n  🌊 {self.name} (HP: {self.hp}/{self.max_hp}) ВЗРЕВЕЛ!")
            messages.append("  💀 «Ты утонешь в моём омуте!»")
        
        roll = random.random()
        
        if self.phase == 2 and not self.drown_used and roll < 0.25:
            self.drown_used = True
            damage = 30 + random.randint(0, 15)
            messages.append(f"  🌀 {self.name} тянет на дно!")
            messages.append(target.take_damage(damage, "утопления"))
        elif roll < 0.4:
            damage = self.strength + random.randint(3, 8)
            messages.append(f"  💧 {self.name} бьёт водяной плетью!")
            messages.append(target.take_damage(damage, "водяной плети"))
        elif roll < 0.55:
            messages.append(f"  ❄️ {self.name} призывает холод глубин!")
            target.add_effect(FreezeEffect(1))
            messages.append(f"  ❄️ {target.name} скован льдом!")
        else:
            messages.append(self.attack(target))
        
        return "\n".join(messages)


class SoloveyRazboynik(Boss):
    """Соловей-разбойник."""
    
    def __init__(self):
        super().__init__(
            name="Соловей-разбойник",
            hp=90,
            strength=16,
            agility=15,
            intellect=8,
            description="Свистом сшибает с ног богатырей.",
            phase_threshold=0.5,
            gender=Gender.MALE,
            boss_id="соловей"
        )
        self.deadly_whistle_used = False
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            messages.append(f"\n  🎵 {self.name} (HP: {self.hp}/{self.max_hp}) НАБИРАЕТ ВОЗДУХ!")
            messages.append("  💀 «Сейчас я тебя оглушу!»")
        
        roll = random.random()
        
        if self.phase == 2 and not self.deadly_whistle_used and roll < 0.3:
            self.deadly_whistle_used = True
            damage = 35 + random.randint(0, 10)
            messages.append(f"  🔊 {self.name}: СМЕРТЕЛЬНЫЙ СВИСТ!")
            messages.append(target.take_damage(damage, "смертельного свиста"))
        elif roll < 0.45:
            damage = self.strength + random.randint(0, 8)
            messages.append(f"  🎶 {self.name} свистит!")
            messages.append(target.take_damage(damage, "свиста"))
            if random.random() < 0.25:
                target.add_effect(FreezeEffect(1))
                messages.append(f"  😵 {target.name} оглушён!")
        else:
            messages.append(f"  🪵 {self.name} бьёт дубиной!")
            messages.append(self.attack(target))
        
        return "\n".join(messages)


class BabaYaga(Boss):
    """Баба-Яга."""
    
    def __init__(self):
        super().__init__(
            name="Баба-Яга",
            hp=70,
            strength=10,
            agility=12,
            intellect=20,
            description="Костяная нога, железные зубы, но мудрая.",
            phase_threshold=0.3,
            gender=Gender.FEMALE,
            boss_id="яга"
        )
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            messages.append(f"\n  🧙 {self.name} (HP: {self.hp}/{self.max_hp}) РАЗЪЯРЕНА!")
            messages.append("  💀 «Съем тебя, окаянного!»")
        
        roll = random.random()
        
        if roll < 0.25:
            messages.append(f"  ☠️ {self.name} бормочет проклятие!")
            target.add_effect(PoisonEffect(3, 5))
            verb = "проклят" if target.gender == Gender.MALE else "проклята"
            messages.append(f"  🤢 {target.name} {verb}!")
        elif roll < 0.45:
            damage = self.intellect + random.randint(3, 10)
            messages.append(f"  🔥 {self.name} швыряет огненный шар!")
            messages.append(target.take_damage(damage, "огня"))
            if random.random() < 0.2:
                target.add_effect(BurnEffect(2, 4))
                messages.append(f"  🔥 {target.name} горит!")
        elif self.phase == 2 and roll < 0.6:
            messages.append(f"  🐸 {self.name}: «Стань лягушкой!»")
            target.add_effect(FreezeEffect(1))
        else:
            messages.append(f"  🧹 {self.name} бьёт метлой!")
            messages.append(self.attack(target))
        
        return "\n".join(messages)


class Leshy(Boss):
    """Леший - хозяин леса."""
    
    def __init__(self):
        super().__init__(
            name="Леший",
            hp=120,
            strength=18,
            agility=5,
            intellect=18,
            description="Древний дух леса, хранитель чащи.",
            phase_threshold=0.4,
            gender=Gender.MALE,
            boss_id="леший"
        )
        self.roots_used = False
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            self.strength += 5
            messages.append(f"\n  🌲 ЛЕС ПРОБУЖДАЕТСЯ! {self.name} (HP: {self.hp}/{self.max_hp})")
            messages.append("  💀 «Ты не покинешь мою чащу!»")
        
        roll = random.random()
        
        if self.phase == 2 and not self.roots_used and roll < 0.25:
            self.roots_used = True
            damage = 25 + random.randint(0, 10)
            messages.append(f"  🌿 Корни вырываются из земли!")
            messages.append(target.take_damage(damage, "корней"))
            target.add_effect(FreezeEffect(1))
            messages.append(f"  🌿 {target.name} опутан корнями!")
        elif roll < 0.4:
            damage = 12 + random.randint(3, 10)
            messages.append(f"  🐺 {self.name} призывает зверей!")
            messages.append(target.take_damage(damage, "волков"))
        elif roll < 0.55:
            messages.append(f"  🍄 {self.name} напускает морок!")
            target.add_effect(PoisonEffect(2, 6))
            messages.append(f"  😵 {target.name} в дурмане!")
        else:
            messages.append(f"  🪵 {self.name} бьёт корнем!")
            messages.append(self.attack(target))
        
        return "\n".join(messages)


class ShadowKoschei(Boss):
    """Тень Кощея - финальный босс."""
    
    def __init__(self):
        super().__init__(
            name="Тень Кощея",
            hp=150,
            strength=18,
            agility=12,
            intellect=15,
            description="Тёмная тень бессмертного владыки.",
            phase_threshold=0.5,
            gender=Gender.MALE,
            boss_id="тень_кощея"
        )
        self.death_touch_used = False
    
    def choose_action(self, target: Character) -> str:
        messages = []
        
        if not self.phase_changed and self.hp < self.max_hp * self.phase_threshold:
            self.phase = 2
            self.phase_changed = True
            self.strength += 5
            messages.append(f"\n  👤 ТЕНЬ КОЩЕЯ (HP: {self.hp}/{self.max_hp}) СГУЩАЕТСЯ!")
            messages.append("  💀 «Я — БЕССМЕРТЕН!»")
        
        roll = random.random()
        
        if not self.death_touch_used and roll < 0.15:
            self.death_touch_used = True
            damage = 35 + random.randint(0, 15)
            messages.append(f"  💀 {self.name}: КАСАНИЕ СМЕРТИ!")
            messages.append(target.take_damage(damage, "касания смерти"))
        elif roll < 0.3:
            damage = self.strength + 8 + random.randint(0, 8)
            messages.append(f"  🌀 {self.name} создаёт вихрь тьмы!")
            messages.append(target.take_damage(damage, "тёмного вихря"))
        elif roll < 0.45:
            messages.append(f"  ☠️ {self.name}: «Будь проклят, смертный!»")
            target.add_effect(PoisonEffect(3, 6))
            verb = "проклят" if target.gender == Gender.MALE else "проклята"
            messages.append(f"  💀 {target.name} {verb}!")
        elif self.phase == 2 and roll < 0.6:
            damage = 20 + random.randint(0, 8)
            messages.append(f"  🖤 {self.name} поглощает жизнь!")
            messages.append(target.take_damage(damage, "поглощения"))
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + damage // 3)
            if self.hp > old_hp:
                messages.append(f"  💚 {self.name} восстанавливает {self.hp - old_hp} HP! (HP: {self.hp}/{self.max_hp})")
        else:
            messages.append(f"  ⚔️ {self.name} атакует тёмным клинком!")
            messages.append(self.attack(target))
        
        return "\n".join(messages)


class ForestSpirit(Enemy):
    """Лесной дух."""
    
    def __init__(self):
        super().__init__(
            name="Лесной дух",
            hp=35,
            strength=7,
            agility=15,
            intellect=10,
            description="Блуждающий дух заблудшего путника.",
            gender=Gender.MALE
        )
        self.boss_id = "дух"
    
    def choose_action(self, target: Character) -> str:
        if random.random() < 0.25:
            target.add_effect(FreezeEffect(1))
            return f"  👻 {self.name} (HP: {self.hp}/{self.max_hp}) пугает! {target.name} пропускает ход!"
        return self.attack(target)


class Kikimora(Enemy):
    """Кикимора."""
    
    def __init__(self):
        super().__init__(
            name="Кикимора",
            hp=50,
            strength=10,
            agility=12,
            intellect=8,
            description="Болотная нечисть с острыми когтями.",
            gender=Gender.FEMALE
        )
        self.boss_id = "кикимора"
    
    def choose_action(self, target: Character) -> str:
        if random.random() < 0.2:
            target.add_effect(PoisonEffect(2, 4))
            verb = "отравлен" if target.gender == Gender.MALE else "отравлена"
            return f"  🤢 {self.name} (HP: {self.hp}/{self.max_hp}) царапает когтями! {target.name} {verb}!"
        return self.attack(target)


class Upyr(Enemy):
    """Упырь."""
    
    def __init__(self):
        super().__init__(
            name="Упырь",
            hp=70,
            strength=14,
            agility=8,
            intellect=5,
            description="Неупокоенный мертвец, жаждущий крови.",
            gender=Gender.MALE
        )
        self.boss_id = "упырь"
    
    def choose_action(self, target: Character) -> str:
        messages = []
        if random.random() < 0.25:
            damage = 12 + random.randint(0, 8)
            messages.append(f"  🩸 {self.name} (HP: {self.hp}/{self.max_hp}) впивается клыками!")
            messages.append(target.take_damage(damage, "укуса"))
            old_hp = self.hp
            self.hp = min(self.max_hp, self.hp + damage // 2)
            if self.hp > old_hp:
                messages.append(f"  💚 {self.name} восстанавливает {self.hp - old_hp} HP!")
            return "\n".join(messages)
        return self.attack(target)
