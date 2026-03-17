'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import json
import re
import tempfile
import xml.etree.ElementTree as ET

from constants import (
    CONFIG_DIR, MAP_CONFIG, DEFAULT_CONFIG_PATH, CUSTOM_MAPPER_DIR,
    NON_MAA_KEYS, TITLE_NON_MAA_KEYS,
)

_DEFAULT_CONFIG = None

def _get_default_config():
    global _DEFAULT_CONFIG
    if _DEFAULT_CONFIG is None:
        with open(DEFAULT_CONFIG_PATH, 'r') as f:
            _DEFAULT_CONFIG = json.load(f)
    return _DEFAULT_CONFIG

def init_map_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(MAP_CONFIG):
        try:
            with open(MAP_CONFIG, 'w') as f:
                json.dump(_get_default_config(), f, indent=4)
            print(f'Initialised mapper config at {MAP_CONFIG}')
        except OSError as e:
            raise OSError(f'Failed to initialize mapper config at {MAP_CONFIG}: {e}') from e

def get_config(mapping):
    target_config = []
    with open(MAP_CONFIG, 'r') as f:
        config = json.load(f)
        target_config = config.get(mapping)

    if not target_config:
        with open(MAP_CONFIG, 'r') as f:
            config = json.load(f)

        config[mapping] = []

        with open(MAP_CONFIG, 'w') as f:
            json.dump(config, f, indent=4)
        target_config = config.get(mapping)

    return target_config

def get_full_config():
    """Load the entire mod_config.json and return as dict."""
    if not os.path.exists(MAP_CONFIG):
        init_map_config()
    with open(MAP_CONFIG, 'r') as f:
        return json.load(f)

def get_ck3_mods_from_config():
    """Load mod_config.json and return a flat {mod_name: mod_id} dict."""
    data = get_full_config()
    ck3_mods = {}
    for map_entry in data.items():
        for mod in map_entry[1]:
            mod_name = mod[0]
            mod_id = str(mod[1])
            ck3_mods[mod_name] = mod_id
    return ck3_mods

