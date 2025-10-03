import configparser
from io import StringIO
import os
import re
import sys
import xml.etree.ElementTree as ET

import pandas as pd

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Identify working directories
working_dir = application_path
attila_export_dir = os.path.join(working_dir, 'attila_exports','db','main_units_tables')
mapper_dir = '../../unit mappers/attila'
settings_dir = '../../data/settings'

# Handle improper .ini structure and pass through configparser
settings_paths_file = os.path.join(settings_dir,'GamePaths.ini')
if os.path.exists(settings_paths_file):
    with open (settings_paths_file,'r') as f:
        content = f.read()
        settings_content = '[GamePaths]\n' + content.replace('::','=')
        settings_file = StringIO(settings_content)
    config = configparser.ConfigParser()
    config.read_file(settings_file)
else:
    print(f"== Could not find GamePaths.ini! Please ensure you place the cw_mapping_validator folder in the 'tools' folder of the Crusader Wars directory.")
    input(f"Press Enter to quit...")
    quit()

os.chdir(working_dir)
if os.path.exists(attila_export_dir):
    if not any(file.endswith('.tsv') for file in os.listdir(attila_export_dir)):
        print(f'== Mapping directory exists, but no .tsv mapping were files found! ==')
        print(f'Please read the readme.txt!')
        input("Press Enter to quit...")
        quit()
    else:
        print(f'== Mapping files found! ==')
else:
    print(f'== No attila export files directory found in attila_exports. Please ensure you export .tsv files from RPFM/PFM to "attila_exports/db/main_units_tables" ==')
    print(f'Please read the readme.txt!')
    input("Press Enter to quit...")
    quit()

# Declare data frame for Attila unit export mapping, and merge
df_attila = pd.DataFrame()
for file in os.listdir(attila_export_dir):
    if file.endswith('.tsv'):
        # Define source of file if ends with .tsv
        source_file = os.path.join(attila_export_dir,file)
        source_name = os.path.basename(source_file)
                
        df = pd.read_csv(source_file, header=None, names=['attila_map_key']
                         ,sep='\t', usecols=[0])
        df = df.iloc[2:]
        df['attila_source'] = source_name
        # Append loop
        df_attila = pd.concat([df_attila, df])

print()
print(f'== Found mapping directories: {os.listdir(mapper_dir)} ==')
print()

# Declare directories and data frame for cultures from Crusader Kings 3 and obtain cultures from Crusader Kings installation, and merge
ck3_dir_path = os.path.dirname(os.path.dirname(config.get('GamePaths','CRUSADERKINGS3')))
if ck3_dir_path == "":
    print(f"== The Crusader Kings 3 directory path was not found! Please ensure you configure your game paths in Crusader Wars.")
    input("Press Enter to quit...")
    quit()

