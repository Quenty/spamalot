"""
Holds the role data for the game
"""


class Role:
    generic_good = 'Generic good'
    generic_evil = 'Generic evil'

    good_lancelot = 'Good Lancelot'
    evil_lancelot = 'Evil Lancelot'

    single_lancelot_good = 'the Good Lancelot'
    single_lancelot_evil = 'the Evil Lancelot'

    merlin = 'Merlin'
    percival = 'Percival'
    assassin = 'the Assassin'
    morgana = 'Morgana'
    mordred = 'Mordred'
    oberon = 'Oberon'


EVERY_ROLE = {v for k, v in Role.__dict__.items() if not k.startswith('_')}

DISPLAY_OVERRIDE = {
    Role.single_lancelot_good: 'Lancelot',
    Role.single_lancelot_evil: 'Lancelot',
}

DOUBLE_LANCELOTS = {Role.good_lancelot, Role.evil_lancelot}
SINGLE_LANCELOTS = {Role.single_lancelot_good, Role.single_lancelot_evil}

GOOD_ALIGNED = {Role.merlin, Role.percival, Role.generic_good}
EVIL_GROUP = {Role.assassin, Role.mordred, Role.morgana, Role.generic_evil}
EVIL_ALIGNED = {*EVIL_GROUP, Role.oberon}

GOOD_ALIGNED_ALL = {*GOOD_ALIGNED, Role.good_lancelot, Role.single_lancelot_good}
EVIL_ALIGNED_ALL = {*EVIL_ALIGNED, Role.evil_lancelot, Role.single_lancelot_evil}

VISIBLE_EVIL = {*EVIL_ALIGNED, Role.evil_lancelot, Role.single_lancelot_evil, Role.single_lancelot_good} - {Role.mordred}

VISION_MATRIX = (
    # these people    know that    those people       are        this        css_class
    ({Role.merlin},     VISIBLE_EVIL,                 'evil',               'danger'),
    ({Role.percival},   {Role.merlin, Role.morgana},  'Merlin or Morgana',  'warning'),
    (EVIL_GROUP,        EVIL_GROUP,                   'also evil',          'danger'),
    (EVIL_GROUP,        DOUBLE_LANCELOTS,             'the Lancelots',      'warning'),
    (EVIL_GROUP,        SINGLE_LANCELOTS,             'the Lancelot',       'warning'),
    (DOUBLE_LANCELOTS,  DOUBLE_LANCELOTS,             'the other Lancelot', 'warning'),)

DEFAULT_FORM = {'num_players': 7, Role.merlin: True, Role.percival: True,
                Role.assassin: True, Role.morgana: True, Role.mordred: True, }
EMPTY_FORM = {'num_players': -1}
