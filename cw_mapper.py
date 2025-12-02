import os
import re
import sys
import webbrowser
import xml.etree.ElementTree as ET

from io import StringIO

import configparser
import pandas as pd

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

CK3_MODS = {
            'Africa Plus' : '3401420817',
            'Buffed Mongol Invasion' : '2796578078',
            'Cultures Expanded' : '2829397295',
            'More Traditions v2' : '2893793966',
            'Muslim Enhancements' : '2241658518',
            'RICE' : '2273832430',
            'Fallen Eagle' : '2243307127',
            'Realms in Exile' : '2291024373',
            'AGOT' : '2962333032'
        }
os.chdir(WORKING_DIR)

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
        print(f"== Could not find GamePaths.ini! Please ensure you place the cw_mapper folder in the 'tools' folder of the Crusader Wars directory.")
        input(f"Press Enter to quit...")
        exit(1) # Exit with an error

    ck3_dir_path = os.path.dirname(os.path.dirname(config.get('GamePaths','CRUSADERKINGS3')))
    if ck3_dir_path == "":
        print(f"== The Crusader Kings 3 directory path was not found! Please ensure you configure your game paths in Crusader Wars.")
        input("Press Enter to quit...")
        exit(1) # Exit with an error
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
        input("Press Enter to quit...")
        
        # Auto open readme.txt upon close
        webbrowser.open("readme.txt")
        exit(1) # Exit with an error
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

    # CK3 + MODS CULTURE KEYS
    while True:
        key_input = input("Enter the name of any additional CK3 mods you wish to check (or press Enter to continue): ")
        if key_input.strip() == '':
            print('No further mod input.')
            break
        value_input = input(f"Enter the mod steam id for '{key_input}': ")
        CK3_MODS[key_input] = value_input
    print()
    print(f'== CK3 mods to check: {CK3_MODS} ==')
    print()
    
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

            culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
            for culture in culture_txt:
                ck3_rows.append({
                    "ck3_culture":culture,
                    "ck3_source_file":source_name,
                    "ck3_source":"CK3"
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

            culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
            for culture in culture_txt:
                ck3_rows.append({
                    "ck3_culture":culture,
                    "ck3_source_file":source_name,
                    "ck3_source":"CK3"
                })

    # Obtain additional cultures from CK3 mods
    for folders in os.scandir(ck3_mod_dir):
        if folders.name in CK3_MODS.values():
            ck3_mod_culture_dir = os.path.join(ck3_mod_dir,folders.name,'common','culture','cultures')
            ck3_mod_culture_dir_hybrid = os.path.join(ck3_mod_dir,folders.name,'common','culture','creation_names')
            mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)] + ', ' + folders.name
            print(f'== Finding mod culture files in: {folders.name} ==')

            if os.path.exists(ck3_mod_culture_dir):
                for file in os.listdir(ck3_mod_culture_dir):
                    if file.endswith('.txt'):
                        source_file = os.path.join(ck3_mod_culture_dir,file)
                        source_name = os.path.basename(source_file)

                        with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                            data = culture_txt_file.read()

                        culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                        for culture in culture_txt:
                            ck3_rows.append({
                                "ck3_culture":culture,
                                "ck3_source_file":source_name,
                                "ck3_source": mod_name
                            })

            # Obtain additional cultures from hybrid and creation names                
            if os.path.exists(ck3_mod_culture_dir_hybrid):
                for file in os.listdir(ck3_mod_culture_dir_hybrid):
                    if file.endswith('.txt'):
                        source_file = os.path.join(ck3_mod_culture_dir_hybrid,file)
                        source_name = os.path.basename(source_file)

                        with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                            data = culture_txt_file.read()

                        culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                        for culture in culture_txt:
                            ck3_rows.append({
                                "ck3_culture":culture,
                                "ck3_source_file":source_name,
                                "ck3_source":mod_name
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
                    "ck3_source":"CK3"
                })

    # Obtain additional maa from CK3 mods
    for folders in os.scandir(ck3_mod_dir):      
        if folders.name in CK3_MODS.values():
            ck3_mod_maa_dir = os.path.join(ck3_mod_dir,folders.name,'common','men_at_arms_types')
            mod_name = list(CK3_MODS.keys())[list(CK3_MODS.values()).index(folders.name)] + ', ' + folders.name
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
                                "ck3_source":mod_name
                            })

    df_ck3_maa = pd.concat([df_ck3_maa,pd.DataFrame(ck3_rows)],ignore_index=True)

    return df_ck3_cultures, df_ck3_maa, df_attila

