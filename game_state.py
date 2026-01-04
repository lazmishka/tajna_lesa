

import os
import json
import hashlib
import copy
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict, fields


SAVE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_games")


# Глобальная переменная для хранения последнего приглашения
_last_prompt_info = {
    "text": "",
    "options": [],
    "valid_range": None,
    "prompt": ""
}


def set_last_prompt(text: str, options: Optional[List[str]] = None, 
                   valid_range: Optional[range] = None, prompt: str = "") -> None:
    """Сохранить последнее приглашение для повтора после меню."""
    _last_prompt_info["text"] = text
    _last_prompt_info["options"] = options or []
    _last_prompt_info["valid_range"] = valid_range
    _last_prompt_info["prompt"] = prompt


def show_last_prompt() -> None:
    """Показать последнее приглашение."""
    if _last_prompt_info["text"]:
        print(_last_prompt_info["text"])
    for opt in _last_prompt_info["options"]:
        print(opt)


@dataclass
class GameState:
    """Состояние игры."""
    
    class_id: str = ""
    player_name: str = ""
    hp: int = 100
    max_hp: int = 100
    strength: int = 10
    base_strength: int = 10
    agility: int = 10
    intellect: int = 10
    mp: int = 0
    max_mp: int = 0
    ability_uses: int = 0
    spells_used: List[bool] = field(default_factory=lambda: [False, False, False])
    
    current_location: str = "opushka"
    visited_locations: List[str] = field(default_factory=list)
    defeated_bosses: List[str] = field(default_factory=list)
    inventory: List[Dict] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    
    npc_relations: Dict[str, str] = field(default_factory=dict)
    game_flags: Dict[str, Any] = field(default_factory=dict)
    path_taken: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        valid_fields = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in data.items() if k in valid_fields})
    
    def copy(self) -> 'GameState':
        return GameState.from_dict(copy.deepcopy(self.to_dict()))


