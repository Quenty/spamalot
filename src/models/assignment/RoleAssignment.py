"""
Holds the assignment logic and data model
"""

from models.assignment.RoleData import *
from collections import Counter, defaultdict


def shuffled(enumerable):
    new_list = list(enumerable)
    shuffle(new_list)
    return new_list


class RoleAssignment:
    """
    Immutable object that holds mapping of player UIDs to roles
    :param uids: List of UIDs (strings)
    :param roles: List of roles (strings)
    """
    def __init__(self, uids, roles):
        assert(roles)
        assert(uids)
        assert(len(uids) == len(roles))

        self._uids = uids
        self._roles = roles

        self._assignments = dict()  # uid -> role
        self._role_lookup = defaultdict(lambda: set())

        for uid, r in zip(shuffled(self._uids), roles):
            self._assignments[uid] = r
            self._role_lookup[r].add(uid)

    def player_has_role(self, uid):
        return uid in self._assignments

    def get_roles(self):
        return list(self._assignments.values())

    def get_spectator_role_info(self, get_user_name_from_uid):
        assert(get_user_name_from_uid)

        info = {
            'messages': [],
            'has_role': True,
            'role_name': 'spectator',
        }

        for role in EVERY_ROLE:
            if role not in self._role_lookup:
                continue

            people = [get_user_name_from_uid(uid) for uid in self._role_lookup[role]]

            info['messages'].append({
                'people': people,
                'text': role,
                'people_css_class': get_role_css_class(role)
            })

        return info

    # def get_prank_targets(self, uid, valid_fakes, target):
    #     fake_people_num = len([role for role in target if
    #                            role is not uid and role in self._roles])
    #     shuffle(valid_fakes)
    #     people = valid_fakes[0:fake_people_num]
    #     return people

    def get_role_info(self, uid, get_user_name_from_uid):
        assert(uid)
        assert(get_user_name_from_uid)

        uid = self._assignments.get(uid, None)
        if uid is None:
            return self.get_spectator_role_info(get_user_name_from_uid)

        info = {
            'messages': self.get_role_info_messages(uid, get_user_name_from_uid),
            'has_role': True,
            'role_name': f'{uid}',
            'role_css_class': get_role_css_class(uid),
            'original_is_good': False,  # Hack for easy code in alignment sweet alert
            'original_alignment': 'Error',
        }

        if uid in GOOD_ALIGNED_ALL:
            info['original_alignment'] = 'good'
            info['original_is_good'] = True
        elif uid in EVIL_ALIGNED_ALL:
            info['original_alignment'] = 'evil'

        # valid_fakes = list(names.values())
        # valid_fakes.remove(names[uid])

        return info

    def get_role_info_messages(self, uid, get_user_name_from_uid):
        assert(get_user_name_from_uid)

        messages = []

        # Use vision matrix to add messages
        for group, target, description, people_css_class in VISION_MATRIX:
            if uid not in group:
                continue

            people = [get_user_name_from_uid(uid) for uid in
                      set.union(*[self._role_lookup.get(role, set())
                                  for role in target])
                      if uid not in (uid, None)]

            # if self._config.get('prank_everyone_is'):
            #     people = self.get_prank_targets(uid, valid_fakes, target)
            #     valid_fakes = list(
            #         fake for fake in valid_fakes if fake not in people)

            if people:
                messages.append({
                    'people': people,
                    'text': description,
                    'people_css_class': people_css_class,
                })

        # Add additional information for Merlin and mordred
        if uid is Role.merlin and Role.mordred in self._roles:
            info['messages'].append({
                'people': ['Mordred'],
                'text': 'remains hidden',
                'people_css_class': 'danger',
                'custom_message': True,
            })

        # Add additional information for evil oberion
        if uid in (EVIL_GROUP-{Role.oberon}):
            if Role.oberon in self._roles:
                info['messages'].append({
                    'people': ['Oberon'],
                    'text': 'is out there somewhere',
                    'people_css_class': 'danger',
                    'custom_message': True,
                })

        return messages
