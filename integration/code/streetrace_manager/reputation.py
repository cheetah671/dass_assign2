"""Extra module: crew reputation and leaderboard tracking."""


class ReputationModule:
    """Tracks reputation points accumulated by crew members."""

    def __init__(self):
        self._points = {}

    def add_reputation(self, member_name, points):
        """Add non-negative reputation points to a member."""
        if points < 0:
            raise ValueError("Reputation points cannot be negative.")
        self._points[member_name] = self._points.get(member_name, 0) + points

    def get_points(self, member_name):
        """Get current reputation points for a member."""
        return self._points.get(member_name, 0)

    def leaderboard(self):
        """Return sorted leaderboard as (member, points) tuples."""
        return sorted(self._points.items(), key=lambda item: item[1], reverse=True)
