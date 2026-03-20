"""Extra module: garage maintenance and repair operations."""


class GarageModule:
    """Repairs damaged cars by checking mechanic and inventory resources."""

    def __init__(self, crew_module, inventory_module):
        self.crew = crew_module
        self.inventory = inventory_module

    def repair_car(self, car_id, parts_required=1):
        """Repair a damaged car if mechanic and parts are available."""
        car = self.inventory.get_car(car_id)
        if car is None:
            raise ValueError("Car not found.")
        if not car.damaged:
            return False
        if not self.crew.members_with_role("mechanic"):
            return False
        if self.inventory.spare_parts < parts_required:
            return False
        if self.inventory.tools <= 0:
            return False

        self.inventory.spare_parts -= parts_required
        car.damaged = False
        car.condition = min(100, car.condition + 40)
        return True
