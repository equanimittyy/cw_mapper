'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import re
import sys
import csv
import json
import webbrowser
import xml.etree.ElementTree as ET

from io import StringIO

import configparser
import pandas as pd

from utils import get_config, init_map_config

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Identify working directories
WORKING_DIR = application_path
ATTILA_EXPORT_DIR = os.path.join(WORKING_DIR, 'attila_exports','db','main_units_tables')
MAPPER_DIR = '../../unit mappers/attila'
SETTINGS_DIR = '../../data/settings'
REPORT_OUTPUT_DIR = 'reports'
os.makedirs(REPORT_OUTPUT_DIR,exist_ok=True) # Ensure the report directory exists
os.chdir(WORKING_DIR)

CONFIG_DIR = os.path.join('config')
target_config = os.path.join(CONFIG_DIR,'mod_config.json')

with open("ascii.txt", 'r') as f:
    ASCII = f.read()

# Set CK3_MODS to check whatever is in config
CK3_MODS = {}
if not os.path.exists(target_config):
    init_map_config()

with open(target_config, 'r') as f:
    data = json.load(f)
    for map in data.items():
        for mod in map[1]:
            mod_name = mod[0]
            mod_id = str(mod[1])
            CK3_MODS[mod_name] = mod_id

def get_cw_config():
    # Handle improper .ini structure and pass through configparser
    settings_paths_file = os.path.join(SETTINGS_DIR,'GamePaths.ini')
    if os.path.exists(settings_paths_file):
        with open (settings_paths_file,'r') as f:
            content = f.read()
            settings_content = '[GamePaths]\n' + content.replace('::','=')
            settings_file = StringIO(settings_content)
        config = configparser.ConfigParser()
        config.read_file(settings_file)
    else:
        raise FileNotFoundError("Could not find GamePaths.ini! Please ensure you place the cw_mapper folder in the 'tools' folder of the Crusader Wars directory.")

    ck3_exe_path = config.get('GamePaths','CRUSADERKINGS3')
    ck3_dir_path = os.path.dirname(os.path.dirname(ck3_exe_path))
    if ck3_dir_path == "":
        raise FileNotFoundError("The Crusader Kings 3 directory path was not found! Please ensure you configure your game paths in Crusader Wars.")
    if not os.path.exists(ck3_exe_path):
        raise FileNotFoundError(f"The Crusader Kings 3 executable was not found at: {ck3_exe_path}")

    try:
        attila_exe_path = config.get('GamePaths','ATTILA')
        if attila_exe_path and not os.path.exists(attila_exe_path):
            print(f"== Warning: The Attila executable was not found at: {attila_exe_path}")
    except configparser.NoOptionError:
        pass

    return config