class GameManager:
    """Менеджер игры."""
    
    def __init__(self):
        self.account_name: str = ""
        self.password_hash: str = ""
        self.current_state: Optional[GameState] = None
        self.saved_state: Optional[GameState] = None
        self.hero = None
        
        self.stats: Dict[str, Any] = {
            "victories": {"иван": [], "василиса": [], "слуга": []},
            "defeats": 0,
            "total_games": 0
        }
        
        os.makedirs(SAVE_DIR, exist_ok=True)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def get_save_path(self) -> str:
        safe_name = "".join(c for c in self.account_name if c.isalnum() or c in ('_', '-'))
        return os.path.join(SAVE_DIR, f"{safe_name}.json")
    
    @staticmethod
    def account_exists(name: str) -> bool:
        safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
        return os.path.exists(os.path.join(SAVE_DIR, f"{safe_name}.json"))
    
    def create_account(self, name: str, password: str) -> bool:
        self.account_name = name
        self.password_hash = self.hash_password(password)
        self.stats = {
            "victories": {"иван": [], "василиса": [], "слуга": []},
            "defeats": 0,
            "total_games": 0
        }
        self.current_state = None
        self.saved_state = None
        return self._save_account()
    
    def login(self, name: str, password: str) -> bool:
        safe_name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
        path = os.path.join(SAVE_DIR, f"{safe_name}.json")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data.get("password_hash") != self.hash_password(password):
                return False
            
            self.account_name = name
            self.password_hash = data["password_hash"]
            self.stats = data.get("stats", {
                "victories": {"иван": [], "василиса": [], "слуга": []},
                "defeats": 0,
                "total_games": 0
            })
            
            saved_game = data.get("saved_game")
            if saved_game:
                self.saved_state = GameState.from_dict(saved_game)
                self.current_state = self.saved_state.copy()
            else:
                self.saved_state = None
                self.current_state = None
            
            return True
        except (IOError, KeyError, json.JSONDecodeError):
            return False
    
    def _save_account(self) -> bool:
        data = {
            "password_hash": self.password_hash,
            "stats": self.stats,
            "saved_game": self.saved_state.to_dict() if self.saved_state else None
        }
        
        path = self.get_save_path()
        temp_path = path + ".tmp"
        
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            if os.path.exists(path):
                os.remove(path)
            os.rename(temp_path, path)
            return True
        except IOError:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return False
    
    def state_differs_from_saved(self) -> bool:
        if self.current_state is None:
            return False
        if self.saved_state is None:
            return True
        
        current = self.current_state.to_dict()
        saved = self.saved_state.to_dict()
        
        keys = ['class_id', 'hp', 'max_hp', 'strength', 'mp', 'max_mp',
                'ability_uses', 'current_location', 'visited_locations', 
                'defeated_bosses', 'inventory', 'artifacts',
                'npc_relations', 'game_flags', 'path_taken']
        
        for key in keys:
            if current.get(key) != saved.get(key):
                return True
        return False
    
    def has_saved_game(self) -> bool:
        return self.saved_state is not None
    
    def can_load(self) -> bool:
        return self.has_saved_game()
    
    def can_save(self) -> bool:
        return self.current_state is not None and self.state_differs_from_saved()
    
    def save_game(self) -> bool:
        if self.current_state is None:
            return False
        self.saved_state = self.current_state.copy()
        return self._save_account()
    
    def load_game(self) -> bool:
        if self.saved_state is None:
            return False
        self.current_state = self.saved_state.copy()
        return True
    
    def new_game(self, class_id: str) -> None:
        self.current_state = GameState(class_id=class_id)
    
    def clear_saved_game(self) -> bool:
        self.saved_state = None
        self.current_state = None
        return self._save_account()
    
    def sync_from_hero(self, hero) -> None:
        """Синхронизировать состояние из героя."""
        if self.current_state is None:
            self.current_state = GameState()
        
        self.current_state.class_id = hero.CLASS_ID
        self.current_state.player_name = hero.name
        self.current_state.hp = hero.hp
        self.current_state.max_hp = hero.max_hp
        self.current_state.strength = hero.strength
        self.current_state.base_strength = hero.base_strength
        self.current_state.agility = hero.agility
        self.current_state.intellect = hero.intellect
        self.current_state.ability_uses = hero.ability_uses
        self.current_state.visited_locations = list(hero.visited_locations)
        self.current_state.defeated_bosses = list(hero.defeated_bosses)
        self.current_state.npc_relations = dict(hero.npc_relations)
        self.current_state.game_flags = dict(hero.game_flags)
        self.current_state.path_taken = hero.path_taken
        
        self.current_state.inventory = [
            {"name": item.name, "desc": item.description, "type": item.item_type,
             "hp": item.hp_restore, "mp": item.mp_restore, "damage": item.damage,
             "usable": item.usable, "consumable": item.consumable}
            for item in hero.inventory
        ]
        
        self.current_state.artifacts = [a.id for a in hero.artifacts]
        
        if hasattr(hero, 'mp'):
            self.current_state.mp = hero.mp
            self.current_state.max_mp = hero.max_mp
        if hasattr(hero, 'spells_used'):
            self.current_state.spells_used = list(hero.spells_used)
        
        self.hero = hero
    
    def sync_to_hero(self, hero) -> None:
        """Синхронизировать состояние в героя."""
        if self.current_state is None:
            return
        
        from core import Item, ARTIFACTS
        
        hero.hp = self.current_state.hp
        hero.max_hp = self.current_state.max_hp
        hero.strength = self.current_state.strength
        hero.base_strength = self.current_state.base_strength
        hero.agility = self.current_state.agility
        hero.intellect = self.current_state.intellect
        hero.ability_uses = self.current_state.ability_uses
        hero.visited_locations = list(self.current_state.visited_locations)
        hero.defeated_bosses = list(self.current_state.defeated_bosses)
        hero.npc_relations = dict(self.current_state.npc_relations)
        hero.game_flags = dict(self.current_state.game_flags)
        hero.path_taken = self.current_state.path_taken
        
        hero.inventory = [
            Item(i["name"], i["desc"], i["type"], i["hp"], i["mp"], 
                 i["damage"], i["usable"], i["consumable"])
            for i in self.current_state.inventory
        ]
        
        hero.artifacts = []
        for art_id in self.current_state.artifacts:
            if art_id in ARTIFACTS:
                hero.artifacts.append(ARTIFACTS[art_id])
        
        if hasattr(hero, 'mp'):
            hero.mp = self.current_state.mp
            hero.max_mp = self.current_state.max_mp
        if hasattr(hero, 'spells_used'):
            hero.spells_used = list(self.current_state.spells_used)
        
        self.hero = hero
    
    def record_victory(self, path_taken: str) -> None:
        if self.current_state:
            class_id = self.current_state.class_id
            if class_id in self.stats["victories"]:
                if path_taken and path_taken not in self.stats["victories"][class_id]:
                    self.stats["victories"][class_id].append(path_taken)
        self.stats["total_games"] += 1
        self._save_account()
    
    def record_defeat(self) -> None:
        self.stats["defeats"] += 1
        self.stats["total_games"] += 1
        self._save_account()
    
    def show_stats(self) -> None:
        print("\n" + "═" * 50)
        print(f"  📊 СТАТИСТИКА: {self.account_name}")
        print("═" * 50)
        
        class_names = {
            "иван": "🤪 Иван-дурак",
            "василиса": "✨ Василиса Премудрая",
            "слуга": "🗡️ Кощеев слуга"
        }
        
        path_names = {
            "вода": "💧 Путь воды",
            "дым": "🏚️ Путь дыма",
            "тьма": "🌲 Путь тьмы",
            "тайный": "🕳️ Тайный путь"
        }
        
        total_victories = 0
        print("\n  🏆 ПОБЕДЫ:")
        
        for class_id, class_name in class_names.items():
            paths = self.stats["victories"].get(class_id, [])
            if paths:
                total_victories += len(paths)
                print(f"\n  {class_name}:")
                for path in paths:
                    print(f"    ✅ {path_names.get(path, path)}")
            else:
                print(f"\n  {class_name}: ещё не пройден")
        
        print(f"\n  📈 ОБЩЕЕ:")
        print(f"    🎮 Всего игр: {self.stats['total_games']}")
        print(f"    🏆 Побед: {total_victories}")
        print(f"    💀 Поражений: {self.stats['defeats']}")
        print("═" * 50)
    
    def show_menu(self) -> str:
        """Показать меню. Возвращает действие."""
        
        print("\n" + "═" * 50)
        print("  📋 МЕНЮ")
        print("═" * 50)
        
        options: List[str] = []
        actions: List[str] = []
        
        options.append("▶️ Продолжить игру")
        actions.append("continue")
        
        if self.can_save():
            options.append("💾 Сохранить игру")
            actions.append("save")
        else:
            options.append("💾 Сохранить (нет изменений)")
            actions.append("save_disabled")
        
        if self.can_load():
            options.append("📂 Загрузить сохранение")
            actions.append("load")
        else:
            options.append("📂 Загрузить (нет сохранения)")
            actions.append("load_disabled")
        
        options.append("👤 Статус персонажа")
        actions.append("status")
        
        options.append("🎒 Инвентарь и артефакты")
        actions.append("inventory")
        
        options.append("📊 Статистика")
        actions.append("stats")
        
        options.append("🚪 Выйти в главное меню")
        actions.append("quit")
        
        for i, opt in enumerate(options, 1):
            print(f"  {i}. {opt}")
        
        print("═" * 50)
        
        while True:
            try:
                choice = int(input("\n  Выберите: "))
                if 1 <= choice <= len(options):
                    action = actions[choice - 1]
                    
                    if action == "save_disabled":
                        print("  ⚠️ Нечего сохранять - изменений нет.")
                        continue
                    elif action == "load_disabled":
                        print("  ⚠️ Нет сохранённой игры.")
                        continue
                    
                    return action
                print("  ⚠️ Неверный выбор.")
            except ValueError:
                print("  ⚠️ Введите число!")
    
    def process_menu_action(self, action: str) -> bool:
        """Обработать действие. Возвращает True если продолжить игру."""
        
        if action == "continue":
            # Возвращаемся в игру - приглашение повторится в get_input_with_menu
            return True
        
        elif action == "save":
            if self.save_game():
                print("\n  ✅ Игра сохранена!")
            else:
                print("\n  ❌ Ошибка сохранения!")
            input("\n  [Enter — продолжить]")
            return True
        
        elif action == "load":
            if self.load_game():
                print("\n  ✅ Игра загружена!")
                if self.hero:
                    self.sync_to_hero(self.hero)
                return True  # Сигнал о необходимости перезапуска локации
            else:
                print("\n  ❌ Ошибка загрузки!")
            input("\n  [Enter — продолжить]")
            return True
        
        elif action == "status":
            if self.hero:
                print(self.hero.get_full_status())
            input("\n  [Enter — продолжить]")
            return True
        
        elif action == "inventory":
            if self.hero:
                print(self.hero.show_inventory())
                
                from battle import use_item_outside_combat
                usable = [i for i in self.hero.inventory if i.can_use(self.hero) and i.damage == 0]
                if usable:
                    print("\n  Использовать предмет? (y/n)")
                    if input("  ").lower() == 'y':
                        if use_item_outside_combat(self.hero):
                            self.sync_from_hero(self.hero)
            input("\n  [Enter — продолжить]")
            return True
        
        elif action == "stats":
            self.show_stats()
            input("\n  [Enter — продолжить]")
            return True
        
        elif action == "quit":
            if self.can_save():
                print("\n  ⚠️ Есть несохранённые изменения!")
                print("  1. Сохранить и выйти")
                print("  2. Выйти без сохранения")
                print("  3. Отмена")
                
                try:
                    choice = int(input("\n  Выберите: "))
                    if choice == 1:
                        self.save_game()
                        print("  ✅ Сохранено!")
                        return False
                    elif choice == 2:
                        return False
                    else:
                        return True
                except ValueError:
                    return True
            return False
        
        return True
    
    def call_menu(self) -> bool:
        """Вызвать меню. Возвращает True если продолжить."""
        action = self.show_menu()
        return self.process_menu_action(action)
    
    def game_over_menu(self, victory: bool, path_taken: str = "") -> str:
        """Меню после победы/поражения. Позволяет загрузить сохранение."""
        
        if victory:
            self.record_victory(path_taken)
            print("\n" + "🏆" * 25)
            print("\n  🎉 ПОЗДРАВЛЯЕМ С ПОБЕДОЙ!")
            print("\n" + "🏆" * 25)
        else:
            # Не записываем поражение сразу - даём шанс загрузить
            print("\n" + "💀" * 25)
            print("\n  😢 ИГРА ОКОНЧЕНА")
            print("\n" + "💀" * 25)
        
        options: List[str] = ["🔄 Новая игра"]
        actions: List[str] = ["new_game"]
        
        # Позволяем загрузить сохранение при поражении
        if not victory and self.can_load():
            options.append("📂 Загрузить сохранение")
            actions.append("load")
        
        options.append("📊 Статистика")
        actions.append("stats")
        
        options.append("🚪 Главное меню")
        actions.append("main_menu")
        
        options.append("❌ Выход")
        actions.append("quit")
        
        while True:
            print()
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            
            try:
                choice = int(input("\n  Выберите: "))
                if choice < 1 or choice > len(options):
                    continue
                    
                action = actions[choice - 1]
                
                if action == "stats":
                    self.show_stats()
                    continue
                elif action == "load":
                    if self.load_game():
                        print("\n  ✅ Игра загружена!")
                        if self.hero:
                            self.sync_to_hero(self.hero)
                        return "continue"  # Продолжить с сохранения
                    else:
                        print("\n  ❌ Ошибка загрузки!")
                        continue
                else:
                    if not victory and action in ("new_game", "main_menu", "quit"):
                        self.record_defeat()
                    return action
                    
            except ValueError:
                print("  ⚠️ Введите число!")


