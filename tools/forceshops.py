"""Force the town shop sequence in the local engine (to compare agents in the same world as a replay)."""
import random
from kaggle_environments.envs.kaggriculture import kaggriculture as K

FORCED = {'shops': None}
_orig_end = K._end_of_day


def _end_of_day(state, env, day):
    town = state[0].observation.town
    before = len(town['unlocked_shops'])
    _orig_end(state, env, day)
    if FORCED['shops'] is not None and len(town['unlocked_shops']) > before:
        town['unlocked_shops'][-1] = FORCED['shops'][len(town['unlocked_shops']) - 1]


K._end_of_day = _end_of_day


def force(shops):
    FORCED['shops'] = list(shops) if shops else None
