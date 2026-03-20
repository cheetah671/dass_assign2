"""Mission planning module for StreetRace Manager."""

from .models import Mission


class MissionPlanningModule:
    """Creates missions and validates role availability before launch."""

    def __init__(self, crew_module, inventory_module):
        self.crew = crew_module
        self.inventory = inventory_module
        self._missions = {}

    def create_mission(self, mission_id, mission_type, required_roles):
        """Create a mission with required crew roles."""
        if mission_id in self._missions:
            raise ValueError(f"Mission '{mission_id}' already exists.")
        mission = Mission(
            mission_id=mission_id,
            mission_type=mission_type,
            required_roles=list(required_roles),
        )
        self._missions[mission_id] = mission
        return mission

    def get_mission(self, mission_id):
        """Return mission by id or None."""
        return self._missions.get(mission_id)

    def can_start_mission(self, mission_id):
        """Return True only if required roles and business rules are satisfied."""
        mission = self.get_mission(mission_id)
        if mission is None:
            raise ValueError("Mission not found.")

        for role in mission.required_roles:
            if not self.crew.members_with_role(role):
                return False

        if mission.mission_type == "repair_after_race":
            damaged_exists = any(car.damaged for car in self.inventory.cars.values())
            if not damaged_exists:
                return False
            if not self.crew.members_with_role("mechanic"):
                return False

        return True

    def start_mission(self, mission_id):
        """Start mission when validations pass."""
        mission = self.get_mission(mission_id)
        if mission is None:
            raise ValueError("Mission not found.")
        if not self.can_start_mission(mission_id):
            return False
        mission.started = True
        return True

    def complete_mission(self, mission_id, reward_money=0):
        """Complete mission and apply reward."""
        mission = self.get_mission(mission_id)
        if mission is None:
            raise ValueError("Mission not found.")
        if not mission.started:
            raise ValueError("Mission must be started before completion.")
        mission.completed = True
        if reward_money > 0:
            self.inventory.add_cash(reward_money)
        return mission
