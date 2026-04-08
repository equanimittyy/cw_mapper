'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import csv

from typing import NamedTuple
from constants import (
    NON_MAA_KEYS, ATTILA_EXPORT_DIR, CLI_DATA_DIR,
    CLI_CULTURES_PATH, CLI_MAA_PATH, CLI_TITLE_PATH,
    REPORT_OUTPUT_DIR,
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

def _load_attila_keys_from_tsv():
    """Read Attila unit keys directly from TSV exports in attila_exports/."""
    attila_keys = []
    if not os.path.exists(ATTILA_EXPORT_DIR):
        return attila_keys
    for file in sorted(os.listdir(ATTILA_EXPORT_DIR)):
        if file.endswith('.tsv'):
            source_name = file
            filepath = os.path.join(ATTILA_EXPORT_DIR, file)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                reader = csv.reader(f, delimiter='\t')
                for i, row in enumerate(reader):
                    if i < 2 or not row:
                        continue
                    attila_keys.append({'attila_map_key': row[0], 'attila_source': source_name})
    return attila_keys

def load_source_data():
    """Load source key data for CLI/GUI use.

    Attila keys: read directly from TSV exports in attila_exports/.
    CK3 keys: read from cli_data/ (preferred) or reports/ (fallback).
    """
    # Attila keys from TSV exports (always available in repo)
    attila_keys = _load_attila_keys_from_tsv()

    # CK3 keys: prefer cli_data/, fall back to reports/
    cultures_path = CLI_CULTURES_PATH if os.path.exists(CLI_CULTURES_PATH) else CULTURES_SOURCE_PATH
    maa_path = CLI_MAA_PATH if os.path.exists(CLI_MAA_PATH) else MAA_SOURCE_PATH
    title_path = CLI_TITLE_PATH if os.path.exists(CLI_TITLE_PATH) else TITLE_SOURCE_PATH

    cultures_keys = []
    maa_keys = []
    title_keys = []

    if os.path.exists(cultures_path):
        with open(cultures_path, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                cultures_keys.append({'ck3_culture': key['ck3_culture'], 'heritage': key['ck3_heritage'], 'ck3_source': key['ck3_source']})

    if os.path.exists(maa_path):
        with open(maa_path, 'r', encoding='utf-8') as f:
            key_data = csv.DictReader(f)
            for key in key_data:
                maa_keys.append({'ck3_maa': key['ck3_maa'], 'ck3_source': key['ck3_source']})

    if os.path.exists(title_path):
        with open(title_path, 'r', encoding='utf-8') as f:
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

def export_cli_source_data(on_step=None):
    """Export CK3 source key CSVs to cli_data/ for CLI use.
    Attila keys are read directly from attila_exports/ TSVs and don't need exporting.
    If on_step callback is provided, it is called with a status message before each step."""
    import cw_map_checker
    if on_step: on_step('Initialising configuration...')
    init_map_config()
    if on_step: on_step('Loading game keys (CK3 + Attila)...')
    cw_config = cw_map_checker.get_cw_config()
    game_keys = cw_map_checker.get_keys(cw_config)
    if on_step: on_step('Writing CK3 source data to cli_data/...')
    os.makedirs(CLI_DATA_DIR, exist_ok=True)
    game_keys.cultures.to_csv(CLI_CULTURES_PATH, index=False)
    game_keys.maa.to_csv(CLI_MAA_PATH, index=False)
    game_keys.titles.to_csv(CLI_TITLE_PATH, index=False)

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