def get_keys(cw_config):

    # Declare the necessary data frames for obtaining keys
    df_attila = pd.DataFrame() # TW:Attila unit keys
    df_ck3_cultures = pd.DataFrame() # CK3 culture keys
    df_ck3_maa = pd.DataFrame()  # CK3 man at arms keys

    ck3_dir_path = os.path.dirname(os.path.dirname(cw_config.get('GamePaths','CRUSADERKINGS3')))
    ck3_mod_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(cw_config.get('GamePaths','CRUSADERKINGS3')))))),'steamapps','workshop','content','1158310')

    # TW:ATTILA UNIT KEYS
    os.makedirs(ATTILA_EXPORT_DIR, exist_ok=True)
    if not any(file.endswith('.tsv') for file in os.listdir(ATTILA_EXPORT_DIR)):
        print(f'== No .tsv Atilla unit keys were found in {ATTILA_EXPORT_DIR} ==')
        print(f'Please read the readme.txt!')
        
        # Auto open readme.txt upon close
        webbrowser.open("readme.txt")
        sys.exit(1) # Exit with an error
    else:
        print(f'== Atilla unit keys found in {ATTILA_EXPORT_DIR}! ==')

    for file in os.listdir(ATTILA_EXPORT_DIR):
        if file.endswith('.tsv'):
            # Define source of file if ends with .tsv
            source_file = os.path.join(ATTILA_EXPORT_DIR,file)
            source_name = os.path.basename(source_file)
                    
            df = pd.read_csv(source_file, header=None, names=['attila_map_key']
                            ,sep='\t', usecols=[0])
            df = df.iloc[2:]
            df['attila_source'] = source_name
            # Append loop
            df_attila = pd.concat([df_attila, df])
    
    ck3_culture_dir = os.path.join(ck3_dir_path,'game','common','culture','cultures')
    ck3_culture_dir_hybrid = os.path.join(ck3_dir_path,'game','common','culture','creation_names')
    ck3_rows = []

    # Obtain vanilla cultures from CK3
    print(f'== Finding CK3 culture files in: {ck3_culture_dir} ==')
    print()
    for file in os.listdir(ck3_culture_dir):
        if file.endswith('.txt'):
            source_file = os.path.join(ck3_culture_dir,file)
            source_name = os.path.basename(source_file)

            with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                data = culture_txt_file.read()
            culture_data = re.findall(r"^(\w+)\s=\s\{\n([\s\S]*?)\n\}\n$", data, re.M | re.S)

            for data in culture_data:
                culture_name = data[0]
                heritage = re.findall(r"=\s(heritage_\w+).*[\n|\t]", data[1])
                if not heritage:
                    heritage_name = ''
                else:
                    heritage_name = heritage[0]
                # heritage = [info for info in culture_info_list if info]
                ck3_rows.append({
                    "ck3_culture":culture_name,
                    "ck3_heritage":heritage_name,
                    "ck3_source_file":source_name,
                    "ck3_source":"CK3",
                    "mod_id":"0"
                })

    # Obtain additional cultures from hybrid and creation names
    print(f'== Finding CK3 hybrid and creation culture files in: {ck3_culture_dir_hybrid} ==')
    print()
    for file in os.listdir(ck3_culture_dir_hybrid):
        if file.endswith('.txt'):
            source_file = os.path.join(ck3_culture_dir_hybrid,file)
            source_name = os.path.basename(source_file)

            with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                data = culture_txt_file.read()
            culture_data = re.findall(r"^(\w+)\s=\s\{\n([\s\S]*?)\n\}$", data, re.M | re.S)

            for data in culture_data:
                culture_name = data[0]
                heritage = re.findall(r"=\s(heritage_\w+).*[\n|\t]", data[1])
                if not heritage:
                    heritage_name = ''
                else:
                    heritage_name = heritage[0]
                # heritage = [info for info in culture_info_list if info]
                ck3_rows.append({
                    "ck3_culture":culture_name,
                    "ck3_heritage":heritage_name,
                    "ck3_source_file":source_name,
                    "ck3_source":"CK3",
                    "mod_id":"0"
                })

    # Obtain additional cultures from CK3 mods
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod cultures ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                ck3_mod_culture_dir = os.path.join(ck3_mod_dir,folders.name,'common','culture','cultures')
                ck3_mod_culture_dir_hybrid = os.path.join(ck3_mod_dir,folders.name,'common','culture','creation_names')
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod culture files in: {folders.name} ==')

                if os.path.exists(ck3_mod_culture_dir):
                    for file in os.listdir(ck3_mod_culture_dir):
                        if file.endswith('.txt'):
                            source_file = os.path.join(ck3_mod_culture_dir,file)
                            source_name = os.path.basename(source_file)

                            with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                                data = culture_txt_file.read()
                            culture_data = re.findall(r"^(\w+)\s=\s\{\n([\s\S]*?)\n\}$", data, re.M | re.S)

                            for data in culture_data:
                                culture_name = data[0]
                                heritage = re.findall(r"=\s(heritage_\w+).*[\n|\t]", data[1])
                                if not heritage:
                                    heritage_name = ''
                                else:
                                    heritage_name = heritage[0]
                                ck3_rows.append({
                                    "ck3_culture":culture_name,
                                    "ck3_heritage":heritage_name,
                                    "ck3_source_file":source_name,
                                    "ck3_source":mod_name,
                                    "mod_id":folders.name
                                })

                # Obtain additional cultures from hybrid and creation names
                if os.path.exists(ck3_mod_culture_dir_hybrid):
                    for file in os.listdir(ck3_mod_culture_dir_hybrid):
                        if file.endswith('.txt'):
                            source_file = os.path.join(ck3_mod_culture_dir_hybrid,file)
                            source_name = os.path.basename(source_file)

                            with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                                data = culture_txt_file.read()
                            culture_data = re.findall(r"^(\w+)\s=\s\{\n([\s\S]*?)\n\}$", data, re.M | re.S)

                            for data in culture_data:
                                culture_name = data[0]
                                heritage = re.findall(r"=\s(heritage_\w+).*[\n|\t]", data[1])
                                if not heritage:
                                    heritage_name = ''
                                else:
                                    heritage_name = heritage[0]
                                ck3_rows.append({
                                    "ck3_culture":culture_name,
                                    "ck3_heritage":heritage_name,
                                    "ck3_source_file":source_name,
                                    "ck3_source":mod_name,
                                    "mod_id":folders.name
                                })

    df_ck3_cultures = pd.concat([df_ck3_cultures,pd.DataFrame(ck3_rows)],ignore_index=True)

    # CK3 + MODS MAN AT ARMS KEYS
    ck3_maa_dir = os.path.join(ck3_dir_path,'game','common','men_at_arms_types')
    ck3_rows = []
    print()
    print(f'== Finding CK3 maa files in: {ck3_maa_dir} ==')
    print()
    for file in os.listdir(ck3_maa_dir):
        if file.endswith('.txt'):
            source_file = os.path.join(ck3_maa_dir,file)
            source_name = os.path.basename(source_file)

            with open (source_file, 'r', encoding="utf-8-sig") as maa_txt_file:
                data = maa_txt_file.read()

            maa_txt = re.findall(r"^(\w+)\s*=", data, re.M)
            for maa in maa_txt:
                ck3_rows.append({
                    "ck3_maa":maa,
                    "ck3_source_file":source_name,
                    "ck3_source":"CK3",
                    "mod_id":"0"
                })

    # Obtain additional maa from CK3 mods
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod MAA ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                ck3_mod_maa_dir = os.path.join(ck3_mod_dir,folders.name,'common','men_at_arms_types')
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod maa files in: {folders.name} ==')

                if os.path.exists(ck3_mod_maa_dir):
                    for file in os.listdir(ck3_mod_maa_dir):
                        if file.endswith('.txt'):
                            source_file = os.path.join(ck3_mod_maa_dir,file)
                            source_name = os.path.basename(source_file)

                            with open (source_file, 'r', encoding="utf-8-sig") as maa_txt_file:
                                data = maa_txt_file.read()

                            maa_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                            for maa in maa_txt:
                                ck3_rows.append({
                                    "ck3_maa":maa,
                                    "ck3_source_file":source_name,
                                    "ck3_source":mod_name,
                                    "mod_id":folders.name
                                })

    df_ck3_maa = pd.concat([df_ck3_maa,pd.DataFrame(ck3_rows)],ignore_index=True)

    # CK3 + MODS LANDED TITLE KEYS
    df_ck3_titles = pd.DataFrame()
    ck3_title_dir = os.path.join(ck3_dir_path,'game','common','landed_titles')
    ck3_rows = []
    print()
    print(f'== Finding CK3 landed title files in: {ck3_title_dir} ==')
    print()

    rank_map = {'e': 'Empire', 'k': 'Kingdom', 'd': 'Duchy'}

    if os.path.exists(ck3_title_dir):
        for file in os.listdir(ck3_title_dir):
            if file.endswith('.txt'):
                source_file = os.path.join(ck3_title_dir,file)
                source_name = os.path.basename(source_file)

                with open(source_file, 'r', encoding="utf-8-sig") as title_txt_file:
                    data = title_txt_file.read()

                title_keys = re.findall(r'^([ekd]_\w+)\s*=\s*\{', data, re.M)
                for title in title_keys:
                    prefix = title[0]
                    ck3_rows.append({
                        "title_key":title,
                        "title_rank":rank_map.get(prefix, 'Unknown'),
                        "ck3_source_file":source_name,
                        "ck3_source":"CK3",
                        "mod_id":"0"
                    })

    # Obtain additional titles from CK3 mods
    if not os.path.exists(ck3_mod_dir):
        print(f'== CK3 mod directory not found: {ck3_mod_dir}, skipping mod titles ==')
    else:
        for folders in os.scandir(ck3_mod_dir):
            if folders.name in CK3_MODS.values():
                ck3_mod_title_dir = os.path.join(ck3_mod_dir,folders.name,'common','landed_titles')
                mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)]
                print(f'== Finding mod landed title files in: {folders.name} ==')

                if os.path.exists(ck3_mod_title_dir):
                    for file in os.listdir(ck3_mod_title_dir):
                        if file.endswith('.txt'):
                            source_file = os.path.join(ck3_mod_title_dir,file)
                            source_name = os.path.basename(source_file)

                            with open(source_file, 'r', encoding="utf-8-sig") as title_txt_file:
                                data = title_txt_file.read()

                            title_keys = re.findall(r'^([ekd]_\w+)\s*=\s*\{', data, re.M)
                            for title in title_keys:
                                prefix = title[0]
                                ck3_rows.append({
                                    "title_key":title,
                                    "title_rank":rank_map.get(prefix, 'Unknown'),
                                    "ck3_source_file":source_name,
                                    "ck3_source":mod_name,
                                    "mod_id":folders.name
                                })

    df_ck3_titles = pd.concat([df_ck3_titles,pd.DataFrame(ck3_rows)],ignore_index=True)

    return df_ck3_cultures, df_ck3_maa, df_attila, df_ck3_titles

