import os
import ast
import json
import xml.etree.ElementTree as ET


from typing import List, Tuple
from xml.dom import minidom

CONFIG_DIR = os.path.join('config')
MAP_CONFIG = os.path.join(CONFIG_DIR,'mapper_config.json')
CUSTOM_MAPPER_DIR = 'custom_mappers'

DEFAULT_CONFIG_PATH = os.path.join('config',"default.json")
with open(DEFAULT_CONFIG_PATH, 'r') as f:
    DEFAULT_CONFIG = json.load(f)

def init_map_config():
    # Initialise the default config, if none present
    os.makedirs(CONFIG_DIR,exist_ok=True)
    if not os.path.exists(MAP_CONFIG):
        try:
            with open(MAP_CONFIG, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
            print(f'Initialised mapper config at {MAP_CONFIG}')
        except Exception as e:
            print('Error: {e}')
            exit(1) # Exit with an error
        
def get_config(mapping):
    vanilla_mappers = ["OfficialCW_EarlyMedieval_919Mod", "OfficialCW_HighMedieval_MK1212Mod","OfficialCW_LateMedieval_MK1212Mod","OfficialCW_Rennaisance_MK1212Mod"]
    target_config = []
    if mapping in vanilla_mappers:
        with open(MAP_CONFIG, 'r') as f:
            config = json.load(f)
            target_config = config.get("CW_VANILLA")
    else:
       with open(MAP_CONFIG, 'r') as f:
            config = json.load(f)
            target_config = config.get(mapping)
    return target_config

def add_map_config(mapper_key, mapper_config: List[Tuple[str,int]]):
    # Open the config, and initialise if missing
    try:
        with open (MAP_CONFIG, 'r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print(f'WARNING: {e}, config file not found in {CONFIG_DIR}. Initialising config and trying again')
        print(f'Initialising {MAP_CONFIG} with defaults')
        init_map_config()
        add_map_config()
    except json.JSONDecodeError as e:
        print(f'ERROR: {e}, the file {MAP_CONFIG} exists but is not valid JSON or is corrupt')
        exit(1) # Exit with an error

    if mapper_key not in data:
        data[mapper_key] = mapper_config
    else:
        existing_config = set((tuple(item)) for item in data[mapper_key])
        for item in mapper_config:
            if tuple(item) not in existing_config:
                data[mapper_key].append(item)
                existing_config.add(tuple(item)) # Add to existing set
    
    try:
        with open(MAP_CONFIG, 'w') as f:
            json.dump(data, f, indent=4)
        print(f'Successfully updated {MAP_CONFIG} with {mapper_key}')
    except Exception as e:
        print(f'Error: {e}, error occurred while writing to config file')

def import_xml(import_folder):
    # Format faction mapping: {(ck3_maa, faction): [attila_unit]} | {tuple: [value]}
    imported_mappings = {}
    # Format heritage mapping: {heritage(faction,[culture[faction]]} | {key(value,list[value])}
    imported_heritage_mappings = {}
    # Import folders and important files
    import_cultures = os.path.join(import_folder,'Cultures')
    import_factions = os.path.join(import_folder,'Factions')
    import_titles = os.path.join(import_folder,'Titles')
    import_mods = os.path.join(import_folder,'Mods.xml')
    import_tag = os.path.join(import_folder,'tag.txt')
    import_time = os.path.join(import_folder,'Time Period.xml')

    # Cultures
    for file in os.listdir(import_cultures):
        if file.endswith('.xml'):
            file_path = os.path.join(import_cultures,file)
            tree = ET.parse(file_path)
            root = tree.getroot()
            for heritage in root:
                heritage_name = heritage.get('name')
                heritage_faction = heritage.get('faction')
                imported_heritage_mappings[(heritage_name,'PARENT_KEY')] = heritage_faction
                for culture in heritage:
                    culture_name = culture.get('name')
                    culture_faction = culture.get('faction')
                    imported_heritage_mappings[(heritage_name,culture_name)] = culture_faction

    # Factions
    for file in os.listdir(import_factions):
        if file.endswith('.xml'):
            file_path = os.path.join(import_factions,file)
            tree = ET.parse(file_path)
            root = tree.getroot()
            for faction in root:
                faction_name = faction.get('name')
                for key in faction:
                    if key.tag == 'MenAtArm':
                        maa_key = key.get('type')
                        attila_key = key.get('key')
                        size = key.get('max')
                        imported_mappings[(maa_key, faction_name)]= [attila_key, size]
    
    return imported_mappings, imported_heritage_mappings
                        
def export_xml(file, NON_MAA_KEYS, tag):
    file_name, _ = os.path.splitext(os.path.split(file)[1])
    export_dir = os.path.join(CUSTOM_MAPPER_DIR, 'export', file_name)
    os.makedirs(export_dir,exist_ok=True)

    # Define export folders and files
    cultures_dir = os.path.join(export_dir, 'Cultures')
    os.makedirs(cultures_dir,exist_ok=True)
    factions_dir = os.path.join(export_dir, 'Factions')
    os.makedirs(factions_dir,exist_ok=True)
    titles_dir = os.path.join(export_dir, 'Titles')
    os.makedirs(titles_dir,exist_ok=True)
    export_mods = os.path.join(export_dir,'Mods.xml')
    export_tag = os.path.join(export_dir,'tag.txt')
    export_time = os.path.join(export_dir,'Time Period.xml')

    seperator = ','
    with open(file, 'r', encoding='utf-8-sig') as f:
        export_dict = json.load(f)
        faction_data = export_dict.get('FACTIONS_AND_MAA',{})
        heritage_data = export_dict.get('HERITAGES_AND_CULTURES', {})

        # Load mappings for export
        loaded_faction_mapping = {
            tuple(k.split(seperator)):v
            for k, v in faction_data.items()
        }
        loaded_heritage_mapping = {
            tuple(k.split(seperator)):v[0]
            for k, v in heritage_data.items()
        }

    def sort_factions(item):
        if item == 'DEFAULT' or item == 'Default':
            priority = 0 
        else:
            priority = 1
        name = item
        return priority, name

    def sort_xml_elements(child):
        tag = child.tag

        if tag == 'MenAtArm':
            maa = child.get('type') # type, being MAA key
        else:
            maa = 'ZZZ'

        if tag == 'General':
            priority = 0
        elif tag == 'Knights':
            priority = 1
        elif tag == 'Levies':
            priority = 2
        else:
            priority = 3
    
        secondary_key = maa
        return priority, secondary_key

    # Export CULTURE mapping to XML file
    c_output = os.path.join(cultures_dir,file_name+'_Cultures.xml')
    c_root = ET.Element("Cultures")
    for key, value in loaded_heritage_mapping.items():
        if key[1] == 'PARENT_KEY': # I.e. the heritage head
            heritage = ET.SubElement(c_root, "Heritage", name=key[0], faction=value)
        else:
            culture = ET.SubElement(heritage, "Culture", name=key[1], faction=value)
    
    c_tree = ET.ElementTree(c_root)
    try:
        # Use ET.indent for cleaner output in Python 3.9+
        ET.indent(c_tree, space="\t", level=0)
    except AttributeError:
        # Fallback for older Python versions
        pass
    c_tree.write(c_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Export FACTION mapping to XML file
    f_output = os.path.join(factions_dir,file_name+'_Units.xml')
    f_root = ET.Element("FactionsGroups")
    factions = sorted(set([key[1] for key in loaded_faction_mapping.keys()]),key=sort_factions)
    for fac in factions:
        faction = ET.SubElement(f_root, "Faction", name=fac)
        filtered_items = {
            key:value
            for key, value in loaded_faction_mapping.items() if key[1] == fac
            }
        for key, value in filtered_items.items():
                if key[0] in NON_MAA_KEYS: #i.e. a CW key, General, Knight, or a levy unit
                    if key[0] == 'GENERAL':
                        general = ET.SubElement(faction, "General", key=value[0])
                    if key[0] == 'KNIGHTS':
                        knights = ET.SubElement(faction, "Knights", key=value[0])
                    else: # Levies are the only remaining possible type
                        levy = ET.SubElement(faction,'Levies', porcentage='0',key=value[0], max='LEVY')
                    pass
                else:
                    maa = ET.SubElement(faction, "MenAtArm", type=key[0], key=value[0], max=value[1])

        # Sort XML elements within faction tree
        faction[:] = sorted(
            faction,
            key=sort_xml_elements
        )
    f_tree = ET.ElementTree(f_root)
    try:
        # Use ET.indent for cleaner output in Python 3.9+
        ET.indent(f_tree, space="\t", level=0)
    except AttributeError:
        # Fallback for older Python versions
        pass
    f_tree.write(f_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Create tag file
    if not tag:
        tag = file_name
    with open(export_tag, 'w', encoding='utf-8-sig') as f:
        f.write(tag)

    return export_dir