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
            market.append(Artifact(item_id, name, category, rarity, weight, sell_price, buy_price, sell_price))
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

    def status(self) -> str:
        return f"День {self.day} · {self.gold:,} кр. · репутация {self.reputation:+d} · инвентарь {len(self.inventory)}/20"
