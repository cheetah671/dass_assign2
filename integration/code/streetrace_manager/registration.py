"""Registration module for StreetRace Manager."""

from .models import CrewMember


class RegistrationModule:
    """Handles onboarding and lookup of crew members."""

    def __init__(self):
        self._members = {}

    def register_member(self, name, role=""):
        """Register a new crew member with an optional initial role."""
        if name in self._members:
            raise ValueError(f"Crew member '{name}' is already registered.")
        self._members[name] = CrewMember(name=name, role=role)
        return self._members[name]

    def is_registered(self, name):
        """Return True if the member exists in the registry."""
        return name in self._members

    def get_member(self, name):
        """Return the crew member by name or None if absent."""
        return self._members.get(name)

    def all_members(self):
        """Return all crew members."""
        return list(self._members.values())