def mapping_validation(culture_keys, maa_keys, attila_keys, title_keys=None):
    # == BEGIN MAPPING ==
    # Declare data frame for processed cw mapping
    df_cultures = pd.DataFrame()
    df_maa = pd.DataFrame()

    df_ck3_cultures = culture_keys
    df_ck3_maa = maa_keys
    df_attila = attila_keys
    df_ck3_titles = title_keys

    cultures_rows = []
    maa_rows = []

    # CW MAPPERS
    if os.listdir(MAPPER_DIR):
        print()
        print(f'== Found mapping directories: {os.listdir(MAPPER_DIR)} ==')
        print()
    else:
        print()
        print(f'== No CW mapping files were found in {MAPPER_DIR}... ==')
        sys.exit(1) # Exit with an error

    for mapping in os.listdir(MAPPER_DIR):
            cultures = os.path.join(MAPPER_DIR,mapping,'Cultures')
            factions = os.path.join(MAPPER_DIR,mapping,'Factions')
            titles = os.path.join(MAPPER_DIR,mapping,'Titles')
            os.makedirs(os.path.join(REPORT_OUTPUT_DIR,mapping),exist_ok=True) # Ensure the report directory exists

            # Processing loop for cultures
            if os.path.exists(cultures):
                print(f'== ✝ Cultures found in {mapping}. ==')
                for x in os.listdir(cultures):
                    if x.endswith('.xml'):
                        print(f'// ✝ Processing {x}.')
                        cultures_tree = ET.parse(os.path.join(cultures,x))
                        cultures_root = cultures_tree.getroot()
                        for cultures_parent in cultures_root:
                            for cultures_child in cultures_parent:
                                # Update rows
                                cultures_rows.append({
                                    "cw_category": 'Culture',
                                    "ck3_culture": cultures_child.attrib.get('name'),
                                    "cw_culture": cultures_child.attrib.get('faction'),
                                    "cw_source_file": x,
                                    "cw_source_folder": mapping
                                })              

            # Processing loop for maa, factions
            if os.path.exists(factions):
                print(f'== ⚔ Factions found in {mapping}. ==')
                for x in os.listdir(factions):
                    if x.endswith('.xml'):
                        print(f'// ⚔ Processing {x}.')
                        faction_tree = ET.parse(os.path.join(factions,x))
                        faction_root = faction_tree.getroot()
                        for faction_parent in faction_root:
                            for faction_child in faction_parent:
                                # Update rows
                                maa_rows.append({
                                    "cw_type": faction_child.tag,
                                    "cw_category": 'Faction',
                                    "cw_maa_parent": faction_parent.attrib.get('name'),
                                    "cw_maa": faction_child.attrib.get('type'),
                                    "attila_map_key": faction_child.attrib.get('key'),
                                    "cw_source_file": x,
                                    "cw_source_folder": mapping
                                })              
                    
            # Processing loop for maa, titles
            if os.path.exists(titles):
                print(f'== ♠ Titles found in {mapping}. ==')
                for x in os.listdir(titles):
                    if x.endswith('.xml'):
                        print(f'// ♠ Processing {x}.')
                        titles_tree = ET.parse(os.path.join(titles,x))
                        titles_root = titles_tree.getroot()
                        for titles_parent in titles_root:
                            for titles_child in titles_parent:
                                # Update rows
                                maa_rows.append({
                                    "cw_type": titles_child.tag,
                                    "cw_category": 'Title',
                                    "cw_maa_parent": titles_parent.attrib.get('name'),
                                    "cw_maa": titles_child.attrib.get('type'),
                                    "attila_map_key": titles_child.attrib.get('key'),
                                    "cw_source_file": x,
                                    "cw_source_folder": mapping
                                })     

            # Append processing results to df
            df_cultures = pd.concat([df_cultures,pd.DataFrame(cultures_rows)],ignore_index=True)
            df_maa = pd.concat([df_maa,pd.DataFrame(maa_rows)],ignore_index=True)

            # Join df from CW and Attila/CK3, and produce reports
            df_maa = pd.merge(df_maa,df_attila, on='attila_map_key', how ='left')
            df_maa.to_csv(os.path.join(REPORT_OUTPUT_DIR,mapping,f'{mapping}_cw_maa.csv'))
            print(f'// 🕮  Report produced for man-at-arms files for mapper: {mapping}.')

            df_cultures = pd.merge(df_cultures,df_ck3_cultures, on='ck3_culture', how ='left')
            df_cultures.to_csv(os.path.join(REPORT_OUTPUT_DIR,mapping,f'{mapping}_cw_cultures.csv'))
            print(f'// 🕮  Report produced for culture files for mapper: {mapping}.')

            df_cultures = pd.DataFrame()
            df_maa = pd.DataFrame()
            cultures_rows = []
            maa_rows = []

    df_attila.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv'))
    df_ck3_cultures.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures_keys.csv'))
    df_ck3_maa.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa_keys.csv'))
    if df_ck3_titles is not None and not df_ck3_titles.empty:
        df_ck3_titles.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_title_keys.csv'))
        print(f'Report produced for source title key files.')
    print(f'Report produced for source key files.')

