import os
import sys
import csv
import re
import json
import webbrowser
import FreeSimpleGUI as sg

import cw_map_checker

from utils import init_map_config, import_xml, export_xml 

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Identify working directories
WORKING_DIR = application_path
CW_DIR = os.path.dirname(os.path.dirname(application_path)) #Expected directory: CW/tools/cw_mapper

ASCII_ART_MAIN = os.path.join('ascii-art-main.png')
ASCII_ART_MAPPER = os.path.join('ascii-art-mapper.png')
SUMMARY_LOG = os.path.join("summary_log.txt")
ATTILA_EXPORT_DIR = os.path.join(WORKING_DIR, 'attila_exports','db','main_units_tables')
REPORT_OUTPUT_DIR = 'reports'
CUSTOM_MAPPER_DIR = 'custom_mappers'

MOD_LIST = []

# Key sources
ATTILA_SOURCE_KEYS = []
CULTURES_SOURCE_KEYS = []
MAA_SOURCE_KEYS = []

ATTILA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv')
CULTURES_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures_keys.csv')
MAA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa_keys.csv')

NON_MAA_KEYS = [
    'GENERAL',
    'KNIGHTS',
    'LEVY-SPEAR',
    'LEVY-SWORD',
    'LEVY-ARCHER',
    'LEVY-SKIRM',
    'LEVY-CAV',
    'LEVY-CUSTOM1',
    'LEVY-CUSTOM2',
    'LEVY-CUSTOM3',
]

# If none of the source files exists, run the check program to refresh files
if not os.path.exists(ATTILA_SOURCE_PATH) or not os.path.exists(CULTURES_SOURCE_PATH) or not os.path.exists(MAA_SOURCE_PATH):
    init_map_config()
    cw_map_checker.mapping_validation(*cw_map_checker.get_keys(cw_map_checker.get_cw_config()))
    cw_map_checker.summary()

with open (ATTILA_SOURCE_PATH, 'r') as f:
    key_data = csv.DictReader(f)
    for key in key_data:
        ATTILA_SOURCE_KEYS.append({'attila_map_key':key['attila_map_key'],'attila_source':key['attila_source']})

with open(CULTURES_SOURCE_PATH, 'r') as f:
    key_data = csv.DictReader(f)
    for key in key_data:
        CULTURES_SOURCE_KEYS.append({'ck3_culture':key['ck3_culture'],'heritage':key['ck3_heritage'],'ck3_source':key['ck3_source']})

with open(MAA_SOURCE_PATH, 'r') as f:
    key_data = csv.DictReader(f)
    for key in key_data:
        MAA_SOURCE_KEYS.append({'ck3_maa':key['ck3_maa'],'ck3_source':key['ck3_source']})
    for maa in NON_MAA_KEYS:
        MAA_SOURCE_KEYS.append({'ck3_maa':maa,'ck3_source':'CW'})

ATTILA_SOURCES = [item['attila_source'] for item in ATTILA_SOURCE_KEYS]
CK3_SOURCES = [item['ck3_source'] for item in CULTURES_SOURCE_KEYS] + [item['ck3_source'] for item in MAA_SOURCE_KEYS]

