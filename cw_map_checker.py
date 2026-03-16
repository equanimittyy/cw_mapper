'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import re
import sys
import csv
import webbrowser
import xml.etree.ElementTree as ET

from io import StringIO
from typing import NamedTuple

import configparser
import pandas as pd

from constants import (
    WORKING_DIR, ATTILA_EXPORT_DIR, MAPPER_DIR, SETTINGS_DIR,
    REPORT_OUTPUT_DIR, CW_CUSTOM_VALUES, RANK_MAP,
)
from utils import get_config, init_map_config, get_ck3_mods_from_config

os.makedirs(REPORT_OUTPUT_DIR, exist_ok=True)
os.chdir(WORKING_DIR)

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
        print(f'== No .tsv Atilla unit keys were found in {ATTILA_EXPORT_DIR} ==')
        print(f'Please read the readme.txt!')
        webbrowser.open("readme.txt")
        sys.exit(1)
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

    if not os.listdir(MAPPER_DIR):
        print()
        print(f'== No CW mapping files were found in {MAPPER_DIR}... ==')
        sys.exit(1)
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

def summary():
    output_columns = 4

    ck3_culture_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_cultures_keys.csv')
    ck3_maa_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_maa_keys.csv')
    attila_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_attila_keys.csv')
    ck3_title_key_file = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_title_keys.csv')

    with open('summary_log.txt', 'w', encoding="utf-8-sig") as sum_f:
        print(_get_ascii(), file=sum_f)
        if os.listdir(REPORT_OUTPUT_DIR):
            print(f'== Found reports in report directory ==', file=sum_f)
            print('==================================================', file=sum_f)
        else:
            print(f'== No reports were found in {REPORT_OUTPUT_DIR}. No summary can be made until reports are produced based on your CK3/Attila install... ==', file=sum_f)
            print('', file=sum_f)
            sys.exit(1)

        for mapping in os.listdir(REPORT_OUTPUT_DIR):
            map_folder = os.path.join(REPORT_OUTPUT_DIR, mapping)

            if os.path.isdir(map_folder):
                print('◆ Mapper: ' + mapping, file=sum_f)
                target_config = get_config(mapping)

                source_ids = []
                for mods in target_config:
                    id = str(mods[1])
                    source_ids.append(id)

                print('', file=sum_f)
                print(f'\t🛠 Sources: {target_config}', file=sum_f)

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

                missing_mods = set(source_ids) - set(found_mods)
                if missing_mods:
                    print(f'\t↳ ⚠ Sources missing: {missing_mods}\n\tMissing sources can cause inaccuracies when checking for keys', file=sum_f)
                    print('', file=sum_f)
                else:
                    print(f'\t↳ ✓ No missing sources', file=sum_f)
                    print('', file=sum_f)

                files = os.listdir(map_folder)
                if files:
                    for file in files:
                        missing_keys = []
                        missing_attila_keys = []
                        title_rows = []
                        missing_title_keys = []
                        # CULTURES
                        if file.endswith('cultures.csv'):
                            print(f'\t⚑ Cultures: ', file=sum_f)
                            file_path = os.path.join(map_folder, file)

                            with open(file_path, 'r') as f:
                                report_data = csv.DictReader(f)
                                expected_cultures = [d["ck3_culture"] for d in expected_culture_keys]
                                report_cultures = [d["ck3_culture"] for d in report_data]
                                missing_keys = sorted(list(set(expected_cultures) - set(report_cultures)))

                        # MAN AT ARMS
                        if file.endswith('maa.csv'):
                            print(f'\t⚔ ManAtArms: ', file=sum_f)
                            file_path = os.path.join(map_folder, file)

                            with open(file_path, 'r') as f:
                                report_data = list(csv.DictReader(f))
                                expected_maa = [d["ck3_maa"] for d in expected_maa_keys]
                                report_maa = [d["cw_maa"] for d in report_data]
                                missing_keys = sorted(set(expected_maa) - set(report_maa))

                                report_attila_keys = [d["attila_map_key"] for d in report_data]
                                expected_attila_keys = [d["attila_map_key"] for d in source_attila_keys]
                                missing_attila_keys = sorted(set(report_attila_keys) - set(expected_attila_keys) - CW_CUSTOM_VALUES)

                        # TITLES
                        if file.endswith('titles.csv'):
                            print(f'\t♠ Titles: ', file=sum_f)
                            file_path = os.path.join(map_folder, file)

                            with open(file_path, 'r') as f:
                                title_rows = list(csv.DictReader(f))
                                if title_rows:
                                    report_title_keys = set(d["title_key"] for d in title_rows)
                                    expected_title_key_set = set(d["title_key"] for d in expected_title_keys)
                                    missing_title_keys = sorted(report_title_keys - expected_title_key_set)

                        if expected_culture_keys and expected_maa_keys:
                            if file.endswith('cultures.csv') or file.endswith('maa.csv'):
                                if missing_keys:
                                    print(f'\t↳ ⚠ Missing keys: {len(missing_keys)} missing keys', file=sum_f)
                                    for i in range(0, len(missing_keys), output_columns):
                                        row = missing_keys[i:i + output_columns]
                                        formatted_row = " ".join(key.ljust(30) for key in row)
                                        print(formatted_row, file=sum_f)
                                    print('', file=sum_f)
                                else:
                                    print(f'\t↳ ✓ No missing keys found for {file}', file=sum_f)
                                    print('', file=sum_f)

                                if missing_attila_keys:
                                    print(f'\t↳ ⚠ Missing keys from Total War Attila: {len(missing_attila_keys)} missing keys', file=sum_f)
                                    for i in range(0, len(missing_attila_keys), output_columns):
                                        row = missing_attila_keys[i:i + output_columns]
                                        formatted_row = " ".join(key.ljust(30) for key in row)
                                        print(formatted_row, file=sum_f)
                                    print('', file=sum_f)
                                else:
                                    if file.endswith('maa.csv'):
                                        print(f'\t↳ ✓ No missing Attila keys were found for {file}', file=sum_f)
                                        print('', file=sum_f)

                            if file.endswith('titles.csv'):
                                if missing_title_keys:
                                    print(f'\t↳ ⚠ Missing title keys: {len(missing_title_keys)} missing keys', file=sum_f)
                                    for i in range(0, len(missing_title_keys), output_columns):
                                        row = missing_title_keys[i:i + output_columns]
                                        formatted_row = " ".join(key.ljust(30) for key in row)
                                        print(formatted_row, file=sum_f)
                                    print('', file=sum_f)
                                else:
                                    print(f'\t↳ ✓ No missing title keys found', file=sum_f)
                                    print('', file=sum_f)
                        else:
                            print(f'\t↳ ⚠ Missing all source files for keys: {file}. Skipping...', file=sum_f)
                            print('', file=sum_f)

                else:
                    print(f'↳ ⚠ No reports were found in {map_folder}', file=sum_f)
                print('==================================================', file=sum_f)