def summary():
    output_columns = 4
    
    ck3_culture_key_file = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures_keys.csv')
    ck3_maa_key_file = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa_keys.csv')
    attila_key_file = os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv')

    with open('summary_log.txt', 'w', encoding="utf-8-sig") as sum_f:
        # Check if reports exists
        print(ASCII, file=sum_f)
        if os.listdir(REPORT_OUTPUT_DIR):
            print(f'== Found reports in report directory ==', file=sum_f)
            print('==================================================', file=sum_f)
        else:
            print(f'== No reports were found in {REPORT_OUTPUT_DIR}. No summary can be made until reports are produced based on your CK3/Attila install... ==', file=sum_f)
            print('', file=sum_f)
            # Could potentially in future add a functionality to run a report from here.
            sys.exit(1) # Exit with an error        

        for mapping in os.listdir(REPORT_OUTPUT_DIR):
            map_folder = os.path.join(REPORT_OUTPUT_DIR,mapping)

            # Key things that need to be summarised:
            # - Whether the mapper has all the MAA and cultures from Vanilla or MOD, based on the mod_config.json
            # - Whether the mapper has a valid attila unit key
            
            # Check if mapping directory, and load map to mod config
            if os.path.isdir(map_folder):
                print('◆ Mapper: '+mapping, file=sum_f)
                target_config = get_config(mapping)
                
                source_ids = []
                for mods in target_config:
                    id = str(mods[1])
                    source_ids.append(id)

                print('', file=sum_f)
                print(f'\t🛠 Sources: {target_config}', file=sum_f)

                # Set up list of expected culture and MAA keys
                expected_culture_keys = []
                expected_maa_keys = []
                source_attila_keys = []
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
                
                missing_mods = set(source_ids) - set(found_mods)
                if missing_mods:
                    print(f'\t↳ ⚠ Sources missing: {missing_mods}\n\tMissing sources can cause inaccuracies when checking for keys', file=sum_f)
                    print('', file=sum_f)
                else:
                    print(f'\t↳ ✓ No missing sources', file=sum_f)
                    print('', file=sum_f)

                # Compare reports to expected keys
                files = os.listdir(map_folder)
                if files:
                    for file in files:
                        missing_keys = []
                        missing_attila_keys = []
                        # CULTURES
                        if file.endswith('cultures.csv'):
                            print(f'\t⚑ Cultures: ', file=sum_f)
                            file_path = os.path.join(map_folder,file)

                            with open(file_path, 'r') as f:
                                report_data = csv.DictReader(f)
                                expected_cultures = [d["ck3_culture"] for d in expected_culture_keys]
                                report_cultures = [d["ck3_culture"] for d in report_data]
                                missing_keys = sorted(list(set(expected_cultures) - set(report_cultures)))
                        
                        # MAN AT ARMS
                        if file.endswith('maa.csv'):
                            print(f'\t⚔ ManAtArms: ', file=sum_f)
                            file_path = os.path.join(map_folder,file)

                            with open(file_path, 'r') as f:
                                report_data = list(csv.DictReader(f))
                                expected_maa = [d["ck3_maa"] for d in expected_maa_keys]
                                report_maa = [d["cw_maa"] for d in report_data]
                                missing_keys = sorted(set(expected_maa) - set(report_maa))

                                report_attila_keys = [d["attila_map_key"] for d in report_data]
                                expected_attila_keys = [d["attila_map_key"] for d in source_attila_keys]
                                missing_attila_keys = sorted(set(report_attila_keys)-set(expected_attila_keys))

                        if expected_culture_keys and expected_maa_keys:
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
                        else:
                            print(f'\t↳ ⚠ Missing all source files for keys: {file}. Skipping...', file=sum_f)
                            print('', file=sum_f)

                else:
                    print(f'↳ ⚠ No reports were found in {map_folder}', file=sum_f)
                print('==================================================', file=sum_f)