# 2. StreetRace Manager Integration Report

## 2.1 System Design and Implementation

### Overview
StreetRace Manager is implemented as a command-line Python system in:
- `integration/code/main.py` (CLI entrypoint)
- `integration/code/streetrace_manager/` (module implementations)

The system is built module-by-module and then validated with integration tests in:
- `integration/tests/test_streetrace_integration.py`

### Required Modules Implemented

1. Registration module (`registration.py`)
- Registers crew members.
- Stores member name and optional role.
- Prevents duplicate registrations.

2. Crew Management module (`crew_management.py`)
- Assigns valid roles (`driver`, `mechanic`, `strategist`, `scout`, `medic`).
- Enforces rule: role assignment only for registered members.
- Stores and updates skill levels per member.

3. Inventory module (`inventory.py`)
- Tracks cars, spare parts, tools, and cash balance.
- Adds cars and marks cars as damaged.
- Adds/deducts cash with validations.

4. Race Management module (`race_management.py`)
- Creates races.
- Enters driver + car pairs into races.
- Enforces rule: only `driver` role can enter race.
- Enforces rule: damaged cars cannot be entered.

5. Results module (`results.py`)
- Records race outcomes.
- Updates rankings points.
- Updates inventory cash with prize money.
- Marks selected cars as damaged after race.

6. Mission Planning module (`mission_planning.py`)
- Creates missions with required roles.
- Validates role availability before mission start.
- Enforces rule: repair missions require damaged car + mechanic availability.
- Completes missions and applies reward to inventory cash.

### Additional Modules Implemented (Required: at least 2)

7. Garage module (`garage.py`) [Extra Module 1]
- Repairs damaged cars.
- Requires mechanic availability, spare parts, and tools.
- Integrates crew + inventory states.

8. Reputation module (`reputation.py`) [Extra Module 2]
- Tracks reputation points per crew member.
- Updated automatically from race results.
- Provides leaderboard data.

### Module Interaction Rules Enforced
- Crew member must be registered before role assignment.
- Only crew members with `driver` role can enter races.
- Damaged cars cannot be entered in races.
- Race results update inventory cash balance.
- Missions cannot start if required roles are unavailable.
- Repair-after-race missions require mechanic + damaged car.

## 2.2 Integration Test Design

### Test Execution Command
```bash
cd integration
/home/arnav-agnihotri/miniconda3/envs/autograder/bin/python -m pytest tests -q
```

### Final Test Result
- Total integration tests: 20
- Passed: 20
- Failed: 0

### Integration Test Cases

1. Scenario:
Register a driver and enter that driver into a race.
- Modules involved: Registration, Crew Management, Race Management, Inventory
- Why needed: Confirms registration-to-race data flow works correctly.
- Expected result: Entry accepted and driver-car mapping stored.
- Actual result: Pass.
- Errors/issues found: None.

2. Scenario:
Try assigning role to an unregistered member.
- Modules involved: Registration, Crew Management
- Why needed: Validates prerequisite business rule.
- Expected result: Role assignment rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

3. Scenario:
Attempt race entry by a non-driver crew member.
- Modules involved: Crew Management, Race Management
- Why needed: Ensures role-based access control in race flow.
- Expected result: Race entry rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

4. Scenario:
Complete race and verify ranking + cash + reputation update.
- Modules involved: Race Management, Results, Inventory, Reputation
- Why needed: Core post-race integration check.
- Expected result: Rankings and reputation increase, cash balance increases by prize.
- Actual result: Pass.
- Errors/issues found: None.

5. Scenario:
Mark car damaged via race result, then block future race until repaired.
- Modules involved: Results, Inventory, Race Management, Garage, Crew Management
- Why needed: Validates cross-module safety and repair dependency.
- Expected result: Damaged car rejected for race, accepted after repair.
- Actual result: Pass.
- Errors/issues found: None.

6. Scenario:
Mission start attempt without required strategist role.
- Modules involved: Mission Planning, Crew Management
- Why needed: Confirms mission precondition checks.
- Expected result: Mission start denied.
- Actual result: Pass (`False` returned).
- Errors/issues found: None.

7. Scenario:
Repair mission requires mechanic and damaged car.
- Modules involved: Mission Planning, Crew Management, Inventory
- Why needed: Verifies stated repair business rule.
- Expected result: Start denied before conditions, allowed after conditions are satisfied.
- Actual result: Pass.
- Errors/issues found: None.