def add_map_config(mapper_name, mods):
    try:
        with open(MAP_CONFIG, 'r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print(f'WARNING: {e}, config file not found in {CONFIG_DIR}. Initialising config and trying again')
        print(f'Initialising {MAP_CONFIG} with defaults')
        init_map_config()
        add_map_config(mapper_name, mods)
        return
    except json.JSONDecodeError as e:
        raise ValueError(f'The file {MAP_CONFIG} exists but is not valid JSON or is corrupt: {e}') from e

    cur_CK3_mods = [v for k, v in mods.items() if k == 'CK3']
    new_ck3_mods = []
    if cur_CK3_mods:
        for v in cur_CK3_mods[0]:
            try:
                name, id = v.split(':', 1)
                mod = tuple((name, int(id)))
            except (ValueError, TypeError):
                print(f'WARNING: Skipping malformed CK3 mod entry: {v} (expected Name:ID format)')
                continue
            new_ck3_mods.append(mod)

    data[mapper_name] = new_ck3_mods

    try:
        with open(MAP_CONFIG, 'w') as f:
            json.dump(data, f, indent=4)
        print(f'Successfully updated {MAP_CONFIG} with {mapper_name}')
    except Exception as e:
        print(f'Error: {e}, error occurred while writing to config file')

def resolve_import_mods(import_folder_name, imported_mods):
    """Look up CK3 mods from config for an imported mapper name.
    Returns the updated mods dict with CK3 key populated, and whether a match was found."""
    config = get_full_config()
    ck3_mods_match = [v for k, v in config.items() if k == import_folder_name]
    imported_mods['CK3'] = []
    found = bool(ck3_mods_match)
    if found:
        ck3_mods = ck3_mods_match[0]
        for mod in ck3_mods:
            imported_mods['CK3'] += [mod[0] + ':' + str(mod[1])]
    return imported_mods, found

# ============================================================
# Save / Load mapper (moved from main.py mapping_window scope)
# ============================================================

def save_mapper(name, faction_mapping, heritage_mapping, mods, title_mapping=None, title_names=None):
    output_path = os.path.join(CUSTOM_MAPPER_DIR, f'{name}.txt')
    os.makedirs(CUSTOM_MAPPER_DIR, exist_ok=True)
    seperator = ','
    save_format = {
        'FACTIONS_AND_MAA': {
            seperator.join(k): v
            for k, v in faction_mapping.items()
        },
        'HERITAGES_AND_CULTURES': {
            seperator.join(k): [v]
            for k, v in heritage_mapping.items()
        },
        'TITLES_AND_MAA': {
            seperator.join(k): v
            for k, v in (title_mapping or {}).items()
        },
        'TITLE_NAMES': dict(title_names or {}),
        'MODS': dict(mods),
    }
    fd, tmp_path = tempfile.mkstemp(dir=CUSTOM_MAPPER_DIR, suffix='.tmp', prefix='.save_')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8-sig') as f:
            json.dump(save_format, f, indent=4)
        os.replace(tmp_path, output_path)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise

def load_mapper(file, maa_source_keys, attila_source_keys, cultures_source_keys, title_source_keys):
    """Load a mapper .txt (JSON) file and validate keys against source data.

    Args:
        file: Path to the mapper .txt file
        maa_source_keys: List of {'ck3_maa':..., 'ck3_source':...} dicts
        attila_source_keys: List of {'attila_map_key':..., 'attila_source':...} dicts
        cultures_source_keys: List of {'ck3_culture':..., 'heritage':..., 'ck3_source':...} dicts
        title_source_keys: List of {'title_key':..., 'title_rank':..., 'ck3_source':...} dicts

    Returns:
        Tuple of (faction_mapping, heritage_mapping, mods, has_diff, missing_keys,
                  title_mapping, title_names)
    """
    diff_message = ''
    maa_diff = 0
    attila_diff = 0
    heritage_diff = 0
    culture_diff = 0
    overall_diff = 0
    seperator = ','
    with open(file, 'r', encoding='utf-8-sig') as f:
        loaded_data = json.load(f)

    faction_data = loaded_data.get('FACTIONS_AND_MAA', {})
    heritage_data = loaded_data.get('HERITAGES_AND_CULTURES', {})
    mod_data = loaded_data.get('MODS', {})
    missing_keys = []

    loaded_faction_mapping = {
        tuple(k.split(seperator, 1)): v
        for k, v in faction_data.items()
    }
    for k in loaded_faction_mapping.keys():
        maa = k[0]
        if maa not in NON_MAA_KEYS and maa not in [key['ck3_maa'] for key in maa_source_keys]:
            maa_diff = 1
            if not re.search(r'^LEVY-', maa):
                missing_keys.append([maa, 'CK3 ManAtArms'])
    for v in loaded_faction_mapping.values():
        attila = v[0]
        if attila not in [key['attila_map_key'] for key in attila_source_keys]:
            attila_diff = 1
            missing_keys.append([attila, 'Attila Unit'])

    loaded_heritage_mapping = {
        tuple(k.split(seperator, 1)): v[0] if v else ''
        for k, v in heritage_data.items()
    }
    for k in loaded_heritage_mapping.keys():
        heritage = k[0]
        culture = k[1]
        if heritage not in [key['heritage'] for key in cultures_source_keys] and heritage != 'Unassigned':
            heritage_diff = 1
            missing_keys.append([heritage, 'CK3 Heritage'])
        if culture != 'PARENT_KEY' and culture not in [key['ck3_culture'] for key in cultures_source_keys]:
            culture_diff = 1
            missing_keys.append([culture, 'CK3 Culture'])

    loaded_mods = dict(mod_data)

    # Load title data (backward compatible with old saves)
    title_data = loaded_data.get('TITLES_AND_MAA', {})
    title_names_data = loaded_data.get('TITLE_NAMES', {})
    loaded_title_mapping = {
        tuple(k.split(seperator, 1)): v
        for k, v in title_data.items()
    }
    loaded_title_names = dict(title_names_data)

    # Validate title keys
    title_diff = 0
    for k in loaded_title_mapping.keys():
        maa = k[0]
        if maa not in TITLE_NON_MAA_KEYS and maa not in [key['ck3_maa'] for key in maa_source_keys]:
            maa_diff = 1
            missing_keys.append([maa, 'CK3 ManAtArms (Title)'])
    for v in loaded_title_mapping.values():
        attila = v[0]
        if attila not in [key['attila_map_key'] for key in attila_source_keys]:
            attila_diff = 1
            missing_keys.append([attila, 'Attila Unit (Title)'])
    for tk in loaded_title_names.keys():
        if tk not in [item['title_key'] for item in title_source_keys]:
            title_diff = 1
            missing_keys.append([tk, 'CK3 Title'])

    if maa_diff == 1:
        diff_message = diff_message + '\u26a0\ufe0f Detected missing MAA source! (CK3/CK3 mods)\n'
    if attila_diff == 1:
        diff_message = diff_message + '\u26a0\ufe0f Detected missing Attila source! (Attila/Attila mods)\n'
    if heritage_diff == 1:
        diff_message = diff_message + '\u26a0\ufe0f Detected missing heritage source! (CK3/CK3 mods)\n'
    if culture_diff == 1:
        diff_message = diff_message + '\u26a0\ufe0f Detected missing culture source! (CK3/CK3 mods)\n'
    if title_diff == 1:
        diff_message = diff_message + '\u26a0\ufe0f Detected missing title source! (CK3/CK3 mods)\n'

    if diff_message:
        overall_diff = 1
        unique = sorted(set(tuple(x) for x in missing_keys))
        missing_keys = [list(x) for x in unique]

    return loaded_faction_mapping, loaded_heritage_mapping, loaded_mods, overall_diff, missing_keys, loaded_title_mapping, loaded_title_names, diff_message

# ============================================================
# XML Import / Export
# ============================================================

def import_xml(import_folder):
    imported_mappings = {}
    imported_heritage_mappings = {}
    imported_mods = {}
    import_cultures = os.path.join(import_folder, 'Cultures')
    import_factions = os.path.join(import_folder, 'Factions')
    import_titles = os.path.join(import_folder, 'Titles')
    import_mods = os.path.join(import_folder, 'Mods.xml')

    # Cultures
    if os.path.exists(import_cultures):
        for file in os.listdir(import_cultures):
            if file.endswith('.xml'):
                file_path = os.path.join(import_cultures, file)
                tree = ET.parse(file_path)
                root = tree.getroot()
                for heritage in root:
                    heritage_name = heritage.get('name')
                    heritage_faction = heritage.get('faction')
                    imported_heritage_mappings[(heritage_name, 'PARENT_KEY')] = heritage_faction
                    for culture in heritage:
                        culture_name = culture.get('name')
                        culture_faction = culture.get('faction')
                        imported_heritage_mappings[(heritage_name, culture_name)] = culture_faction

    # Factions
    if not os.path.exists(import_factions):
        return imported_mappings, imported_heritage_mappings, imported_mods, imported_title_mappings, imported_title_names
    for file in os.listdir(import_factions):
        if file.endswith('.xml'):
            file_path = os.path.join(import_factions, file)
            tree = ET.parse(file_path)
            root = tree.getroot()
            for faction in root:
                faction_name = faction.get('name')
                levy_count = 0
                for key in faction:
                    if key.tag == 'MenAtArm':
                        maa_key = key.get('type')
                        attila_key = key.get('key')
                        size = key.get('max')
                        imported_mappings[(maa_key, faction_name)] = [attila_key, size]
                    elif key.tag == 'General':
                        maa_key = 'GENERAL'
                        attila_key = key.get('key')
                        size = 'GENERAL'
                        imported_mappings[(maa_key, faction_name)] = [attila_key, size]
                    elif key.tag == 'Knights':
                        maa_key = 'KNIGHTS'
                        attila_key = key.get('key')
                        size = 'KNIGHTS'
                        imported_mappings[(maa_key, faction_name)] = [attila_key, size]
                    elif key.tag == 'Levies':
                        levy_count += 1
                        maa_key = 'LEVY-IMPORTED_' + str(levy_count)
                        attila_key = key.get('key')
                        size = 'LEVY'
                        try:
                            percentage = int(key.get('porcentage', 0))
                        except (ValueError, TypeError):
                            percentage = 0
                        imported_mappings[(maa_key, faction_name)] = [attila_key, size, percentage]

    # Titles
    imported_title_mappings = {}
    imported_title_names = {}
    if os.path.exists(import_titles):
        for file in os.listdir(import_titles):
            if file.endswith('.xml'):
                file_path = os.path.join(import_titles, file)
                tree = ET.parse(file_path)
                root = tree.getroot()
                for faction in root:
                    title_key = faction.get('title_key')
                    title_name = faction.get('name')
                    if title_key:
                        imported_title_names[title_key] = title_name
                        for key in faction:
                            if key.tag == 'MenAtArm':
                                maa_key = key.get('type')
                                attila_key = key.get('key')
                                size = key.get('max')
                                imported_title_mappings[(maa_key, title_key)] = [attila_key, size]
                            elif key.tag == 'General':
                                attila_key = key.get('key')
                                imported_title_mappings[('GENERAL', title_key)] = [attila_key, 'GENERAL']
                            elif key.tag == 'Knights':
                                attila_key = key.get('key')
                                imported_title_mappings[('KNIGHTS', title_key)] = [attila_key, 'KNIGHTS']

    # Mods
    if os.path.exists(import_mods):
        tree = ET.parse(import_mods)
        root = tree.getroot()
        imported_mods['Attila'] = []
        for mod in root:
            imported_mods['Attila'].append(mod.text)

    return imported_mappings, imported_heritage_mappings, imported_mods, imported_title_mappings, imported_title_names

def export_xml(file, tag, s_date, e_date):
    file_name, _ = os.path.splitext(os.path.split(file)[1])
    export_dir = os.path.join(CUSTOM_MAPPER_DIR, 'export', file_name)
    os.makedirs(export_dir, exist_ok=True)

    # Define export folders and files
    cultures_dir = os.path.join(export_dir, 'Cultures')
    os.makedirs(cultures_dir, exist_ok=True)
    factions_dir = os.path.join(export_dir, 'Factions')
    os.makedirs(factions_dir, exist_ok=True)
    titles_dir = os.path.join(export_dir, 'Titles')
    os.makedirs(titles_dir, exist_ok=True)
    export_mods = os.path.join(export_dir, 'Mods.xml')
    export_tag = os.path.join(export_dir, 'tag.txt')
    export_time = os.path.join(export_dir, 'Time Period.xml')

    seperator = ','
    with open(file, 'r', encoding='utf-8-sig') as f:
        export_dict = json.load(f)
        faction_data = export_dict.get('FACTIONS_AND_MAA', {})
        heritage_data = export_dict.get('HERITAGES_AND_CULTURES', {})
        mod_data = export_dict.get('MODS', {})
        title_data = export_dict.get('TITLES_AND_MAA', {})
        title_names_data = export_dict.get('TITLE_NAMES', {})

        loaded_faction_mapping = {
            tuple(k.split(seperator, 1)): v
            for k, v in faction_data.items()
        }
        loaded_heritage_mapping = {
            tuple(k.split(seperator, 1)): v[0]
            for k, v in heritage_data.items()
        }
        loaded_mods = dict(mod_data)
        loaded_title_mapping = {
            tuple(k.split(seperator, 1)): v
            for k, v in title_data.items()
        }
        loaded_title_names = dict(title_names_data)

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
            maa = child.get('type')
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
    c_output = os.path.join(cultures_dir, file_name + '_Cultures.xml')
    c_root = ET.Element("Cultures")
    heritage_elements = {}
    for key, value in loaded_heritage_mapping.items():
        if key[1] == 'PARENT_KEY':
            heritage_elements[key[0]] = ET.SubElement(c_root, "Heritage", name=key[0], faction=value)
    for key, value in loaded_heritage_mapping.items():
        if key[1] != 'PARENT_KEY' and key[0] in heritage_elements:
            ET.SubElement(heritage_elements[key[0]], "Culture", name=key[1], faction=value)

    c_tree = ET.ElementTree(c_root)
    try:
        ET.indent(c_tree, space="\t", level=0)
    except AttributeError:
        pass
    c_tree.write(c_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Export FACTION mapping to XML file
    f_output = os.path.join(factions_dir, file_name + '_Units.xml')
    f_root = ET.Element("FactionsGroups")
    factions = sorted(set([key[1] for key in loaded_faction_mapping.keys()]), key=sort_factions)
    for fac in factions:
        faction = ET.SubElement(f_root, "Faction", name=fac)
        filtered_items = {
            key: value
            for key, value in loaded_faction_mapping.items() if key[1] == fac
        }
        for key, value in filtered_items.items():
            if key[0] in NON_MAA_KEYS or re.search(r'^LEVY-', key[0]):
                if key[0] == 'GENERAL':
                    ET.SubElement(faction, "General", key=value[0])
                elif key[0] == 'KNIGHTS':
                    ET.SubElement(faction, "Knights", key=value[0])
                else:
                    percentage = str(value[2]) if len(value) > 2 else '0'
                    ET.SubElement(faction, 'Levies', porcentage=percentage, key=value[0], max='LEVY')
            else:
                if value[1]:
                    ET.SubElement(faction, "MenAtArm", type=key[0], key=value[0], max=value[1])
                else:
                    ET.SubElement(faction, "MenAtArm", type=key[0], key=value[0])

        faction[:] = sorted(
            faction,
            key=sort_xml_elements
        )
    f_tree = ET.ElementTree(f_root)
    try:
        ET.indent(f_tree, space="\t", level=0)
    except AttributeError:
        pass
    f_tree.write(f_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Export TITLE mapping to XML files (grouped by rank)
    if loaded_title_mapping:
        rank_prefix_map = {'e': 'Empires', 'k': 'Kingdoms', 'd': 'Duchies'}
        rank_groups = {}
        for title_key in loaded_title_names.keys():
            prefix = title_key[0]
            rank_name = rank_prefix_map.get(prefix)
            if rank_name:
                if rank_name not in rank_groups:
                    rank_groups[rank_name] = []
                rank_groups[rank_name].append(title_key)

        for rank_name, title_keys in rank_groups.items():
            t_output = os.path.join(titles_dir, rank_name + '.xml')
            t_root = ET.Element("Titles")
            t_root.append(ET.Comment("This is to assign MEN-AT-ARMS units based on title key and not owner culture"))
            t_root.append(ET.Comment("Levies do not take part in this!!"))
            t_root.append(ET.Comment("DEFAULT value does not work here, every unit must have a unit key"))
            t_root.append(ET.Comment("title_key = key of the landed title"))

            for title_key in sorted(title_keys):
                title_name = loaded_title_names.get(title_key, title_key)
                faction_elem = ET.SubElement(t_root, "Faction", title_key=title_key, name=title_name)

                filtered_items = {
                    key: value
                    for key, value in loaded_title_mapping.items() if key[1] == title_key
                }
                for key, value in filtered_items.items():
                    if key[0] == 'GENERAL':
                        ET.SubElement(faction_elem, "General", key=value[0])
                    elif key[0] == 'KNIGHTS':
                        ET.SubElement(faction_elem, "Knights", key=value[0])
                    else:
                        if value[1]:
                            ET.SubElement(faction_elem, "MenAtArm", type=key[0], key=value[0], max=value[1])
                        else:
                            ET.SubElement(faction_elem, "MenAtArm", type=key[0], key=value[0])

                faction_elem[:] = sorted(
                    faction_elem,
                    key=sort_xml_elements
                )

            t_tree = ET.ElementTree(t_root)
            try:
                ET.indent(t_tree, space="\t", level=0)
            except AttributeError:
                pass
            t_tree.write(t_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Create tag file
    if not tag:
        tag = file_name
    with open(export_tag, 'w', encoding='utf-8-sig') as f:
        f.write(tag)

    # Create start/end date file
    date_output = export_time
    date_root = ET.Element("TimePeriod")
    date_start = ET.SubElement(date_root, "StartDate")
    date_start.text = s_date if s_date is not None else '0'
    date_end = ET.SubElement(date_root, "EndDate")
    date_end.text = e_date if e_date is not None else '9999'
    date_tree = ET.ElementTree(date_root)
    try:
        ET.indent(date_tree, space="\t", level=0)
    except AttributeError:
        pass
    date_tree.write(date_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    # Create mod file
    mod_output = export_mods
    mod_root = ET.Element("Mods")
    mod_list = loaded_mods.get('Attila', [])
    for mod in mod_list:
        mod_child = ET.SubElement(mod_root, 'Mod')
        mod_child.text = mod
    mod_tree = ET.ElementTree(mod_root)
    try:
        ET.indent(mod_tree, space="\t", level=0)
    except AttributeError:
        pass
    mod_tree.write(mod_output, encoding="utf-8", xml_declaration=True, short_empty_elements=False)

    return export_dir

# ============================================================
# Shared helper: filter source lists (used by GUI windows)
# ============================================================

def filter_source_list(items, key_field, source_field, source_value, search_term):
    """Filter a list of source key dicts by source and search term.

    Args:
        items: List of dicts (e.g. MAA_SOURCE_KEYS, ATTILA_SOURCE_KEYS)
        key_field: Dict key to extract values from (e.g. 'ck3_maa', 'attila_map_key')
        source_field: Dict key for the source (e.g. 'ck3_source', 'attila_source')
        source_value: Source filter value, or 'ALL' for no filter
        search_term: Search string to filter by (case-insensitive), or empty string

    Returns:
        Sorted list of matching key values
    """
    if source_value == 'ALL':
        result = [item[key_field] for item in items]
    else:
        result = [item[key_field] for item in items if item[source_field] == source_value]

    if search_term:
        search_lower = search_term.lower()
        result = [v for v in result if search_lower in v.lower()]

    return sorted(result)
