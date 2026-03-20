"""Composition root for StreetRace Manager modules."""

from .registration import RegistrationModule
from .crew_management import CrewManagementModule
from .inventory import InventoryModule
from .race_management import RaceManagementModule
from .results import ResultsModule
from .mission_planning import MissionPlanningModule
from .garage import GarageModule
from .reputation import ReputationModule


class StreetRaceManager:
    """Wires all modules and exposes a single system object."""

    def __init__(self, initial_cash=0):
        self.registration = RegistrationModule()
        self.crew = CrewManagementModule(self.registration)
        self.inventory = InventoryModule(initial_cash=initial_cash)
        self.race = RaceManagementModule(self.crew, self.inventory)
        self.reputation = ReputationModule()
        self.results = ResultsModule(self.race, self.inventory, self.reputation)
        self.missions = MissionPlanningModule(self.crew, self.inventory)
        self.garage = GarageModule(self.crew, self.inventory)
