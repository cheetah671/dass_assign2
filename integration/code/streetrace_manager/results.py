"""Results module for StreetRace Manager."""


class ResultsModule:
    """Records outcomes, ranking points, and prize money."""

    POINTS_BY_POSITION = {0: 10, 1: 6, 2: 4}

    def __init__(self, race_module, inventory_module, reputation_module=None):
        self.races = race_module
        self.inventory = inventory_module
        self.reputation = reputation_module
        self.rankings = {}

    def record_race_result(self, race_id, final_order, prize_money=0, damaged_cars=None):
        """Record race results and apply cross-module updates."""
        race = self.races.get_race(race_id)
        if race is None:
            raise ValueError("Race not found.")
        if race.completed:
            raise ValueError("Race already completed.")
        if not final_order:
            raise ValueError("Result order cannot be empty.")

        for driver_name in final_order:
            if driver_name not in race.participants:
                raise ValueError("Result includes a driver not entered in race.")

        for index, driver_name in enumerate(final_order):
            points = self.POINTS_BY_POSITION.get(index, 1)
            self.rankings[driver_name] = self.rankings.get(driver_name, 0) + points
            if self.reputation is not None:
                self.reputation.add_reputation(driver_name, points)

        if prize_money > 0:
            self.inventory.add_cash(prize_money)

        for car_id in damaged_cars or []:
            self.inventory.mark_car_damaged(car_id)

        race.completed = True
        return {"race_id": race_id, "winner": final_order[0], "prize_money": prize_money}
