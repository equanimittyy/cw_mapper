'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import csv

from typing import NamedTuple
from constants import (
    NON_MAA_KEYS,
    ATTILA_SOURCE_PATH, CULTURES_SOURCE_PATH, MAA_SOURCE_PATH, TITLE_SOURCE_PATH,
)
from utils import init_map_config

# ============================================================
# Source data container
# ============================================================

class SourceData(NamedTuple):
    attila_keys: list
    cultures_keys: list
    maa_keys: list
    title_keys: list
    attila_sources: list
    ck3_sources: list
    title_sources: list

def load_source_data():
    """Load source key data from CSV report files. Returns a SourceData."""
    attila_keys = []
    cultures_keys = []
    maa_keys = []
    title_keys = []

    if os.path.exists(ATTILA_SOURCE_PATH):
        with open(ATTILA_SOURCE_PATH, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                attila_keys.append({'attila_map_key': key['attila_map_key'], 'attila_source': key['attila_source']})

    if os.path.exists(CULTURES_SOURCE_PATH):
        with open(CULTURES_SOURCE_PATH, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                cultures_keys.append({'ck3_culture': key['ck3_culture'], 'heritage': key['ck3_heritage'], 'ck3_source': key['ck3_source']})

    if os.path.exists(MAA_SOURCE_PATH):
        with open(MAA_SOURCE_PATH, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                maa_keys.append({'ck3_maa': key['ck3_maa'], 'ck3_source': key['ck3_source']})

    if os.path.exists(TITLE_SOURCE_PATH):
        with open(TITLE_SOURCE_PATH, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                title_keys.append({'title_key': key['title_key'], 'title_rank': key['title_rank'], 'ck3_source': key['ck3_source']})

    for maa in NON_MAA_KEYS:
        maa_keys.append({'ck3_maa': maa, 'ck3_source': 'CW'})

    attila_sources = [item['attila_source'] for item in attila_keys]
    ck3_sources = [item['ck3_source'] for item in cultures_keys] + [item['ck3_source'] for item in maa_keys]
    title_sources = [item['ck3_source'] for item in title_keys]

    return SourceData(
        attila_keys=attila_keys,
        cultures_keys=cultures_keys,
        maa_keys=maa_keys,
        title_keys=title_keys,
        attila_sources=attila_sources,
        ck3_sources=ck3_sources,
        title_sources=title_sources,
    )

def run_validation(on_step=None):
    """Run the CW validation pipeline (init config, validate, write reports, summarize).
    If on_step callback is provided, it is called with a status message before each step."""
    import cw_map_checker
    if on_step: on_step('Initialising configuration...')
    init_map_config()
    if on_step: on_step('Loading game keys (CK3 + Attila)...')
    cw_config = cw_map_checker.get_cw_config()
    game_keys = cw_map_checker.get_keys(cw_config)
    if on_step: on_step('Validating mapper files...')
    results, game_keys = cw_map_checker.mapping_validation(game_keys)
    if on_step: on_step('Writing reports...')
    cw_map_checker.write_reports(results, game_keys)
    if on_step: on_step('Generating summary...')
    cw_map_checker.summary()
