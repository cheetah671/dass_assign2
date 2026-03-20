"""Integration tests for StreetRace Manager module interactions."""

import pytest


def test_register_driver_then_enter_race_success(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.race.create_race("R-1", "Dock Sprint")

    race = app.race.enter_race("R-1", "Alex", "CAR-1")

    assert race.participants == ["Alex"]
    assert race.car_assignments["Alex"] == "CAR-1"


def test_assign_role_requires_registration(app):
    with pytest.raises(ValueError, match="registered"):
        app.crew.assign_role("Unregistered", "driver")


def test_enter_race_without_driver_role_fails(app):
    app.registration.register_member("Sam")
    app.crew.assign_role("Sam", "mechanic")
    app.race.create_race("R-2", "Tunnel Rush")

    with pytest.raises(ValueError, match="driver role"):
        app.race.enter_race("R-2", "Sam", "CAR-1")


def test_record_race_result_updates_rankings_cash_and_reputation(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.race.create_race("R-3", "Midnight Run")
    app.race.enter_race("R-3", "Alex", "CAR-1")

    before_cash = app.inventory.cash_balance
    summary = app.results.record_race_result("R-3", ["Alex"], prize_money=1200)

    assert summary["winner"] == "Alex"
    assert app.results.rankings["Alex"] == 10
    assert app.reputation.get_points("Alex") == 10
    assert app.inventory.cash_balance == before_cash + 1200


def test_record_result_with_car_damage_blocks_next_race_until_repaired(app):
    app.registration.register_member("Alex")
    app.registration.register_member("Mia")
    app.crew.assign_role("Alex", "driver")
    app.crew.assign_role("Mia", "mechanic")

    app.race.create_race("R-4", "Harbor Circuit")
    app.race.enter_race("R-4", "Alex", "CAR-1")
    app.results.record_race_result("R-4", ["Alex"], prize_money=500, damaged_cars=["CAR-1"])

    app.race.create_race("R-5", "Airport Dash")
    with pytest.raises(ValueError, match="Damaged cars"):
        app.race.enter_race("R-5", "Alex", "CAR-1")

    assert app.garage.repair_car("CAR-1") is True
    app.race.enter_race("R-5", "Alex", "CAR-1")


def test_mission_cannot_start_when_required_roles_unavailable(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.missions.create_mission("M-1", "delivery", ["driver", "strategist"])

    assert app.missions.start_mission("M-1") is False


def test_repair_mission_requires_mechanic_and_damaged_car(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.missions.create_mission("M-2", "repair_after_race", ["mechanic"])

    assert app.missions.start_mission("M-2") is False

    app.registration.register_member("Mia")
    app.crew.assign_role("Mia", "mechanic")
    app.inventory.mark_car_damaged("CAR-2", severity=20)

    assert app.missions.start_mission("M-2") is True


def test_complete_mission_updates_inventory_cash(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.missions.create_mission("M-3", "delivery", ["driver"])

    started = app.missions.start_mission("M-3")
    assert started is True

    before_cash = app.inventory.cash_balance
    mission = app.missions.complete_mission("M-3", reward_money=350)

    assert mission.completed is True
    assert app.inventory.cash_balance == before_cash + 350


def test_results_reject_unregistered_race_participant_in_outcome(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.race.create_race("R-6", "Bridge Heat")
    app.race.enter_race("R-6", "Alex", "CAR-1")

    with pytest.raises(ValueError, match="not entered"):
        app.results.record_race_result("R-6", ["Ghost"], prize_money=100)


def test_duplicate_registration_is_rejected(app):
    app.registration.register_member("Alex")
    with pytest.raises(ValueError, match="already registered"):
        app.registration.register_member("Alex")


def test_invalid_role_assignment_is_rejected_for_registered_member(app):
    app.registration.register_member("Lee")
    with pytest.raises(ValueError, match="Invalid role"):
        app.crew.assign_role("Lee", "hacker")


def test_set_skill_level_validation_and_persistence(app):
    with pytest.raises(ValueError, match="registered"):
        app.crew.set_skill_level("Ghost", "cornering", 8)

    app.registration.register_member("Jin")
    app.crew.assign_role("Jin", "driver")
    member = app.crew.set_skill_level("Jin", "cornering", 9)

    assert member.skills["cornering"] == 9

    with pytest.raises(ValueError, match="between 1 and 10"):
        app.crew.set_skill_level("Jin", "reaction", 11)


def test_duplicate_race_id_is_rejected(app):
    app.race.create_race("R-7", "Neon Loop")
    with pytest.raises(ValueError, match="already exists"):
        app.race.create_race("R-7", "Neon Loop 2")


def test_enter_race_fails_for_missing_race_or_damaged_car(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")

    with pytest.raises(ValueError, match="Race not found"):
        app.race.enter_race("R-X", "Alex", "CAR-1")

    app.race.create_race("R-8", "Night Grid")
    app.inventory.mark_car_damaged("CAR-1", severity=10)
    with pytest.raises(ValueError, match="Damaged cars"):
        app.race.enter_race("R-8", "Alex", "CAR-1")


def test_record_result_rejects_empty_and_completed_race(app):
    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.race.create_race("R-9", "Canal Rush")
    app.race.enter_race("R-9", "Alex", "CAR-1")

    with pytest.raises(ValueError, match="cannot be empty"):
        app.results.record_race_result("R-9", [], prize_money=50)

    app.results.record_race_result("R-9", ["Alex"], prize_money=50)
    with pytest.raises(ValueError, match="already completed"):
        app.results.record_race_result("R-9", ["Alex"], prize_money=50)


def test_results_not_found_and_zero_prize_keeps_cash(app):
    with pytest.raises(ValueError, match="Race not found"):
        app.results.record_race_result("R-404", ["Alex"], prize_money=100)

    app.registration.register_member("Alex")
    app.crew.assign_role("Alex", "driver")
    app.race.create_race("R-10", "Hill Climb")
    app.race.enter_race("R-10", "Alex", "CAR-1")

    before = app.inventory.cash_balance
    app.results.record_race_result("R-10", ["Alex"], prize_money=0)
    assert app.inventory.cash_balance == before


def test_mission_not_found_and_complete_before_start_errors(app):
    with pytest.raises(ValueError, match="Mission not found"):
        app.missions.can_start_mission("M-404")

    app.registration.register_member("Ria")
    app.crew.assign_role("Ria", "driver")
    app.missions.create_mission("M-4", "delivery", ["driver"])

    with pytest.raises(ValueError, match="started"):
        app.missions.complete_mission("M-4", reward_money=100)


def test_garage_repair_checks_mechanic_parts_tools_and_missing_car(app):
    app.inventory.mark_car_damaged("CAR-1", severity=30)

    # No mechanic yet
    assert app.garage.repair_car("CAR-1") is False

    app.registration.register_member("Mia")
    app.crew.assign_role("Mia", "mechanic")

    app.inventory.spare_parts = 0
    assert app.garage.repair_car("CAR-1") is False

    app.inventory.spare_parts = 2
    app.inventory.tools = 0
    assert app.garage.repair_car("CAR-1") is False

    with pytest.raises(ValueError, match="Car not found"):
        app.garage.repair_car("CAR-404")


def test_garage_repair_success_consumes_parts_and_clears_damage(app):
    app.registration.register_member("Mia")
    app.crew.assign_role("Mia", "mechanic")
    app.inventory.mark_car_damaged("CAR-2", severity=60)

    before_parts = app.inventory.spare_parts
    repaired = app.garage.repair_car("CAR-2", parts_required=1)

    assert repaired is True
    assert app.inventory.spare_parts == before_parts - 1
    assert app.inventory.get_car("CAR-2").damaged is False


def test_reputation_negative_points_rejected_and_leaderboard_sorted(app):
    with pytest.raises(ValueError, match="cannot be negative"):
        app.reputation.add_reputation("Alex", -1)

    app.registration.register_member("Alex")
    app.registration.register_member("Kai")
    app.crew.assign_role("Alex", "driver")
    app.crew.assign_role("Kai", "driver")

    app.race.create_race("R-11", "Freeway Blitz")
    app.race.enter_race("R-11", "Alex", "CAR-1")
    app.race.enter_race("R-11", "Kai", "CAR-2")
    app.results.record_race_result("R-11", ["Alex", "Kai"], prize_money=300)

    board = app.reputation.leaderboard()
    assert board[0][0] == "Alex"
    assert board[0][1] > board[1][1]