# Глобальный менеджер
game_manager = GameManager()


def get_input_with_menu(prompt: str, valid_range: range, 
                       options_text: str = "", 
                       options_list: Optional[List[str]] = None,
                       game_mgr: Optional['GameManager'] = None) -> int:
    """Ввод с возможностью меню (0). Сохраняет и повторяет приглашение после меню."""
    if game_mgr is None:
        game_mgr = game_manager
    
    mgr: GameManager = game_mgr  # Теперь точно не None
    
    # Сохраняем информацию о приглашении
    set_last_prompt(options_text, options_list or [], valid_range, prompt)
    
    # Показываем подсказку о меню
    print(f"\n  (0 — меню)")
    
    while True:
        try:
            value = int(input(prompt))
            
            if value == 0:
                if mgr.hero:
                    mgr.sync_from_hero(mgr.hero)
                
                if not mgr.call_menu():
                    raise SystemExit("menu_exit")
                
                # После выхода из меню - повторяем ВСЁ приглашение
                print("\n" + "─" * 50)
                print("  ↩️ Возврат к выбору:")
                show_last_prompt()
                print(f"\n  (0 — меню)")
                continue
            
            if value in valid_range:
                return value
            print(f"  ⚠️ Введите {valid_range.start}-{valid_range.stop - 1}")
        except ValueError:
            print("  ⚠️ Введите число!")
