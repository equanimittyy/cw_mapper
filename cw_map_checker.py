'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import re
import csv
import xml.etree.ElementTree as ET

from io import StringIO
from typing import NamedTuple

import configparser
import pandas as pd

from constants import (
    ATTILA_EXPORT_DIR, MAPPER_DIR, SETTINGS_DIR,
    REPORT_OUTPUT_DIR, CW_CUSTOM_VALUES, NON_MAA_KEYS, RANK_MAP,
)
from utils import get_config, get_ck3_mods_from_config

_ASCII = None

def _get_ascii():
    global _ASCII
    if _ASCII is None:
        with open("ascii.txt", 'r') as f:
            _ASCII = f.read()
    return _ASCII

# ============================================================
# NamedTuple for structured return from get_keys()
# ============================================================

class GameKeys(NamedTuple):
    cultures: pd.DataFrame
    maa: pd.DataFrame
    attila: pd.DataFrame
    titles: pd.DataFrame

# ============================================================
# Parsing helpers (deduplicated from get_keys)
# ============================================================

def _parse_culture_files(directory, source_name, mod_id):
    """Parse CK3 culture .txt files from a directory and return rows."""
    rows = []
    if not os.path.exists(directory):
        return rows
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            source_file = os.path.join(directory, file)
            file_name = os.path.basename(source_file)

            with open(source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                data = culture_txt_file.read()
            culture_data = re.findall(r"^(\w+)\s=\s\{\n([\s\S]*?)\n\}$", data, re.M | re.S)

            for data in culture_data:
                culture_name = data[0]
                heritage = re.findall(r"=\s(heritage_\w+).*[\n|\t]", data[1])
                heritage_name = heritage[0] if heritage else ''
                rows.append({
                    "ck3_culture": culture_name,
                    "ck3_heritage": heritage_name,
                    "ck3_source_file": file_name,
                    "ck3_source": source_name,
                    "mod_id": mod_id
                })
    return rows

def _parse_maa_files(directory, source_name, mod_id):
    """Parse CK3 Man-at-Arms .txt files from a directory and return rows."""
    rows = []
    if not os.path.exists(directory):
        return rows
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            source_file = os.path.join(directory, file)
            file_name = os.path.basename(source_file)

            with open(source_file, 'r', encoding="utf-8-sig") as maa_txt_file:
                data = maa_txt_file.read()

            maa_txt = re.findall(r"^(\w+)\s*=", data, re.M)
            for maa in maa_txt:
                rows.append({
                    "ck3_maa": maa,
                    "ck3_source_file": file_name,
                    "ck3_source": source_name,
                    "mod_id": mod_id
                })
    return rows

def _parse_title_files(directory, source_name, mod_id):
    """Parse CK3 landed title .txt files from a directory and return rows."""
    rows = []
    if not os.path.exists(directory):
        return rows
    for file in os.listdir(directory):
        if file.endswith('.txt'):
            source_file = os.path.join(directory, file)
            file_name = os.path.basename(source_file)

            with open(source_file, 'r', encoding="utf-8-sig") as title_txt_file:
                data = title_txt_file.read()

            title_keys = re.findall(r'^\s*([ekdc]_\w+)\s*=\s*\{', data, re.M)
            for title in title_keys:
                prefix = title[0]
                rows.append({
                    "title_key": title,
                    "title_rank": RANK_MAP.get(prefix, 'Unknown'),
                    "ck3_source_file": file_name,
                    "ck3_source": source_name,
                    "mod_id": mod_id
                })
    return rows

# ============================================================
# Core functions
# ============================================================

def get_cw_config():
    settings_paths_file = os.path.join(SETTINGS_DIR, 'GamePaths.ini')
    if os.path.exists(settings_paths_file):
        with open(settings_paths_file, 'r') as f:
            content = f.read()
            settings_content = '[GamePaths]\n' + content.replace('::', '=')
            settings_file = StringIO(settings_content)
        config = configparser.ConfigParser()
        config.read_file(settings_file)
    else:
        raise FileNotFoundError("Could not find GamePaths.ini! Please ensure you place the cw_mapper folder in the 'tools' folder of the Crusader Wars directory.")

    ck3_exe_path = config.get('GamePaths', 'CRUSADERKINGS3')
    ck3_dir_path = os.path.dirname(os.path.dirname(ck3_exe_path))
    if ck3_dir_path == "":
        raise FileNotFoundError("The Crusader Kings 3 directory path was not found! Please ensure you configure your game paths in Crusader Wars.")
    if not os.path.exists(ck3_exe_path):
        raise FileNotFoundError(f"The Crusader Kings 3 executable was not found at: {ck3_exe_path}")

    try:
        attila_exe_path = config.get('GamePaths', 'ATTILA')
        if attila_exe_path and not os.path.exists(attila_exe_path):
            print(f"== Warning: The Attila executable was not found at: {attila_exe_path}")
    except configparser.NoOptionError:
        pass

    return config

def get_keys(cw_config):
    """Read all game keys from CK3/Attila sources. Returns a GameKeys NamedTuple."""
    CK3_MODS = get_ck3_mods_from_config()

    df_attila = pd.DataFrame()
    df_ck3_cultures = pd.DataFrame()
    df_ck3_maa = pd.DataFrame()

    ck3_dir_path = os.path.dirname(os.path.dirname(cw_config.get('GamePaths', 'CRUSADERKINGS3')))
    ck3_mod_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(cw_config.get('GamePaths', 'CRUSADERKINGS3')))))), 'steamapps', 'workshop', 'content', '1158310')

    # TW:ATTILA UNIT KEYS
    os.makedirs(ATTILA_EXPORT_DIR, exist_ok=True)
    if not any(file.endswith('.tsv') for file in os.listdir(ATTILA_EXPORT_DIR)):
        raise FileNotFoundError(f'No .tsv Attila unit keys were found in {ATTILA_EXPORT_DIR}')
    else:
        print(f'== Atilla unit keys found in {ATTILA_EXPORT_DIR}! ==')

    for file in os.listdir(ATTILA_EXPORT_DIR):
        if file.endswith('.tsv'):
            source_file = os.path.join(ATTILA_EXPORT_DIR, file)
            source_name = os.path.basename(source_file)
            df = pd.read_csv(source_file, header=None, names=['attila_map_key'], sep='\t', usecols=[0])
            df = df.iloc[2:]
            df['attila_source'] = source_name
            df_attila = pd.concat([df_attila, df])

    # CK3 CULTURES (vanilla + hybrid)
    ck3_culture_dir = os.path.join(ck3_dir_path, 'game', 'common', 'culture', 'cultures')
    ck3_culture_dir_hybrid = os.path.join(ck3_dir_path, 'game', 'common', 'culture', 'creation_names')
    ck3_rows = []

    print(f'== Finding CK3 culture files in: {ck3_culture_dir} ==')
    print()
    ck3_rows += _parse_culture_files(ck3_culture_dir, "CK3", "0")

    print(f'== Finding CK3 hybrid and creation culture files in: {ck3_culture_dir_hybrid} ==')
    print()
    ck3_rows += _parse_culture_files(ck3_culture_dir_hybrid, "CK3", "0")

    # CK3 CULTURES (mods)
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod cultures ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod culture files in: {folders.name} ==')

                ck3_mod_culture_dir = os.path.join(ck3_mod_dir, folders.name, 'common', 'culture', 'cultures')
                ck3_mod_culture_dir_hybrid = os.path.join(ck3_mod_dir, folders.name, 'common', 'culture', 'creation_names')
                ck3_rows += _parse_culture_files(ck3_mod_culture_dir, mod_name, folders.name)
                ck3_rows += _parse_culture_files(ck3_mod_culture_dir_hybrid, mod_name, folders.name)

    df_ck3_cultures = pd.concat([df_ck3_cultures, pd.DataFrame(ck3_rows)], ignore_index=True)

    # CK3 MAN AT ARMS KEYS (vanilla)
    ck3_maa_dir = os.path.join(ck3_dir_path, 'game', 'common', 'men_at_arms_types')
    ck3_rows = []
    print()
    print(f'== Finding CK3 maa files in: {ck3_maa_dir} ==')
    print()
    ck3_rows += _parse_maa_files(ck3_maa_dir, "CK3", "0")

    # CK3 MAN AT ARMS KEYS (mods)
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod MAA ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                ck3_mod_maa_dir = os.path.join(ck3_mod_dir, folders.name, 'common', 'men_at_arms_types')
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod maa files in: {folders.name} ==')
                ck3_rows += _parse_maa_files(ck3_mod_maa_dir, mod_name, folders.name)

    df_ck3_maa = pd.concat([df_ck3_maa, pd.DataFrame(ck3_rows)], ignore_index=True)

    # CK3 LANDED TITLE KEYS (vanilla)
    df_ck3_titles = pd.DataFrame()
    ck3_title_dir = os.path.join(ck3_dir_path, 'game', 'common', 'landed_titles')
    ck3_rows = []
    print()
    print(f'== Finding CK3 landed title files in: {ck3_title_dir} ==')
    print()
    ck3_rows += _parse_title_files(ck3_title_dir, "CK3", "0")

    # CK3 LANDED TITLE KEYS (mods)
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod titles ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                ck3_mod_title_dir = os.path.join(ck3_mod_dir, folders.name, 'common', 'landed_titles')
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod landed title files in: {folders.name} ==')
                ck3_rows += _parse_title_files(ck3_mod_title_dir, mod_name, folders.name)

    df_ck3_titles = pd.concat([df_ck3_titles, pd.DataFrame(ck3_rows)], ignore_index=True)

    return GameKeys(cultures=df_ck3_cultures, maa=df_ck3_maa, attila=df_attila, titles=df_ck3_titles)