8. Scenario:
Mission completion updates inventory cash.
- Modules involved: Mission Planning, Inventory
- Why needed: Checks mission-to-finance integration path.
- Expected result: Cash balance increases by reward amount.
- Actual result: Pass.
- Errors/issues found: None.

9. Scenario:
Record race result for non-participant driver.
- Modules involved: Race Management, Results
- Why needed: Protects result integrity and ranking correctness.
- Expected result: Result recording rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

10. Scenario:
Duplicate crew registration attempt.
- Modules involved: Registration
- Why needed: Ensures member identity uniqueness.
- Expected result: Duplicate registration rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

11. Scenario:
Invalid role assignment for a registered crew member.
- Modules involved: Crew Management
- Why needed: Prevents unsupported role values from leaking into downstream modules.
- Expected result: Invalid role rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

12. Scenario:
Skill update validation for registration and allowed level range.
- Modules involved: Registration, Crew Management
- Why needed: Protects mission/race logic from invalid skill data.
- Expected result: Unregistered member fails; valid member updates; out-of-range level rejected.
- Actual result: Pass.
- Errors/issues found: None.

13. Scenario:
Duplicate race ID creation.
- Modules involved: Race Management
- Why needed: Prevents race state overwrite and ambiguous result tracking.
- Expected result: Duplicate race rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

14. Scenario:
Race entry failure when race does not exist and when selected car is damaged.
- Modules involved: Race Management, Crew Management, Inventory
- Why needed: Ensures race entry validations are strict before mutating participants.
- Expected result: Both invalid entries rejected.
- Actual result: Pass (ValueError raised in both checks).
- Errors/issues found: None.

15. Scenario:
Result recording validation for empty outcome and repeated completion.
- Modules involved: Race Management, Results
- Why needed: Preserves correctness of result lifecycle.
- Expected result: Empty outcome rejected; second recording on completed race rejected.
- Actual result: Pass.
- Errors/issues found: None.

16. Scenario:
Result recording for missing race and zero-prize result path.
- Modules involved: Results, Inventory
- Why needed: Ensures not-found behavior and no accidental cash changes on zero prize.
- Expected result: Missing race rejected; zero-prize leaves cash unchanged.
- Actual result: Pass.
- Errors/issues found: None.

17. Scenario:
Mission lookup failure and completion-before-start check.
- Modules involved: Mission Planning
- Why needed: Validates mission lifecycle constraints.
- Expected result: Missing mission rejected; completion before start rejected.
- Actual result: Pass (ValueError raised).
- Errors/issues found: None.

18. Scenario:
Garage repair prerequisites: mechanic, parts, tools, and valid car ID.
- Modules involved: Garage, Crew Management, Inventory
- Why needed: Confirms all repair dependencies are enforced before car state changes.
- Expected result: Repair denied until requirements are satisfied; unknown car rejected.
- Actual result: Pass.
- Errors/issues found: None.

19. Scenario:
Successful garage repair updates stock and car state.
- Modules involved: Garage, Inventory
- Why needed: Verifies successful repair mutates all linked resources correctly.
- Expected result: Spare parts decremented and car damage cleared.
- Actual result: Pass.
- Errors/issues found: None.

20. Scenario:
Reputation validation and leaderboard ordering after race points.
- Modules involved: Reputation, Results, Race Management
- Why needed: Confirms secondary ranking system is correctly fed by race outcomes.
- Expected result: Negative points rejected and leaderboard sorted by points.
- Actual result: Pass.
- Errors/issues found: None.

## 2.3 Call Flow Summary (Simple)
- Registration -> Crew Management: member must exist first.
- Crew Management + Inventory -> Race Management: valid driver role and undamaged car required.
- Race Management -> Results: only entered participants can appear in result order.
- Results -> Inventory: prize money added to cash.
- Results -> Inventory/Garage/Mission Planning: damage creates dependency on mechanic availability and repair flow.
- Mission Planning -> Inventory: mission rewards modify cash.

## 2.4 Conclusion
The integrated StreetRace Manager system satisfies all required module behaviors and interaction rules listed in the assignment. The integration test suite confirms module-to-module data flow and rule enforcement with 20/20 passing tests.
