"""
Represents a general room in the game
"""

from models.assignment.RoleData import *
from models.assignment.RoleAssignment import RoleAssignment
from collections import Counter, defaultdict

# GLOBALS TO REMOVE
# names
# Add back in  self._config['prank_everyone_is']


class Room:
    def __init__(self, creator_uid, room_code):
        assert(creator_uid)
        assert(room_code)

        # Immutable
        self._room_code = room_code
        self._creator_uid = None

        # Mutable
        self._players_in_room = list()  # To keep it ordered -_-
        self._current_assignments = None
        self._config = None

        self.add_player(self._creator_uid)

    def get_creator_uid(self):
        return self._creator_uid

    def is_configuring(self):
        if self._current_assignments:
            return

        return not self._config

    def rematch(self):
        self._current_assignments = None
        self._config = None

    def get_max_player_count(self):
        if not self._config:
            return -1

        return self._config["num_players"]

    def get_player_count(self):
        return len(self._players_in_room)

    def get_room_code(self):
        return self._room_code

    def get_configure(self):
        return self._config

    def set_configure(self, config):
        assert(config)
        self._config = config
        self._possibly_do_assignments()

    def _possibly_do_assignments(self):
        if self._current_assignments:
            return
        if not self._config:
            return
        if len(self._players_in_room) != len(self._config['roles']):
            return

        self._current_assignments = RoleAssignment(
            list(self._players_in_room),
            self._config.roles)

    def get_player_names(self, get_user_name_from_uid):
        return [get_user_name_from_uid(uid) for uid in self._players_in_room]

    def has_player(self, uid):
        return uid in self._players_in_room

    def add_player(self, uid):
        if self._current_assignments:
            return False

        if self.has_player(uid):
            return True

        # Attempt to set creator
        if (self._creator_uid is None) or (self._creator_uid not in self._players_in_room):
            self._creator_uid = uid

        # TODO: Update logic
        self._players_in_room.append(uid)
        self._possibly_do_assignments()

        return True

    def remove_player(self, uid):
        if self.has_player(uid):
            self._players_in_room.remove(uid)

            # Try to get a creator
            if self._creator_uid == uid:
                if self._players_in_room:
                    self._creator_uid = self._players_in_room[0]
                else:
                    self._creator_uid = None

    def get_roles_data_for_rendering(self):
        if self._config:
            return self.render_roles(self._config["roles"])
        elif self._current_assignments:
            return self.render_roles(self._current_assignments.get_roles())
        else:
            return []

    def render_roles(self, role_list):
        role_counts = Counter(role_list)
        roles = [{
            'name': DISPLAY_OVERRIDE.get(name, name),
            'count': count,
            'css_class': get_role_css_class(name),
        } for name, count in role_counts.items()]
        return roles

    def get_role_info(self, uid, get_user_name_from_uid):
        assert(uid)
        assert(get_user_name_from_uid)

        if not self._current_assignments:
            return {
                'messages': [],
                'has_role': False,
            }

        return self._current_assignments.get_role_info(uid, get_user_name_from_uid)
