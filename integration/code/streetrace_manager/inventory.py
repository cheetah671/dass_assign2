"""Inventory module for StreetRace Manager."""

from .models import Car


class InventoryModule:
    """Tracks cars, parts, tools, and cash balance."""

    def __init__(self, initial_cash=0):
        self.cash_balance = initial_cash
        self.cars = {}
        self.spare_parts = 0
        self.tools = 0

    def add_car(self, car_id, model, condition=100):
        """Add a new car to inventory."""
        if car_id in self.cars:
            raise ValueError(f"Car '{car_id}' already exists.")
        self.cars[car_id] = Car(car_id=car_id, model=model, condition=condition)
        return self.cars[car_id]

    def get_car(self, car_id):
        """Return car object by id or None."""
        return self.cars.get(car_id)

    def add_spare_parts(self, amount):
        """Increase spare parts stock."""
        if amount < 0:
            raise ValueError("Cannot add negative spare parts.")
        self.spare_parts += amount

    def add_tools(self, amount):
        """Increase tool stock."""
        if amount < 0:
            raise ValueError("Cannot add negative tools.")
        self.tools += amount

    def add_cash(self, amount):
        """Increase cash balance."""
        if amount < 0:
            raise ValueError("Cannot add negative cash.")
        self.cash_balance += amount

    def deduct_cash(self, amount):
        """Deduct cash if enough balance exists."""
        if amount < 0:
            raise ValueError("Cannot deduct negative cash.")
        if amount > self.cash_balance:
            raise ValueError("Insufficient cash balance.")
        self.cash_balance -= amount

    def mark_car_damaged(self, car_id, severity=30):
        """Mark a car as damaged and reduce condition."""
        car = self.get_car(car_id)
        if car is None:
            raise ValueError("Car not found.")
        car.damaged = True
        car.condition = max(0, car.condition - severity)
        return car
