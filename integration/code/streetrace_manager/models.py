"""Core domain models for StreetRace Manager."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CrewMember:
    """Represents a registered crew member and their capabilities."""

    name: str
    role: str = ""
    skills: Dict[str, int] = field(default_factory=dict)


@dataclass
class Car:
    """Represents a car managed by inventory."""

    car_id: str
    model: str
    damaged: bool = False
    condition: int = 100


@dataclass
class Race:
    """Represents a race and participants."""

    race_id: str
    name: str
    participants: List[str] = field(default_factory=list)
    car_assignments: Dict[str, str] = field(default_factory=dict)
    completed: bool = False


@dataclass
class Mission:
    """Represents a mission and role requirements."""

    mission_id: str
    mission_type: str
    required_roles: List[str]
    started: bool = False
    completed: bool = False