ck3_mod_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(config.get('GamePaths','CRUSADERKINGS3')))))),'steamapps','workshop','content','1158310')
ck3_mods = {
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
while True:
    key_input = input("Enter any additional CK3 mods you wish to check (or type 'stop' to finish): ")
    if key_input.lower() == 'stop':
        print('No further mod input.')
        break
    value_input = input(f"Enter the mod steam id for '{key_input}': ")
    ck3_mods[key_input] = value_input
print()
print(f'== CK3 mods to check: {ck3_mods} ==')
print()

df_ck3_cultures = pd.DataFrame() 
ck3_culture_dir = os.path.join(ck3_dir_path,'game','common','culture','cultures')
ck3_rows = []
print(f'== Found CK3 culture files: {os.listdir(ck3_culture_dir)} ==')
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
ck3_culture_dir = os.path.join(ck3_dir_path,'game','common','culture','creation_names')
print(f'== Found additional CK3 culture files: {os.listdir(ck3_culture_dir)} ==')
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

# Obtain additional cultures from CK3 mods
for folders in os.scandir(ck3_mod_dir):
    if folders.name in ck3_mods.values():
        print(f'== Mod files found in: {folders.name} ==')
        for file in os.listdir(os.path.join(ck3_mod_dir,folders.name,'common','culture','cultures')):
            if file.endswith('.txt'):
                source_file = os.path.join(ck3_mod_dir,folders.name,'common','culture','cultures',file)
                source_name = os.path.basename(source_file)

                with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                    data = culture_txt_file.read()

                culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                for culture in culture_txt:
                    ck3_rows.append({
                        "ck3_culture":culture,
                        "ck3_source_file":source_name,
                        "ck3_source":list(ck3_mods.keys())[list(ck3_mods.values()).index(folders.name)] + ', ' + folders.name
                    })

        for file in os.listdir(os.path.join(ck3_mod_dir,folders.name,'common','culture','creation_names')):
            if file.endswith('.txt'):
                source_file = os.path.join(ck3_mod_dir,folders.name,'common','culture','creation_names',file)
                source_name = os.path.basename(source_file)

                with open (source_file, 'r', encoding="utf-8-sig") as culture_txt_file:
                    data = culture_txt_file.read()

                culture_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                for culture in culture_txt:
                    ck3_rows.append({
                        "ck3_culture":culture,
                        "ck3_source_file":source_name,
                        "ck3_source":list(ck3_mods.keys())[list(ck3_mods.values()).index(folders.name)] + ', ' + folders.name
                    })

df_ck3_cultures = pd.concat([df_ck3_cultures,pd.DataFrame(ck3_rows)],ignore_index=True)

# Declare data frame for maa from Crusader Kings 3 and obtain maa from Crusader Kings installation, and merge
df_ck3_maa = pd.DataFrame() 
ck3_maa_dir = os.path.join(ck3_dir_path,'game','common','men_at_arms_types')
ck3_rows = []
print()
print(f'== Found CK3 maa files: {os.listdir(ck3_maa_dir)} ==')
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
    if folders.name in ck3_mods.values():
        for file in os.listdir(os.path.join(ck3_mod_dir,folders.name,'common','men_at_arms_types')):
            if file.endswith('.txt'):
                source_file = os.path.join(ck3_mod_dir,folders.name,'common','men_at_arms_types',file)
                source_name = os.path.basename(source_file)

                with open (source_file, 'r', encoding="utf-8-sig") as maa_txt_file:
                    data = maa_txt_file.read()

                maa_txt = re.findall(r"^(\w+)\s*=", data, re.M)
                for maa in maa_txt:
                    ck3_rows.append({
                        "ck3_maa":maa,
                        "ck3_source_file":source_name,
                        "ck3_source":list(ck3_mods.keys())[list(ck3_mods.values()).index(folders.name)] + ', ' + folders.name
                    })

df_ck3_maa = pd.concat([df_ck3_maa,pd.DataFrame(ck3_rows)],ignore_index=True)

# == BEGIN MAPPING ==
# Declare data frame for processed cw mapping
df_cultures = pd.DataFrame()
cultures_rows = []
df_maa = pd.DataFrame()
maa_rows = []

for mapping in os.listdir(mapper_dir):
        cultures = os.path.join(mapper_dir,mapping,'Cultures')
        factions = os.path.join(mapper_dir,mapping,'Factions')
        titles = os.path.join(mapper_dir,mapping,'Titles')

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
df_maa.to_csv('report_cw_maa.csv')
print(f'Report produced for man-at-arms files.')

df_cultures = pd.merge(df_cultures,df_ck3_cultures, on='ck3_culture', how ='left')
df_cultures.to_csv('report_cw_cultures.csv')
print(f'Report produced for culture files.')

df_attila = pd.merge(df_attila,df_maa, on='attila_map_key', how ='left', suffixes=('','df_maa'))
df_attila['used_in_cw'] = df_attila['cw_unit'].notna()
df_attila = pd.DataFrame(df_attila[['attila_map_key','attila_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
df_attila.to_csv('source_attila_keys.csv')

df_ck3_cultures = pd.merge(df_ck3_cultures,df_cultures, on='ck3_culture', how ='left', suffixes=('','df_cultures'))
df_ck3_cultures['used_in_cw'] = df_ck3_cultures['cw_culture'].notna()
df_ck3_cultures = pd.DataFrame(df_ck3_cultures[['ck3_culture','ck3_source_file','ck3_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
df_ck3_cultures.to_csv('source_ck3_cultures.csv')

df_ck3_maa = pd.merge(df_ck3_maa,df_maa, left_on='ck3_maa', right_on='cw_unit', how ='left', suffixes=('','df_maa'))
df_ck3_maa['used_in_cw'] = df_ck3_maa['cw_unit'].notna()
df_ck3_maa = pd.DataFrame(df_ck3_maa[['ck3_maa','ck3_source','used_in_cw']]).drop_duplicates().reset_index(drop=True)
df_ck3_maa.to_csv('source_ck3_maa.csv')
print(f'Report produced for source files.')

input("Press Enter to quit...")
quit()