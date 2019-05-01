from models.assignment.RoleData import *
from random import choice

DEFAULT_FORM = {'num_players': 7, Role.merlin: True, Role.percival: True,
                Role.assassin: True, Role.morgana: True, Role.mordred: True, }


def MakeConfiguration(form):
    assert(form)

    conf = {}

    conf['checkboxes'] = ((Role.merlin, Role.percival),
                          (Role.assassin, Role.morgana, Role.mordred, Role.oberon))

    conf['boxes'] = [r for g in conf['checkboxes'] for r in g]

    # needed by html
    conf['num_players'] = int(form['num_players'])
    conf['num_lancelots'] = int(form.get('num_lancelots', 0))

    conf['selected'] = {r: r in form for r in conf['boxes']}

    # generate a list of roles
    conf['complaints'] = []

    conf['roles'] = [role for role in conf['boxes'] if role in form]

    if conf['num_lancelots'] == 1:
        conf['roles'].append(
            choice((Role.single_lancelot_evil, Role.single_lancelot_good)))
    elif conf['num_lancelots'] == 2:
        conf['roles'].append(Role.good_lancelot)
        conf['roles'].append(Role.evil_lancelot)

    size = {'evil': 2}
    if conf['num_players'] >= 7:
        size['evil'] = 3
    if conf['num_players'] >= 10:
        size['evil'] = 4

    size['good'] = conf['num_players'] - size['evil'] - conf['num_lancelots']

    for name, group, role in (('evil', EVIL_ALIGNED, Role.generic_evil),
                              ('good', GOOD_ALIGNED, Role.generic_good)):

        special = sum(n in conf['roles'] for n in group)
        generic = size[name] - special

        if generic < 0:
            conf['complaints'].append(f'Too many {name} roles')

        for _ in range(generic):
            conf['roles'].append(role)

    if form.get('enable_prank_mode') and randint(1, 100) == 1:
        conf['prank_everyone_is'] = choice(list(set(conf['roles'])))

    return conf


def MakeDefaultConfiguration():
    return MakeConfiguration(DEFAULT_FORM)