def popup_mapper_name_input():
    layout = [
        [sg.Text('Enter a name for your mapper:')],
        [sg.Input(
            key='CUSTOM_MAPPER_NAME_INPUT'
        )],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Custom mapper name input', layout, modal=True)
    event, values = window.read(close=True) # Closes the window after reading the event

    if event == 'OK':
        name = values['CUSTOM_MAPPER_NAME_INPUT']
        if name:
            return name
    return None

def popup_faction_copy(factions):
    layout = [
        [sg.Text('Select a faction to copy from:')],
        [sg.Listbox(
            values=factions,
            select_mode=sg.SELECT_MODE_SINGLE,
            size=(25, min(10, len(factions))), # Adjust size dynamically
            key='FACTION_COPIED_KEY'
        )],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Copy from faction', layout, modal=True)
    event, values = window.read(close=True) # Closes the window after reading the event

    if event == 'OK':
        target_faction = values['FACTION_COPIED_KEY']
        if target_faction:
            return target_faction
    return None

def popup_faction_list(factions):
    formatted_faction_list = ''
    for faction in factions:
        line = faction
        formatted_faction_list += line + '\n'
    layout = [
        [sg.Text('Faction list, seperate with a new line')],
        [sg.Multiline(
            formatted_faction_list,
            size=(50, 20),
            key='FACTION_EDIT_LIST'
        )],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Edit faction list', layout, modal=True)
    event, values = window.read(close=True) # Closes the window after reading the event

    if event == 'OK':
        new_faction_list = values['FACTION_EDIT_LIST'].split('\n')
        clean_faction_list = [item.strip() for item in new_faction_list]
        if clean_faction_list:
            return clean_faction_list
    return None

def popup_heritage_pick_faction(factions, heritage_mapping_dict, selected_map):
    layout = [
        [sg.Text('Select a faction to assign:')],
        [sg.Listbox(
            values=factions,
            select_mode=sg.SELECT_MODE_SINGLE,
            size=(25, min(10, len(factions))), # Adjust size dynamically
            key='FACTION_HERITAGE_KEY'
        )],
        [sg.Button('OK')]
    ]

    window = sg.Window('Assign faction to heritage/culture', layout, modal=True)
    event, values = window.read(close=True) # Closes the window after reading the event

    if event == 'OK':
        if values['FACTION_HERITAGE_KEY'] == []:
            return None
        prefix = selected_map[0].split(sep=': ', maxsplit=1)[0].strip()
        selected_map = selected_map[0].split(sep=': ', maxsplit=1)[1]
        current_faction = selected_map.split(sep='--',maxsplit=1)[1].strip()
        selected_map = selected_map.split(sep='--',maxsplit=1)[0].strip()
        target_faction = values['FACTION_HERITAGE_KEY'][0]

        for pair in heritage_mapping_dict:
            if pair[0] == selected_map and pair[1] == 'PARENT_KEY': # i.e. if selected a heritage key
                for pair in heritage_mapping_dict: # Assign faction inner loop
                    if pair[0] == selected_map:
                        heritage_mapping_dict[pair] = target_faction
            elif pair[1] == selected_map and heritage_mapping_dict[pair].strip() == current_faction: #i.e. if culture name match and faction match
                heritage_mapping_dict[pair] = target_faction
    return heritage_mapping_dict

def popup_size_manual():
    ALLOWED_CHARS = '0123456789'
    default_size = 'INFANTRY'
    layout = [
        [sg.Text('Enter unit size (numbers only):')],
        [sg.Input(
            default_text='0',
            key='MANUAL_SIZE_INPUT',
            enable_events=True
        )],
        [sg.Button('OK')]
    ]

    window = sg.Window('Custom mapper name input', layout, modal=True)

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            window.close()
            return default_size
        
        elif event == 'MANUAL_SIZE_INPUT':
            current_value = values['MANUAL_SIZE_INPUT']
            updated_value = current_value

            if len(current_value) > 0 and current_value[-1] not in ALLOWED_CHARS:
                window['MANUAL_SIZE_INPUT'].update(current_value[:-1])
                sg.popup_no_buttons('Only numbers are allowed!', auto_close=True, auto_close_duration=2,title='Input Error')
    
            if len(updated_value) > 1 and updated_value.startswith('0'):
                    stripped_zeros = updated_value.lstrip('0')

                    if stripped_zeros == '':
                        updated_value = '0'
                    else:
                        updated_value = stripped_zeros
                    
                    # Update the input field only if the value actually changed
                    if updated_value != current_value:
                        window['MANUAL_SIZE_INPUT'].update(updated_value)
        
        elif event == 'OK':
            size = values['MANUAL_SIZE_INPUT']
            if size:
                window.close()
                return size
            else:
                sg.popup('Input cannot be empty!', auto_close=True, auto_close_duration=2, title='Error')

def popup_xml_import_export():
    cw_mapper_dir = os.path.join(CW_DIR,'unit mappers','attila')

    layout = [
        [sg.Text('Import or export mappers into their .xml formats, ready for Crusader Wars')],
        [sg.Button('Import',size=(15, 2), button_color=('white', "#008670"), expand_x=True), sg.Button('Export',size=(15, 2), button_color=('white', "#008670"),expand_x=True)]
    ]

    window = sg.Window('Import/Export to XML', layout, modal=True)
    event, values = window.read(close=True) # Closes the window after reading the event

    if event == 'Import':
        import_folder = sg.popup_get_folder(title='Find mapper folder',message='Please select the mapping folder you wish to import',initial_folder=cw_mapper_dir)
        if import_folder:
            if not os.path.exists(os.path.join(import_folder,'Factions')): # Only checking for factions as titles and additional cultures/heritages may not exist
                sg.popup_error('Error: Not a valid mapping directory!',title='Directory Error')
            else:
                _, mapper_name = os.path.split(import_folder)
                imported_maa_map, imported_heritage_map = import_xml(import_folder)
                window.close()
                return mapper_name, imported_maa_map, imported_heritage_map

    if event == 'Export':
        pass
    return None

def heritage_window(heritage_mapping_dict, factions):
    # Available heritages, format (heritage, culture) tuple, should allow people to either take a whole heritage, or a specific culture
    available_heritages = []
    
    source_heritages = sorted(set([item['heritage'] for item in CULTURES_SOURCE_KEYS if item['heritage']]))
    source_heritages = ["Unassigned"] + source_heritages

    available_heritages_display_list = []
    display_list = []

    # Initialise available_heritages list from source keys
    for heritage in source_heritages:
        available_heritages.append((heritage,'PARENT_KEY'))
        available_heritages_display_list.append(f'HERITAGE: {heritage}')
        if heritage == 'Unassigned':
            cultures = sorted(set([item['ck3_culture'] for item in CULTURES_SOURCE_KEYS if item['heritage'] == '']))
        else:
            cultures = sorted(set([item['ck3_culture'] for item in CULTURES_SOURCE_KEYS if item['heritage'] == heritage]))
        for culture in cultures:
            source = ([item['ck3_source'] for item in CULTURES_SOURCE_KEYS if item['ck3_culture'] == culture])[0]
            available_heritages.append((heritage,culture))
            available_heritages_display_list.append(f'   ->: {culture} ({source})')

    def refresh_display_lists(window, available_heritages, heritage_mapping_dict):
        # Clear current display lists and rebuild
        available_heritages_display_list = []
        display_list = []

        available_heritages_widget = window['HERITAGE_AVAILABLE_LIST'].Widget
        heritages_widget = window['HERITAGE_MAP_LIST'].Widget
        current_y_ah = available_heritages_widget.yview()[0] # Retain current y-scroll
        current_y_h = heritages_widget.yview()[0]
        
        # Re-sort lists
        def deduplicate_in_order(data):
            """
            Deduplicates a list of hashable items while preserving the 
            order of first appearance.
            """
            seen = set()
            result = []
            
            for item in data:
                if item not in seen:
                    seen.add(item)
                    result.append(item)
                    
            return result

        def sort_heritages_key(item):
            heritage = item[0]
            culture = item[1]

            if heritage == 'Unassigned' and culture == 'PARENT_KEY':
                priority = 0  # Group 1: [Unassigned, PARENT_KEY]
            elif heritage == 'Unassigned':
                priority = 1  # Group 2/3: [Unassigned, ...]
            else:
                priority = 2

            secondary_key = heritage

            if culture == 'PARENT_KEY':
                tertiary_key = "AAA" # 'AAA' is alphabetically smaller than most culture strings
            else:
                tertiary_key = culture

            return (priority, secondary_key, tertiary_key)

        available_heritages = sorted(available_heritages, key=sort_heritages_key)
        # Deduplicate available heritages
        available_heritages = deduplicate_in_order(available_heritages)

        heritage_mapping_dict = dict(sorted(heritage_mapping_dict.items(), key=sort_heritages_key))
        # Available heritages
        for pair in available_heritages:
            if pair[1] == 'PARENT_KEY':
                h_count = 1
            else:
                source = ([item['ck3_source'] for item in CULTURES_SOURCE_KEYS if item['ck3_culture'] == pair[1]])
                if source == []:
                    source = None
                else:
                    source = source[0]
                if h_count == 1:
                    available_heritages_display_list.append(f'HERITAGE: {pair[0]}')
                h_count = h_count+1
                available_heritages_display_list.append(f'   ->: {pair[1]} ({source})')

        # Stealth refresh and restore previous y-scroll
        window['HERITAGE_AVAILABLE_LIST'].update(available_heritages_display_list, visible = False)
        available_heritages_widget.yview_moveto(current_y_ah)
        window['HERITAGE_AVAILABLE_LIST'].update(visible = True)

        # Mapped heritages
        for pair in heritage_mapping_dict:
            faction = heritage_mapping_dict[pair]
            if pair[1] == 'PARENT_KEY':
                h_count = 1
                parent_faction = faction
            else:
                if h_count == 1:
                    display_list.append(f'HERITAGE: {pair[0]}   -- {parent_faction}')
                h_count = h_count+1
                display_list.append(f'   ->: {pair[1]}   -- {faction}')

        # Stealth refresh and restore previous y-scroll
        window['HERITAGE_MAP_LIST'].update(display_list, visible = False)
        heritages_widget.yview_moveto(current_y_h)
        window['HERITAGE_MAP_LIST'].update(visible = True)

    def add_heritage(available_heritages, heritage_mapping_dict, selected_key):
            added_mapping = []
            added_key = selected_key.split(sep=': ', maxsplit=1)[1]
            added_key = added_key.strip()
            if added_key in [heritage[0] for heritage in available_heritages]: #i.e. a heritage key not a culture key
                # Entire heritage
                added_key_pair = (added_key, 'PARENT_KEY')
                added_mapping = [heritage for heritage in available_heritages if heritage[0] == added_key]
                available_heritages = [heritage for heritage in available_heritages if heritage[0] != added_key] # Drop keys with specified heritage
                for map in added_mapping:
                    culture = map[1].split('(',maxsplit=1)[0].strip()
                    added_key_pair = (added_key, culture)
                    heritage_mapping_dict[added_key_pair] = ''
            else:
                matching_heritage = [item['heritage'] for item in CULTURES_SOURCE_KEYS if item['ck3_culture'] == added_key.split(' ')[0]]
                if matching_heritage == ['']:
                    matching_heritage = ['Unassigned']
                    culture = added_key.split('(',maxsplit=1)[0].strip()
                    added_key_pair = (matching_heritage[0], culture)
                else:
                    culture = added_key.split('(',maxsplit=1)[0].strip()
                    added_key_pair = (matching_heritage[0], culture)
                # Handle for missing parent_key
                if not any(heritage[0] in matching_heritage for heritage in heritage_mapping_dict):
                    heritage_mapping_dict[(matching_heritage[0],'PARENT_KEY')] = ''

                heritage_mapping_dict[added_key_pair] = '' # Add the heritage/culture but leave faction blank
                available_heritages = [heritage for heritage in available_heritages if heritage != added_key_pair] # Drop specific (heritage, culture) pair key
            
            refresh_display_lists(window, available_heritages, heritage_mapping_dict)
            return available_heritages

    def remove_heritage(available_heritages, heritage_mapping_dict, selected_key):
        removed_mapping = []
        removed_key = selected_key.split(sep=': ', maxsplit=1)[1]
        removed_key = removed_key.split(sep='--',maxsplit=1)[0].strip()
        if removed_key in [heritage[0] for heritage in heritage_mapping_dict]: #i.e. a heritage key not a culture key
            # Entire heritage
            removed_key_pair = (removed_key, 'PARENT_KEY')
            removed_mapping = [heritage for heritage in heritage_mapping_dict if heritage[0] == removed_key]
            heritage_mapping_dict = {
                pair: value
                for pair, value in heritage_mapping_dict.items() if pair[0] != removed_key} # Drop keys with specified heritage
            for map in removed_mapping:
                removed_key_pair = (removed_key, map[1])
                available_heritages.append(removed_key_pair)
        else:
            matching_heritage = [item['heritage'] for item in CULTURES_SOURCE_KEYS if item['ck3_culture'] == removed_key.split(' ')[0]]
            if matching_heritage == ['']:
                matching_heritage = ['Unassigned']
                removed_key_pair = (matching_heritage[0], removed_key)
            else:
                removed_key_pair = (matching_heritage[0], removed_key)
            # Handle for missing parent_key
            if not any(t[0] in matching_heritage for t in available_heritages):
                available_heritages.append((matching_heritage[0],'PARENT_KEY'))

            available_heritages.append(removed_key_pair) # Add the heritage/culture to available list
            heritage_mapping_dict = { # Drop specific (heritage, culture) pair key
                pair: value
                for pair, value in heritage_mapping_dict.items() if pair != removed_key_pair
            }
        
        refresh_display_lists(window, available_heritages, heritage_mapping_dict)
        return heritage_mapping_dict

    heritage1_col_layout = [
        [sg.Text('Available Heritages and Cultures', font=('Courier New', 12, 'bold'), text_color='#6D0000', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE)],
        [sg.Listbox(
            values=available_heritages_display_list,
            size=(50, 20),
            key='HERITAGE_AVAILABLE_LIST',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            tooltip='Available list of heritages and their associated cultures.\n\nYou can also press spacebar to quickly select with the arrow keys.',
            expand_x=True,
            expand_y=True
        )]
    ]

    heritage2_col_layout = [
            [sg.Button('<<<', size=(10, 2), button_color=('white', '#444444')),sg.Button('>>>', size=(10, 2), button_color=('white', '#444444'))]
        ]

    heritage3_col_layout = [
        [sg.Text('Heritage/Culture to Faction Mapping', font=('Courier New', 12, 'bold'), text_color='#00006D', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE)],
        [sg.Button('Assign Faction', size=(20, 1), button_color=('white', '#008670'), disabled=True)],
        [sg.Listbox(
            values=display_list,
            size=(50, 20),
            key='HERITAGE_MAP_LIST',
            tooltip='Your list of heritages and cultures, with their associated factions.\n\nYou can also press spacebar to quickly select with the arrow keys.',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True
        )]
    ]
    
    layout = [
        [sg.Column(heritage1_col_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
         sg.Column(heritage2_col_layout, element_justification='center', vertical_alignment='center', pad=(10, 10), background_color='#DDDDDD'),
        sg.Column(heritage3_col_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
         ],
        [sg.Push(),sg.Button('OK', size=(15, 2), button_color=('white', '#444444')),sg.Push()]
    ]

    window = sg.Window('Edit heritage mapping', layout, modal=True, finalize= True)

    # Initialise mapping/edit listbox and remove from keys from available list as part of import
    if heritage_mapping_dict:
        loaded_keys = [keys for keys in heritage_mapping_dict]
        available_heritages = [heritage for heritage in available_heritages if not heritage in loaded_keys]
        # Handle for missing parent_key due to import
        remaining_heritages = {t[0] for t in available_heritages}
        heritage_has_parent = {t[0] for t in available_heritages if t[1] == 'PARENT_KEY'}
        heritage_missing_parent = sorted(list(remaining_heritages - heritage_has_parent))

        for heritage in heritage_missing_parent:
            available_heritages.append((heritage,'PARENT_KEY'))

    refresh_display_lists(window, available_heritages, heritage_mapping_dict)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break
         
        elif event == '>>>': # Add to editable list
            selected_heritage_to_add = values['HERITAGE_AVAILABLE_LIST']
            if selected_heritage_to_add:
                available_heritages = add_heritage(available_heritages, heritage_mapping_dict, selected_heritage_to_add[0])

        elif event == '<<<': # Remove from editable list
            selected_heritage_to_remove = values['HERITAGE_MAP_LIST']
            if selected_heritage_to_remove:
                heritage_mapping_dict = remove_heritage(available_heritages, heritage_mapping_dict, selected_heritage_to_remove[0])

        elif event == 'Assign Faction': # Assign faction button
            selected_map = values['HERITAGE_MAP_LIST']
            if selected_map:
                new_mapping = popup_heritage_pick_faction(factions, heritage_mapping_dict, selected_map)
                if new_mapping:
                    heritage_mapping_dict = new_mapping
                    refresh_display_lists(window, available_heritages, heritage_mapping_dict)

            window['Assign Faction'].update(disabled = True)

        elif event == 'HERITAGE_MAP_LIST':
            selected_map = values['HERITAGE_MAP_LIST']
            if selected_map:
                window['Assign Faction'].update(disabled = False)
        
        elif event == 'OK':
            window.close()
            return heritage_mapping_dict
    window.close()
    return heritage_mapping_dict

def mapping_window():
    ATTILA_UNIT_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(ATTILA_SOURCES)))
    MAA_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(CK3_SOURCES)))

    FACTION_LIST = ['DEFAULT'] + [
    ]

    SIZE_LIST = ['MANUAL','CAVALRY','INFANTRY','RANGED']

    # Dictionary to store the actual mappings (CK3 MAA: ATTILA UNIT KEY, per FACTION)
    
    MAPPER_NAME = ''
    # Format faction mapping: {(ck3_maa, faction): [attila_unit]} | {tuple: [value]}
    current_mappings = {}
    # Format heritage mapping: {heritage(faction,[culture[faction]]} | {key(value,list[value])}
    current_heritage_mappings = {}
    CK3_SOURCE_KEY = 'CK3_SOURCE_KEY'
    ATTILA_SOURCE_KEY = 'ATTILA_SOURCE_KEY'
    FACTION_KEY = 'FACTION_SELECT_KEY'


    # Column Definitions and layout
    # Column 1: CK3 MAA Selector
    col1_layout = [
        [sg.Text('Available CK3 MAA', font=('Courier New', 12, 'bold'), text_color='#6D0000', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE),
         sg.Text('Filter CK3 source:'), sg.Combo(
            values=MAA_LIST_SOURCE, 
            default_value=MAA_LIST_SOURCE[0], 
            size=(20, 1), 
            key=CK3_SOURCE_KEY, 
            readonly=True,
            enable_events=True
        )],
        [sg.Text('Search...',background_color='#DDDDDD',text_color="#000000"),sg.Input(key='CK3_SEARCH_KEY', enable_events=True)]
        ,
        [sg.Listbox(
            values=sorted([item['ck3_maa'] for item in MAA_SOURCE_KEYS]),
            size=(30, 15),
            key='CK3_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected CK3:', size=(25, 1), key='SELECTED_CK3_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN, expand_x=True, justification='center')]
    ]

    # Column 2: ATTILA UNIT KEY Selector
    col2_layout = [
        [sg.Text('Available ATTILA UNIT KEYS', font=('Courier New', 12, 'bold'), text_color='#006D00', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE),
         sg.Text('Filter Attila source:'), sg.Combo(
            values=ATTILA_UNIT_LIST_SOURCE, 
            default_value=ATTILA_UNIT_LIST_SOURCE[0], 
            size=(20, 1), 
            key=ATTILA_SOURCE_KEY, 
            readonly=True,
            enable_events=True
        )],
        [sg.Text('Search...',background_color='#DDDDDD',text_color="#000000"),sg.Input(key='ATTILA_SEARCH_KEY', enable_events=True),sg.Text('Select unit size:'), sg.Combo(
            values=SIZE_LIST, 
            default_value=SIZE_LIST[0], 
            size=(10, 1), 
            key='MAA_SIZE_SELECT', 
            readonly=True,
            enable_events=True
        )]
        ,
        [sg.Listbox(
            values=sorted([item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]),
            size=(30, 15),
            key='ATTILA_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected ATTILA:', size=(25, 1), key='SELECTED_ATTILA_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN, expand_x=True, justification='center')]
    ]

    # Column 3: Mappings Display and Action Buttons
    col3_layout = [
        [sg.Text(f'Unit Key Mapper: {MAPPER_NAME}', key='MAPPER_COL_TITLE_KEY', font=('Courier New', 12, 'bold'), text_color='#00006D', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE)],
        # Faction Selector Dropdown
        [sg.Text('Select Faction:'), sg.Combo(
            values=FACTION_LIST, 
            default_value=FACTION_LIST[0], 
            size=(20, 1), 
            key=FACTION_KEY, 
            readonly=True,
            enable_events=True
        ),sg.Push(background_color='#DDDDDD'),sg.Button('Save', key='SAVE_BUTTON_KEY',size=(15, 2), button_color=('white', '#444444')),sg.Input(key='FILE_LOAD_KEY',visible=False,enable_events=True),sg.FileBrowse('Load', target='FILE_LOAD_KEY',size=(15, 2), initial_folder=CUSTOM_MAPPER_DIR, button_color=('white', '#444444'),file_types=((('Text Files', '*.txt'),))),sg.Button('Import/Export XML', key='XML_BUTTON', size=(15, 2), button_color=('white', "#008670"))],
        [sg.Listbox(
            values=[],
            size=(35, 13), # Adjusted size to fit the Combo element
            key='MAPPING_LISTS_KEY',
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            background_color='#E8E8FF',
            expand_x=True,
            expand_y=True
        )],
        [sg.Button('Add Mapping', key='ADD_MAPPING_KEY', size=(15, 2), button_color=('white', '#004D40'), disabled=True),sg.Button('Remove Selected', key='REMOVE_MAPPING_KEY', size=(15, 2), button_color=('white', '#CC0000'), disabled=True),sg.Push(background_color='#DDDDDD'),sg.Button('Open Heritage mapping', key='HERITAGE_EDIT_BUTTON_KEY', size=(25, 2), button_color=('white', '#444444'))],
        [sg.Button('Copy from faction', key='FACTION_COPY_BUTTON_KEY',size=(15, 2), button_color=('white', "#008670")),sg.Push(background_color='#DDDDDD'),sg.Button('Edit faction list', key='FACTION_LIST_EDIT_BUTTON_KEY', size=(15, 2), button_color=('white', '#444444'))]
    ]

    # Main layout
    mapper_layout = [
        [sg.Image(ASCII_ART_MAPPER)],
        [sg.Text('Create your "MAA => UNIT" mapping, per FACTION here. Each FACTION can have as many "MAA => UNIT" mappings as you like. Any missing "MAA => UNIT" mappings will fallback to faction DEFAULT, or crash if not present.', font=('Courier New', 10, 'bold'), justification='center', expand_x=True)],
        [sg.Text('Each FACTION is assigned to one or many HERITAGE.', font=('Courier New', 10, 'bold'), justification='center', expand_x=True)],
        [
            sg.Column(col1_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col2_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col3_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True)
        ],
        [sg.Button('Exit', size=(15, 2), button_color=('white', '#444444'))]
    ]

    window = sg.Window('Custom Unit Mapper', mapper_layout, finalize=True, element_justification='center',resizable=True)

    # Variables to hold the currently selected items
    selected_ck3 = None
    selected_attila = None
    current_faction = FACTION_LIST[0]

    # FUNCTIONS
    # ==============================================
    def update_mappings_list(window, mappings_dict):
        """Formats the mapping dictionary into a list of strings for the Listbox."""
        mapping_widget = window['MAPPING_LISTS_KEY'].Widget
        current_y = mapping_widget.yview()[0] # Retain current y-scroll

        display_list = []
        formatted_list = []
        # Key is a tuple (ck3_maa, faction), value is attila_unit
        for (ck3, faction), attila in mappings_dict.items():
            display_list = [t for t in mappings_dict.items() if t[0][1] == current_faction]
        if display_list:
            for (ck3, faction), attila in display_list:
                formatted_list.append(f"[{faction}] {ck3}   => {attila}")
        else:
            formatted_list = []
        
        window['MAPPING_LISTS_KEY'].update(sorted(formatted_list), visible = False)
        mapping_widget.yview_moveto(current_y)
        window['MAPPING_LISTS_KEY'].update(visible = True)
        # Re-enable/disable the Remove button based on whether there are mappings
        window['REMOVE_MAPPING_KEY'].update(disabled=len(formatted_list) == 0)

    # Function to check if the 'Add Mapping' button should be active
    def check_add_button(window):
        """Enables the Add button only if both CK3 and Attila units are selected."""
        is_ready = selected_ck3 is not None and selected_attila is not None and values[FACTION_KEY] != ''
        window['ADD_MAPPING_KEY'].update(disabled=not is_ready)

    def save_mapper(name, faction_mapping, heritage_mapping):
        output_path = os.path.join(CUSTOM_MAPPER_DIR,f'{name}.txt')
        os.makedirs(CUSTOM_MAPPER_DIR, exist_ok=True)
        seperator = ','
        save_format = {
            'FACTIONS AND MAA': {
                seperator.join(k):v
                for k,v in faction_mapping.items()
                },
            'HERITAGES AND CULTURES': {
                seperator.join(k):[v]
                for k,v in heritage_mapping.items()
                },
        }
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(save_format,f,indent=4)

    def load_mapper(file):
        seperator = ','
        with open(file, 'r', encoding='utf-8-sig') as f:
            loaded_data = json.load(f)

        faction_data = loaded_data.get('FACTIONS AND MAA',{})
        heritage_data = loaded_data.get('HERITAGES AND CULTURES', {})
        
        loaded_faction_mapping = {
            tuple(k.split(seperator)):v
            for k, v in faction_data.items()
        }
        loaded_heritage_mapping = {
            tuple(k.split(seperator)):v[0]
            for k, v in heritage_data.items()
        }
        return loaded_faction_mapping, loaded_heritage_mapping

    # END FUNCTIONS
    # ==============================================

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        elif event == 'CK3_LIST_KEY':
            if values['CK3_LIST_KEY']:
                selected_ck3 = values['CK3_LIST_KEY']
                if len(values['CK3_LIST_KEY']) > 1:
                    window['SELECTED_CK3_KEY'].update(f'Selected CK3: Multiple', background_color='#F5962A')
                else:
                    window['SELECTED_CK3_KEY'].update(f'Selected CK3: {selected_ck3}', background_color='#F5962A')
            else:
                selected_ck3 = None
                window['SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
            check_add_button(window)

        elif event == 'ATTILA_LIST_KEY':
            if values['ATTILA_LIST_KEY']:
                selected_attila = values['ATTILA_LIST_KEY']
                window['SELECTED_ATTILA_KEY'].update(f'Selected ATTILA: {selected_attila}', background_color="#F5962A")
            else:
                selected_attila = None
                window['SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')
            check_add_button(window)

        elif event == CK3_SOURCE_KEY:
            current_ck3_source = values[CK3_SOURCE_KEY]
            search_term = values['CK3_SEARCH_KEY']
            
            if current_ck3_source == 'ALL':
                new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS]
                if search_term != '':
                    new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if search_term.lower() in item['ck3_maa'].lower()]
            else:
                new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if item['ck3_source'] == current_ck3_source]
                if search_term != '':
                    new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if search_term.lower() in item['ck3_maa'].lower() and item['ck3_source'] == current_ck3_source]
            window['CK3_LIST_KEY'].update(sorted(new_list))

        elif event == ATTILA_SOURCE_KEY:
            current_att_source = values[ATTILA_SOURCE_KEY]
            search_term = values['ATTILA_SEARCH_KEY']
            
            if current_att_source == 'ALL':
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]
                if search_term != '':
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower()]
            else:
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if item['attila_source'] == current_att_source]
                if search_term != '':
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower() and item['attila_source'] == current_att_source]
            window['ATTILA_LIST_KEY'].update(sorted(new_list))

        elif event == FACTION_KEY:
            current_faction = values[FACTION_KEY]
            update_mappings_list(window, current_mappings)
            check_add_button(window)

        elif event == 'CK3_SEARCH_KEY':
            current_ck3_source = values[CK3_SOURCE_KEY]
            search_term = values['CK3_SEARCH_KEY']
            
            if current_ck3_source == 'ALL':
                new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS]
                if search_term != '':
                    new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if search_term.lower() in item['ck3_maa'].lower()]
            else:
                new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if item['ck3_source'] == current_ck3_source]
                if search_term != '':
                    new_list = [item['ck3_maa'] for item in MAA_SOURCE_KEYS if search_term.lower() in item['ck3_maa'].lower() and item['ck3_source'] == current_ck3_source]
            window['CK3_LIST_KEY'].update(sorted(new_list))

        elif event == 'ATTILA_SEARCH_KEY':
            current_att_source = values[ATTILA_SOURCE_KEY]
            search_term = values['ATTILA_SEARCH_KEY']
            
            if current_att_source == 'ALL':
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]
                if search_term != '':
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower()]
            else:
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if item['attila_source'] == current_att_source]
                if search_term != '':
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower() and item['attila_source'] == current_att_source]
            window['ATTILA_LIST_KEY'].update(sorted(new_list))

        elif event == 'SAVE_BUTTON_KEY':
            if MAPPER_NAME:
                save_mapper(MAPPER_NAME, current_mappings, current_heritage_mappings)
            else:
                name = popup_mapper_name_input()
                if name:
                    save_mapper(name,current_mappings, current_heritage_mappings)
                    MAPPER_NAME = name
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')

        elif event == 'FILE_LOAD_KEY':
            loaded_faction_mapping, loaded_heritage_mapping = load_mapper(values['FILE_LOAD_KEY'])
            map_name, _ = os.path.splitext(os.path.basename(values['FILE_LOAD_KEY']))
            if loaded_faction_mapping:
                current_mappings = loaded_faction_mapping
                current_heritage_mappings = loaded_heritage_mapping
                available_factions = list(set([item[0][1] for item in current_mappings.items()]))
                FACTION_LIST = sorted(available_factions)
            MAPPER_NAME = map_name
            update_mappings_list(window, current_mappings)
            window[FACTION_KEY].update(values=FACTION_LIST)
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')

        elif event == 'ADD_MAPPING_KEY' and selected_ck3 and selected_attila:
            current_faction = values[FACTION_KEY]
            if current_faction:
                size = values['MAA_SIZE_SELECT']
                if size == 'MANUAL':
                        size = popup_size_manual()
                for selected in selected_ck3:
                    mapping_key = (selected, current_faction)
                
                    # Check for conflicts (CK3 unit + Faction combination already mapped), and overwrite if so.
                    for key in mapping_key:
                        if key in current_mappings:
                            key_to_remove = (selected, current_faction)
                            del current_mappings[key_to_remove]
                        if re.search(r'^LEVY-', key):
                            size = 'LEVY'
                        if re.search(r'^GENERAL\b', key):
                            size = 'GENERAL'
                        if re.search(r'^KNIGHTS\b', key):
                            size = 'KNIGHTS'
            
                    current_mappings[mapping_key] = selected_attila + [size]

                    # Update the displayed list
                    update_mappings_list(window, current_mappings)
                    check_add_button(window)

                # Reset unit selections for the next mapping
                selected_ck3 = None
                selected_attila = None
                window['CK3_LIST_KEY'].update(set_to_index=[])
                window['ATTILA_LIST_KEY'].update(set_to_index=[])
                window['SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
                window['SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')

        elif event == 'REMOVE_MAPPING_KEY':
            if values['MAPPING_LISTS_KEY']:
                # The listbox value is a formatted string. We need to parse it back to find the key tuple.
                for formatted_mapping in values['MAPPING_LISTS_KEY']:
                    # Format: [faction] ck3_unit => attila_unit
                    if formatted_mapping.startswith('['):
                        parts = formatted_mapping.split('] ')
                        faction_key = parts[0].strip('[')
                        ck3_key_to_remove = parts[1].split(' => ')[0].strip()

                    key_to_remove = (ck3_key_to_remove, faction_key)

                    if key_to_remove in current_mappings:
                        del current_mappings[key_to_remove]
                        update_mappings_list(window, current_mappings)

                # Clear selection in case the user immediately clicks remove again
                window['MAPPING_LISTS_KEY'].update(set_to_index=[])
        
        elif event == 'FACTION_COPY_BUTTON_KEY':
            target_faction = popup_faction_copy(FACTION_LIST)
            if target_faction:
                copied_mapping = [item for item in current_mappings.items() if item[0][1] == target_faction[0]]
                for copied_key, copied_value in copied_mapping:
                    mapping_key = (copied_key[0], current_faction)

                    # Check for conflicts (CK3 unit + Faction combination already mapped), and overwrite if so.
                    for key in mapping_key:
                        if key in current_mappings:
                            key_to_remove = (key[0], current_faction)
                            del current_mappings[key_to_remove]
                    current_mappings[mapping_key] = copied_value
                    # Update the displayed list
                update_mappings_list(window, current_mappings)
                check_add_button(window)

        elif event == 'FACTION_LIST_EDIT_BUTTON_KEY':
            new_faction_list = popup_faction_list(FACTION_LIST)
            if new_faction_list != None:
                FACTION_LIST = new_faction_list
                window[FACTION_KEY].update(values=FACTION_LIST)
        
        elif event == 'HERITAGE_EDIT_BUTTON_KEY':
            current_heritage_mappings = heritage_window(current_heritage_mappings, FACTION_LIST)

        elif event == 'XML_BUTTON':
            xml_import = popup_xml_import_export()
            if xml_import:
                import_name = xml_import[0]
                import_maa = xml_import[1]
                import_heritage = xml_import[2]
                save_mapper(import_name,import_maa, import_heritage)

    window.close()

def main_window():
    # Initialise the text in the summary log, if it exists
    if os.path.exists(SUMMARY_LOG):
        with open(SUMMARY_LOG, 'r', encoding="utf-8-sig") as f:
            TEXT = f.read()
    else:
        TEXT = "No summary_log.txt was found. Refresh your mappers using 'Refresh Current Mappers'"


    layout = [
    [sg.Image(ASCII_ART_MAIN)],
    [sg.Text(text='''A mapping tool for FarayC's Crusader Wars, developed by equanimity''',font=('Courier New', 10))],
    [sg.Text(text='Instructions: Click the "Refresh Current Mappers" button to refresh the summary, \n or click "Create Custom Mapper" to open the custom mapping window.',font=('Courier New', 10))],
    
    # --- Control and Input Row ---
    [
        sg.Button('Open README', key='README_KEY'),
        sg.Button('Refresh Current Mappers', key='VALIDATE_KEY'),
        sg.Button('Create Custom Mapper', key='CUSTOM_MAPPER_KEY'),
        # sg.Text('Mod Name:'), 
        # sg.Input(key='MOD_NAME_KEY', size=(20, 1)), # Input for the Mod Name
        # sg.Text('Mod ID:'), 
        # sg.Input(key='MOD_ID_KEY', size=(10, 1)),   # Input for the Mod ID
        # sg.Button('Add/Show Mods', key='ADD_MOD_KEY'),      # Button to trigger the addition
        # sg.Button('Clear Mods', key='CLEAR_MOD_KEY')       # Button to clear mods
    ],
    
    # --- Output Multiline Field ---
    [
        sg.Multiline(
            TEXT,
            enable_events=False,
            size=(80, 25),
            font=('Courier New', 10),
            horizontal_scroll=True,
            expand_x=True,
            expand_y=True,
            disabled=True,
            key='MLINE_KEY'
        )
    ]
]

    window = sg.Window('Crusader Wars Mapper', layout, resizable=True).Finalize()

    # Executable compatibility check
    try:
        if os.path.exists(os.path.join(CW_DIR, 'Crusader Wars.exe')):
            pass
        else:
            raise FileNotFoundError('Executable incompatibility or not found for Crusader Wars.exe')
    except FileNotFoundError as e:
        sg.popup_error(f"Error: {e}\n\nPlease ensure the Crusader Wars mapping tool is stored in tools/cw_mapper")
        window.close()
    except Exception as e:
        sg.popup_error(f"Error: {e}")
        window.close()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break

        elif event == 'README_KEY':
            webbrowser.open("readme.txt")
        
        # elif event == 'ADD_MOD_KEY':
        #     window['MLINE_KEY'].update('')
        #     mod_name = values['MOD_NAME_KEY'].strip()
        #     mod_id = values['MOD_ID_KEY'].strip()
        
        #     if mod_name and mod_id:
        #         MOD_LIST.append((mod_name, mod_id))
        #         window['MOD_NAME_KEY'].update('') # Clear the input field
        #         window['MOD_ID_KEY'].update('')   # Clear the input field
                
        #         # Log the addition to the Multiline
        #         window["MLINE_KEY"].update(f'Added Mod: {mod_name} (ID: {mod_id})\n', append=True)
        #         window["MLINE_KEY"].update(f'Additional mods list: \n', append=True)
        #         window["MLINE_KEY"].update(f'{MOD_LIST}', append=True)
        #     else:
        #         window["MLINE_KEY"].update('Both Mod Name and Mod ID must be entered.\n', append=True)
        #         window["MLINE_KEY"].update(f'Additional mods list: \n', append=True)
        #         window["MLINE_KEY"].update(f'{MOD_LIST}', append=True)
        
        # elif event == 'CLEAR_MOD_KEY':
        #     MOD_LIST.clear()
        #     window['MLINE_KEY'].update('')
        #     window["MLINE_KEY"].update('Additional mod list cleared.\n', append=True)
        #     window["MLINE_KEY"].update(f'Additional mods list: \n', append=True)
        #     window["MLINE_KEY"].update(f'{MOD_LIST}', append=True)

        elif event == 'VALIDATE_KEY':
            window['MLINE_KEY'].update('')
            # Disable validation button
            window['VALIDATE_KEY'].update(disabled=True)

            os.makedirs(ATTILA_EXPORT_DIR, exist_ok=True)
            if not any(file.endswith('.tsv') for file in os.listdir(ATTILA_EXPORT_DIR)):
                window['MLINE_KEY'].update(f'ERROR: No .tsv Atilla unit keys were found in {ATTILA_EXPORT_DIR}\n')
                window['MLINE_KEY'].update(f'\n',append=True)
                window['MLINE_KEY'].update(f'''1. Use a tool like **PFM/RPFM** to export the unit database files (`db/main_units_tables`) from **Attila** as **`.tsv`** files.\n''',append=True)
                window['MLINE_KEY'].update('''2. Place these exported `.tsv` files into this tool's subfolder: **`attila_exports/db/main_units_tables/`**.\n''',append=True)
                window['MLINE_KEY'].update('''You may need to create this subfolder.\n''',append=True)
                window['MLINE_KEY'].update('''> **Tip:** You may need to rename the `.tsv` files if you export from multiple Attila sources to prevent overwriting.\n''',append=True)
                window['MLINE_KEY'].update(f'\n',append=True)
                window['MLINE_KEY'].update(f'''Click the 'Open README' button for more details.''',append=True)
                window['VALIDATE_KEY'].update(disabled=False)
            else:
                init_map_config()
                cw_map_checker.mapping_validation(*cw_map_checker.get_keys(cw_map_checker.get_cw_config()))
                cw_map_checker.summary()

                window['MLINE_KEY'].update(f'*** Crusader Wars mappers refreshed! \n', append=True)
                window['MLINE_KEY'].update(f'\n',append=True)
                if os.path.exists(SUMMARY_LOG):
                    with open(SUMMARY_LOG, 'r', encoding="utf-8-sig") as f:
                        new_summary = f.read()
                else:
                    new_summary = "ERROR: Could not read summary_log.txt"
                window['MLINE_KEY'].update(f'{new_summary}',append=True)
                window['VALIDATE_KEY'].update(disabled=False)

        elif event == 'CUSTOM_MAPPER_KEY':
                mapping_window()

    window.close()

if __name__ == '__main__':
        main_window()