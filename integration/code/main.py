"""Command-line entrypoint for StreetRace Manager."""

from streetrace_manager import StreetRaceManager


def run_cli():
    """Run interactive command-line interface for StreetRace Manager."""
    app = StreetRaceManager(initial_cash=1000)
    print("StreetRace Manager CLI")
    print("Type 'help' for commands, 'quit' to exit.")

    while True:
        raw = input("> ").strip()
        if not raw:
            continue
        if raw == "quit":
            print("Exiting StreetRace Manager.")
            break
        if raw == "help":
            print(
                "register <name> [role] | assign-role <name> <role> | "
                "set-skill <name> <skill> <level> | add-car <car_id> <model> | "
                "create-race <id> <name> | enter-race <id> <driver> <car_id> | "
                "record-result <id> <winner> <prize> | "
                "create-mission <id> <type> <roles_csv> | start-mission <id> | "
                "repair-car <car_id> | show-rankings | show-cash"
            )
            continue

        parts = raw.split()
        cmd = parts[0]

        try:
            if cmd == "register":
                name = parts[1]
                role = parts[2] if len(parts) > 2 else ""
                app.registration.register_member(name, role)
                print(f"Registered {name}.")
            elif cmd == "assign-role":
                app.crew.assign_role(parts[1], parts[2])
                print("Role assigned.")
            elif cmd == "set-skill":
                app.crew.set_skill_level(parts[1], parts[2], int(parts[3]))
                print("Skill updated.")
            elif cmd == "add-car":
                app.inventory.add_car(parts[1], parts[2])
                print("Car added.")
            elif cmd == "create-race":
                app.race.create_race(parts[1], parts[2])
                print("Race created.")
            elif cmd == "enter-race":
                app.race.enter_race(parts[1], parts[2], parts[3])
                print("Race entry accepted.")
            elif cmd == "record-result":
                race_id = parts[1]
                winner = parts[2]
                prize = int(parts[3])
                app.results.record_race_result(race_id, [winner], prize_money=prize)
                print("Result recorded.")
            elif cmd == "create-mission":
                roles = parts[3].split(",") if len(parts) > 3 else []
                app.missions.create_mission(parts[1], parts[2], roles)
                print("Mission created.")
            elif cmd == "start-mission":
                ok = app.missions.start_mission(parts[1])
                print("Mission started." if ok else "Mission cannot start.")
            elif cmd == "repair-car":
                ok = app.garage.repair_car(parts[1])
                print("Car repaired." if ok else "Car cannot be repaired now.")
            elif cmd == "show-rankings":
                print(app.results.rankings)
            elif cmd == "show-cash":
                print(app.inventory.cash_balance)
            else:
                print("Unknown command. Type 'help'.")
        except (IndexError, ValueError) as exc:
            print(f"Error: {exc}")


if __name__ == "__main__":
    run_cli()