def mapping_validation(game_keys):
    """Validate CW mapper XMLs against game keys. Returns (results, game_keys) for report writing.

    Args:
        game_keys: GameKeys NamedTuple from get_keys()

    Returns:
        Tuple of (mapper_results dict, game_keys) where mapper_results maps
        mapper_name -> {'cultures': DataFrame, 'maa': DataFrame, 'titles': DataFrame}
    """
    df_ck3_cultures = game_keys.cultures
    df_ck3_maa = game_keys.maa
    df_attila = game_keys.attila
    df_ck3_titles = game_keys.titles

    mapper_results = {}

    if not os.path.exists(MAPPER_DIR) or not os.listdir(MAPPER_DIR):
        raise FileNotFoundError(f'No CW mapping files were found in {MAPPER_DIR}')
    else:
        print()
        print(f'== Found mapping directories: {os.listdir(MAPPER_DIR)} ==')
        print()

    for mapping in os.listdir(MAPPER_DIR):
        cultures_rows = []
        maa_rows = []
        title_rows = []

        cultures = os.path.join(MAPPER_DIR, mapping, 'Cultures')
        factions = os.path.join(MAPPER_DIR, mapping, 'Factions')
        titles = os.path.join(MAPPER_DIR, mapping, 'Titles')

        if os.path.exists(cultures):
            print(f'== ✝ Cultures found in {mapping}. ==')
            for x in os.listdir(cultures):
                if x.endswith('.xml'):
                    print(f'// ✝ Processing {x}.')
                    cultures_tree = ET.parse(os.path.join(cultures, x))
                    cultures_root = cultures_tree.getroot()
                    for cultures_parent in cultures_root:
                        for cultures_child in cultures_parent:
                            cultures_rows.append({
                                "cw_category": 'Culture',
                                "ck3_culture": cultures_child.attrib.get('name'),
                                "cw_culture": cultures_child.attrib.get('faction'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })

        if os.path.exists(factions):
            print(f'== ⚔ Factions found in {mapping}. ==')
            for x in os.listdir(factions):
                if x.endswith('.xml'):
                    print(f'// ⚔ Processing {x}.')
                    faction_tree = ET.parse(os.path.join(factions, x))
                    faction_root = faction_tree.getroot()
                    for faction_parent in faction_root:
                        for faction_child in faction_parent:
                            maa_rows.append({
                                "cw_type": faction_child.tag,
                                "cw_category": 'Faction',
                                "cw_maa_parent": faction_parent.attrib.get('name'),
                                "cw_maa": faction_child.attrib.get('type'),
                                "attila_map_key": faction_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })

        if os.path.exists(titles):
            print(f'== ♠ Titles found in {mapping}. ==')
            for x in os.listdir(titles):
                if x.endswith('.xml'):
                    print(f'// ♠ Processing {x}.')
                    titles_tree = ET.parse(os.path.join(titles, x))
                    titles_root = titles_tree.getroot()
                    for titles_parent in titles_root:
                        for titles_child in titles_parent:
                            title_rows.append({
                                "cw_type": titles_child.tag,
                                "cw_category": 'Title',
                                "title_key": titles_parent.attrib.get('title_key'),
                                "cw_maa_parent": titles_parent.attrib.get('name'),
                                "cw_maa": titles_child.attrib.get('type'),
                                "attila_map_key": titles_child.attrib.get('key'),
                                "cw_source_file": x,
                                "cw_source_folder": mapping
                            })

        # Build result DataFrames for this mapper
        df_cultures = pd.DataFrame(cultures_rows)
        df_maa = pd.DataFrame(maa_rows)
        df_titles = pd.DataFrame(title_rows)

        if not df_maa.empty:
            df_maa = pd.merge(df_maa, df_attila, on='attila_map_key', how='left')
        if not df_cultures.empty:
            df_cultures = pd.merge(df_cultures, df_ck3_cultures, on='ck3_culture', how='left')
        if not df_titles.empty:
            df_titles = pd.merge(df_titles, df_ck3_titles, on='title_key', how='left')

        mapper_results[mapping] = {
            'cultures': df_cultures,
            'maa': df_maa,
            'titles': df_titles,
        }

    return mapper_results, game_keys

def write_reports(mapper_results, game_keys):
    """Write CSV reports from validation results to disk."""
    os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
    for mapping, results in mapper_results.items():
        os.makedirs(os.path.join(REPORT_OUTPUT_DIR, mapping), exist_ok=True)

        if not results['maa'].empty:
            results['maa'].to_csv(os.path.join(REPORT_OUTPUT_DIR, mapping, f'{mapping}_cw_maa.csv'))
        if not results['titles'].empty:
            results['titles'].to_csv(os.path.join(REPORT_OUTPUT_DIR, mapping, f'{mapping}_cw_titles.csv'))
        print(f'// 🕮  Report produced for man-at-arms files for mapper: {mapping}.')

        if not results['cultures'].empty:
            results['cultures'].to_csv(os.path.join(REPORT_OUTPUT_DIR, mapping, f'{mapping}_cw_cultures.csv'))
        print(f'// 🕮  Report produced for culture files for mapper: {mapping}.')

    # Write source key files
    game_keys.attila.to_csv(os.path.join(REPORT_OUTPUT_DIR, 'source_attila_keys.csv'))
    game_keys.cultures.to_csv(os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_cultures_keys.csv'))
    game_keys.maa.to_csv(os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_maa_keys.csv'))
    game_keys.titles.to_csv(os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_title_keys.csv'))
    print(f'Report produced for source key files.')

def _print_key_list(keys, sum_f, columns=4, col_width=30):
    """Print a list of keys in a formatted column layout."""
    for i in range(0, len(keys), columns):
        row = keys[i:i + columns]
        formatted_row = "  ".join(key.ljust(col_width) for key in row)
        print(f'\t  {formatted_row}', file=sum_f)


def summary():
    ck3_culture_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_cultures_keys.csv')
    ck3_maa_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_maa_keys.csv')
    attila_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_attila_keys.csv')
    ck3_title_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_title_keys.csv')

    with open('summary_log.txt', 'w', encoding="utf-8-sig") as sum_f:
        print(_get_ascii(), file=sum_f)
        if os.listdir(REPORT_OUTPUT_DIR):
            print('== Found reports in report directory ==', file=sum_f)
            print('==================================================', file=sum_f)
        else:
            print(f'== No reports were found in {REPORT_OUTPUT_DIR}. No summary can be made until reports are produced based on your CK3/Attila install... ==', file=sum_f)
            print('', file=sum_f)
            raise FileNotFoundError(f'No reports were found in {REPORT_OUTPUT_DIR}')

        for mapping in os.listdir(REPORT_OUTPUT_DIR):
            map_folder = os.path.join(REPORT_OUTPUT_DIR, mapping)

            if os.path.isdir(map_folder):
                print(f'◆ Mapper: {mapping}', file=sum_f)
                target_config = get_config(mapping)

                # Build mod name/ID lookup
                source_ids = []
                id_to_name = {}
                for mod in target_config:
                    mod_name, mod_id = mod[0], str(mod[1])
                    source_ids.append(mod_id)
                    id_to_name[mod_id] = mod_name

                # ── Required Mods ──
                print('', file=sum_f)
                print('\t🛠 Required CK3 Mods for this mapper:', file=sum_f)
                for mod in target_config:
                    mod_name, mod_id = mod[0], mod[1]
                    if mod_id == 0:
                        print(f'\t  - {mod_name}', file=sum_f)
                    else:
                        print(f'\t  - {mod_name} (Workshop ID: {mod_id})', file=sum_f)

                # ── Load source key data ──
                expected_culture_keys = []
                expected_maa_keys = []
                source_attila_keys = []
                expected_title_keys = []
                found_mods = []

                with open(ck3_culture_key_file, 'r') as f:
                    key_data = csv.DictReader(f)
                    for key in key_data:
                        if key.get("mod_id") in source_ids:
                            expected_culture_keys.append(key)
                            found_mods.append(key.get("mod_id"))

                with open(ck3_maa_key_file, 'r') as f:
                    key_data = csv.DictReader(f)
                    for key in key_data:
                        if key.get("mod_id") in source_ids:
                            expected_maa_keys.append(key)
                            found_mods.append(key.get("mod_id"))

                with open(attila_key_file, 'r') as f:
                    key_data = csv.DictReader(f)
                    for key in key_data:
                        source_attila_keys.append(key)

                with open(ck3_title_key_file, 'r') as f:
                    key_data = csv.DictReader(f)
                    for key in key_data:
                        if key.get("mod_id") in source_ids:
                            expected_title_keys.append(key)
                            found_mods.append(key.get("mod_id"))

                # ── Missing Mods ──
                missing_mod_ids = set(source_ids) - set(found_mods)
                print('', file=sum_f)
                if missing_mod_ids:
                    missing_mod_names = [f'{id_to_name.get(mid, "Unknown")} (ID: {mid})' for mid in sorted(missing_mod_ids)]
                    print(f'\t⚠ MODS NOT FOUND ON PC ({len(missing_mod_ids)}):', file=sum_f)
                    print(f'\t  These mods were not detected in your CK3 install.', file=sum_f)
                    print(f'\t  Missing mods means their cultures/MAA will not be checked.', file=sum_f)
                    for name in missing_mod_names:
                        print(f'\t  - {name}', file=sum_f)
                else:
                    print('\t✓ All required mods found on PC', file=sum_f)
                print('', file=sum_f)

                # ── Process report files ──
                files = os.listdir(map_folder)
                if not files:
                    print(f'\t⚠ No reports were found in {map_folder}', file=sum_f)
                    print('==================================================', file=sum_f)
                    continue

                if not (expected_culture_keys and expected_maa_keys):
                    print('\t⚠ Missing source key files — cannot check for missing keys.', file=sum_f)
                    print('==================================================', file=sum_f)
                    continue

                # Gather all missing/superfluous data from report files
                missing_cultures = []
                missing_maa = []
                missing_attila = []
                missing_titles = []
                superfluous_cultures = []
                superfluous_maa = []

                for file in files:
                    file_path = os.path.join(map_folder, file)

                    if file.endswith('cultures.csv'):
                        with open(file_path, 'r') as f:
                            report_data = csv.DictReader(f)
                            expected = [d["ck3_culture"] for d in expected_culture_keys]
                            found = [d["ck3_culture"] for d in report_data]
                            missing_cultures = sorted(set(expected) - set(found))
                            superfluous_cultures = sorted(set(found) - set(expected))

                    elif file.endswith('maa.csv'):
                        with open(file_path, 'r') as f:
                            report_data = list(csv.DictReader(f))
                            expected_maa = [d["ck3_maa"] for d in expected_maa_keys]
                            report_maa = [d["cw_maa"] for d in report_data]
                            missing_maa = sorted(set(expected_maa) - set(report_maa))
                            superfluous_maa = sorted(set(report_maa) - set(expected_maa) - set(NON_MAA_KEYS))

                            report_attila = [d["attila_map_key"] for d in report_data]
                            expected_attila = [d["attila_map_key"] for d in source_attila_keys]
                            missing_attila = sorted(set(report_attila) - set(expected_attila) - CW_CUSTOM_VALUES)

                    elif file.endswith('titles.csv'):
                        with open(file_path, 'r') as f:
                            title_rows = list(csv.DictReader(f))
                            if title_rows:
                                report_title_keys = set(d["title_key"] for d in title_rows)
                                expected_title_set = set(d["title_key"] for d in expected_title_keys)
                                missing_titles = sorted(report_title_keys - expected_title_set)

                # ── Missing CK3 Cultures (defaults to DEFAULT faction) ──
                print('\t⚑ CK3 Cultures:', file=sum_f)
                if missing_cultures:
                    print(f'\t  ⚠ {len(missing_cultures)} missing — these cultures will fall back to the DEFAULT faction', file=sum_f)
                    _print_key_list(missing_cultures, sum_f)
                else:
                    print('\t  ✓ All CK3 cultures are mapped', file=sum_f)
                if superfluous_cultures:
                    print(f'\t  ⚠ {len(superfluous_cultures)} superfluous — in mapper but not found in CK3 source data', file=sum_f)
                    _print_key_list(superfluous_cultures, sum_f)
                print('', file=sum_f)

                # ── Missing CK3 MAA (causes crash) ──
                print('\t⚔ CK3 Men-at-Arms:', file=sum_f)
                if missing_maa:
                    print(f'\t  ⚠ {len(missing_maa)} missing — WILL CAUSE CRASH if these MAA are used in battle', file=sum_f)
                    _print_key_list(missing_maa, sum_f)
                else:
                    print('\t  ✓ All CK3 MAA types are mapped', file=sum_f)
                if superfluous_maa:
                    print(f'\t  ⚠ {len(superfluous_maa)} superfluous — in mapper but not found in CK3 source data', file=sum_f)
                    _print_key_list(superfluous_maa, sum_f)
                print('', file=sum_f)

                # ── Missing Attila Keys (causes crash) ──
                print('\t⚔ Attila Unit Keys:', file=sum_f)
                if missing_attila:
                    print(f'\t  ⚠ {len(missing_attila)} missing — WILL CAUSE CRASH (keys used in mapper but not found in Attila exports)', file=sum_f)
                    _print_key_list(missing_attila, sum_f)
                else:
                    print('\t  ✓ All Attila unit keys are valid', file=sum_f)
                print('', file=sum_f)

                # ── Missing Title Keys ──
                print('\t♠ Title Keys:', file=sum_f)
                if missing_titles:
                    print(f'\t  ⚠ {len(missing_titles)} missing title keys', file=sum_f)
                    _print_key_list(missing_titles, sum_f)
                else:
                    print('\t  ✓ All title keys are valid', file=sum_f)
                print('', file=sum_f)

                print('==================================================', file=sum_f)