def mapping_validation(culture_keys, maa_keys, attila_keys):
    # == BEGIN MAPPING ==
    # Declare data frame for processed cw mapping
    df_cultures = pd.DataFrame()
    df_maa = pd.DataFrame()

    df_ck3_cultures = culture_keys
    df_ck3_maa = maa_keys
    df_attila = attila_keys

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
        input("Press Enter to quit...")
        exit(1) # Exit with an error

    for mapping in os.listdir(MAPPER_DIR):
            cultures = os.path.join(MAPPER_DIR,mapping,'Cultures')
            factions = os.path.join(MAPPER_DIR,mapping,'Factions')
            titles = os.path.join(MAPPER_DIR,mapping,'Titles')

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
                                    "cw_unit_parent": faction_parent.attrib.get('name'),
                                    "cw_unit": faction_child.attrib.get('type'),
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
                                    "cw_unit_parent": titles_parent.attrib.get('name'),
                                    "cw_unit": titles_child.attrib.get('type'),
                                    "attila_map_key": titles_child.attrib.get('key'),
                                    "cw_source_file": x,
                                    "cw_source_folder": mapping
                                })     

    # Append processing results to df
    df_cultures = pd.concat([df_cultures,pd.DataFrame(cultures_rows)],ignore_index=True)
    df_maa = pd.concat([df_maa,pd.DataFrame(maa_rows)],ignore_index=True)

    # Join df from CW and Attila/CK3, and produce reports
    df_maa = pd.merge(df_maa,df_attila, on='attila_map_key', how ='left')
    df_maa.to_csv(os.path.join(REPORT_OUTPUT_DIR,'report_cw_maa.csv'))
    print(f'Report produced for man-at-arms files.')

    df_cultures = pd.merge(df_cultures,df_ck3_cultures, on='ck3_culture', how ='left')
    df_cultures.to_csv(os.path.join(REPORT_OUTPUT_DIR,'report_cw_cultures.csv'))
    print(f'Report produced for culture files.')

    df_attila = pd.merge(df_attila,df_maa, on='attila_map_key', how ='left', suffixes=('','df_maa'))
    df_attila['used_in_cw'] = df_attila['cw_unit'].notna()
    df_attila = pd.DataFrame(df_attila[['attila_map_key','attila_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
    df_attila.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv'))

    df_ck3_cultures = pd.merge(df_ck3_cultures,df_cultures, on='ck3_culture', how ='left', suffixes=('','df_cultures'))
    df_ck3_cultures['used_in_cw'] = df_ck3_cultures['cw_culture'].notna()
    df_ck3_cultures = pd.DataFrame(df_ck3_cultures[['ck3_culture','ck3_source_file','ck3_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
    df_ck3_cultures.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures.csv'))

    df_ck3_maa = pd.merge(df_ck3_maa,df_maa, left_on='ck3_maa', right_on='cw_unit', how ='left', suffixes=('','df_maa'))
    df_ck3_maa['used_in_cw'] = df_ck3_maa['cw_unit'].notna()
    df_ck3_maa = pd.DataFrame(df_ck3_maa[['ck3_maa','ck3_source_file','ck3_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
    df_ck3_maa.to_csv(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa.csv'))
    print(f'Report produced for source files.')

    input("Press Enter to quit...")
    exit(0) # Exit as a success