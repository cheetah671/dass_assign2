"""Race management module for StreetRace Manager."""

from .models import Race


class RaceManagementModule:
    """Creates races and manages race entries."""

    def __init__(self, crew_module, inventory_module):
        self.crew = crew_module
        self.inventory = inventory_module
        self._races = {}

    def create_race(self, race_id, name):
        """Create a race with a unique ID."""
        if race_id in self._races:
            raise ValueError(f"Race '{race_id}' already exists.")
        self._races[race_id] = Race(race_id=race_id, name=name)
        return self._races[race_id]

    def get_race(self, race_id):
        """Return race by id or None."""
        return self._races.get(race_id)

    def enter_race(self, race_id, driver_name, car_id):
        """Enter a driver-car pair into a race after validations."""
        race = self.get_race(race_id)
        if race is None:
            raise ValueError("Race not found.")
        if race.completed:
            raise ValueError("Cannot enter a completed race.")
        if not self.crew.has_role(driver_name, "driver"):
            raise ValueError("Only crew members with driver role may enter a race.")
        car = self.inventory.get_car(car_id)
        if car is None:
            raise ValueError("Car not found in inventory.")
        if car.damaged:
            raise ValueError("Damaged cars cannot enter races.")

        race.participants.append(driver_name)
        race.car_assignments[driver_name] = car_id
        return race
