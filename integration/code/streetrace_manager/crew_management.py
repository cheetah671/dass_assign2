"""Crew management module for StreetRace Manager."""


class CrewManagementModule:
    """Assigns roles and skills to registered crew members."""

    VALID_ROLES = {"driver", "mechanic", "strategist", "scout", "medic"}

    def __init__(self, registration_module):
        self.registration = registration_module

    def assign_role(self, member_name, role):
        """Assign a role to a registered member."""
        if not self.registration.is_registered(member_name):
            raise ValueError("Member must be registered before assigning a role.")
        if role not in self.VALID_ROLES:
            raise ValueError(f"Invalid role '{role}'.")
        member = self.registration.get_member(member_name)
        member.role = role
        return member

    def set_skill_level(self, member_name, skill_name, level):
        """Set a skill level between 1 and 10 for a member."""
        if not self.registration.is_registered(member_name):
            raise ValueError("Member must be registered before setting skills.")
        if level < 1 or level > 10:
            raise ValueError("Skill level must be between 1 and 10.")
        member = self.registration.get_member(member_name)
        member.skills[skill_name] = level
        return member

    def members_with_role(self, role):
        """Return all members who currently have the requested role."""
        return [m for m in self.registration.all_members() if m.role == role]

    def has_role(self, member_name, role):
        """Return True if the named member has the given role."""
        member = self.registration.get_member(member_name)
        return member is not None and member.role == role
