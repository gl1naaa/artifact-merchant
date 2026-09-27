"""First playable trading slice: artifacts, market, inventory and money."""
from __future__ import annotations

from dataclasses import dataclass, field
import random


@dataclass
class Artifact:
    id: str
    name: str
    category: str
    rarity: str
    weight: float
    base_value: int
    buy_price: int
    sell_price: int
    identified: bool = False
    authentic: bool = True
    hidden_property: str = "Неизвестное свойство"
    revealed_property: bool = False
    curse: str | None = None
    curse_revealed: bool = False
    contained: bool = False


@dataclass
class GameState:
    day: int = 1
    gold: int = 250_000
    reputation: int = 0
    inventory: list[Artifact] = field(default_factory=list)
    market: list[Artifact] = field(default_factory=list)
    journal: list[str] = field(default_factory=list)
    rng_seed: int = 42

    @classmethod
    def new(cls, seed: int = 42) -> "GameState":
        rng = random.Random(seed)
        stock = [
            ("void_shard", "Осколок Пустоты", "реликвия", "легендарный", .5, 575_000),
            ("ancient_compass", "Древний Компас", "реликвия", "редкий", 1.2, 132_000),
            ("observer_claw", "Коготь Наблюдателя", "амулет", "необычный", .8, 71_000),
            ("ash_heart", "Сердце Пепла", "реликвия", "редкий", 1.5, 160_000),
            ("whispering_idol", "Шепчущий Идол", "реликвия", "эпический", .7, 340_000),
            ("quantum_stabilizer", "Квантовый Стабилизатор", "механизм", "обычный", 2.1, 45_000),
        ]
        market = []
        for item_id, name, category, rarity, weight, sell_price in stock:
            buy_price = int(sell_price * rng.uniform(.70, .82))
            hidden = {
                "void_shard": "Искажает локальное пространство",
                "ancient_compass": "Указывает на ближайший разлом",
                "observer_claw": "Реагирует на сознание наблюдателя",
                "ash_heart": "Сохраняет тепло погибшей звезды",
                "whispering_idol": "Шепчет имена будущих покупателей",
                "quantum_stabilizer": "Стабилизирует нестабильные артефакты",
            }[item_id]
            curses = {"void_shard": "Нестабильность Пустоты", "whispering_idol": "Шёпот мёртвого владельца"}
            counterfeits = {"observer_claw"}
            market.append(Artifact(item_id, name, category, rarity, weight, sell_price, buy_price, sell_price,
                                   authentic=item_id not in counterfeits, hidden_property=hidden,
                                   curse=curses.get(item_id)))
        state = cls(market=market, rng_seed=seed)
        state.journal.append("Лавка открыта. Новый день начинается.")
        return state

    def find_market(self, item_id: str) -> Artifact | None:
        return next((item for item in self.market if item.id == item_id), None)

    def find_inventory(self, item_id: str) -> Artifact | None:
        return next((item for item in self.inventory if item.id == item_id), None)

    def buy(self, item_id: str) -> tuple[bool, str]:
        item = self.find_market(item_id)
        if item is None:
            return False, f"Артефакт не найден на рынке: {item_id}"
        if len(self.inventory) >= 20:
            return False, "Инвентарь заполнен (20/20)."
        if self.gold < item.buy_price:
            return False, f"Недостаточно кредитов: нужно {item.buy_price:,} кр."
        self.gold -= item.buy_price
        self.market.remove(item)
        self.inventory.append(item)
        self.journal.append(f"Покупка: {item.name} за {item.buy_price:,} кр.")
        return True, f"Куплено: {item.name} за {item.buy_price:,} кр."

    def sell(self, item_id: str) -> tuple[bool, str]:
        item = self.find_inventory(item_id)
        if item is None:
            return False, f"Артефакт отсутствует в инвентаре: {item_id}"
        self.inventory.remove(item)
        self.gold += item.sell_price
        self.reputation += 1
        self.journal.append(f"Продажа: {item.name} за {item.sell_price:,} кр.")
        return True, f"Продано: {item.name} за {item.sell_price:,} кр."

    def inspect(self, item_id: str) -> tuple[bool, list[str]]:
        item = self.find_inventory(item_id) or self.find_market(item_id)
        if item is None:
            return False, [f"Артефакт не найден: {item_id}"]
        rows = [f"{item.name} [{item.rarity}]", f"Категория: {item.category}", f"Вес: {item.weight:.1f} кг", f"Оценка: {item.sell_price:,} кр."]
        rows.append("Подлинность: не проверена" if not item.identified else ("Подлинность: подтверждена" if item.authentic else "Подлинность: сомнительна"))
        rows.append(f"Свойство: {item.hidden_property}" if item.revealed_property else "Свойство: неизвестно (нужна research)")
        if item.curse_revealed:
            rows.append(f"Проклятие: {item.curse or 'нет'}" + (" [изолировано]" if item.contained else " [активно]"))
        else:
            rows.append("Проклятие: неизвестно")
        return True, rows

    def research(self, item_id: str) -> tuple[bool, list[str]]:
        item = self.find_inventory(item_id)
        if item is None:
            return False, [f"Исследовать можно только предмет в инвентаре: {item_id}"]
        if item.revealed_property:
            return True, [f"Свойство уже раскрыто: {item.hidden_property}"]
        cost = 1_500
        if self.gold < cost:
            return False, [f"Недостаточно кредитов для исследования: нужно {cost:,} кр."]
        self.gold -= cost
        item.revealed_property = True
        item.curse_revealed = True
        item.identified = True
        self.journal.append(f"Исследование: раскрыты свойства {item.name} за {cost:,} кр.")
        authenticity = "подделка обнаружена" if not item.authentic else "подлинность подтверждена"
        curse = item.curse or "проклятий не обнаружено"
        return True, [f"Исследование завершено: {item.hidden_property}", f"{authenticity}; проклятие: {curse}", f"Стоимость: {cost:,} кр."]

    def contain(self, item_id: str) -> tuple[bool, str]:
        item = self.find_inventory(item_id)
        if item is None:
            return False, "Изолировать можно только предмет в инвентаре."
        if not item.curse_revealed or not item.curse:
            return False, "Проклятие не обнаружено. Сначала используйте research."
        item.contained = True
        self.journal.append(f"Изоляция: {item.name} помещён в защитный контейнер.")
        return True, f"{item.name} изолирован. Проклятие подавлено."

    def cleanse(self, item_id: str) -> tuple[bool, str]:
        item = self.find_inventory(item_id)
        if item is None or not item.curse:
            return False, "Проклятый предмет не найден в инвентаре."
        if not item.curse_revealed:
            return False, "Сначала раскройте проклятие через research."
        cost = 3_000
        if self.gold < cost:
            return False, f"Недостаточно кредитов: нужно {cost:,} кр."
        self.gold -= cost
        item.curse = None
        item.contained = False
        self.journal.append(f"Очищение: проклятие снято с {item.name} за {cost:,} кр.")
        return True, f"Проклятие снято с {item.name}."

    def status(self) -> str:
        return f"День {self.day} · {self.gold:,} кр. · репутация {self.reputation:+d} · инвентарь {len(self.inventory)}/20"
