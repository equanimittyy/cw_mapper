'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import sys

import csv
import re
import json
import webbrowser
import FreeSimpleGUI as sg

import cw_map_checker

from utils import init_map_config, import_xml, export_xml, add_map_config

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

CONFIG = os.path.join('config','mod_config.json')

# Key sources
ATTILA_SOURCE_KEYS = []
CULTURES_SOURCE_KEYS = []
MAA_SOURCE_KEYS = []
TITLE_SOURCE_KEYS = []

ATTILA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv')
CULTURES_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures_keys.csv')
MAA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa_keys.csv')
TITLE_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR,'source_ck3_title_keys.csv')

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

DEFAULT_LEVY_PERCENTAGES = {
    'LEVY-SPEAR':50,
    'LEVY-SWORD':25,
    'LEVY-ARCHER':25,
    'LEVY-SKIRM':0,
    'LEVY-CAV':0,
    'LEVY-CUSTOM1':0,
    'LEVY-CUSTOM2':0,
    'LEVY-CUSTOM3':0
}

# If none of the source files exists, run the check program to refresh files
init_map_config()
try:
    cw_map_checker.mapping_validation(*cw_map_checker.get_keys(cw_map_checker.get_cw_config()))
    cw_map_checker.summary()
except (FileNotFoundError, SystemExit, Exception) as e:
    print(f'Warning: Initial validation could not complete: {e}')
    print('The GUI will still load. Use "Refresh Current Mappers" to retry.')

if os.path.exists(ATTILA_SOURCE_PATH):
    with open (ATTILA_SOURCE_PATH, 'r') as f:
        key_data = csv.DictReader(f)
        for key in key_data:
            ATTILA_SOURCE_KEYS.append({'attila_map_key':key['attila_map_key'],'attila_source':key['attila_source']})

if os.path.exists(CULTURES_SOURCE_PATH):
    with open(CULTURES_SOURCE_PATH, 'r') as f:
        key_data = csv.DictReader(f)
        for key in key_data:
            CULTURES_SOURCE_KEYS.append({'ck3_culture':key['ck3_culture'],'heritage':key['ck3_heritage'],'ck3_source':key['ck3_source']})

if os.path.exists(MAA_SOURCE_PATH):
    with open(MAA_SOURCE_PATH, 'r') as f:
        key_data = csv.DictReader(f)
        for key in key_data:
            MAA_SOURCE_KEYS.append({'ck3_maa':key['ck3_maa'],'ck3_source':key['ck3_source']})

if os.path.exists(TITLE_SOURCE_PATH):
    with open(TITLE_SOURCE_PATH, 'r') as f:
        key_data = csv.DictReader(f)
        for key in key_data:
            TITLE_SOURCE_KEYS.append({'title_key':key['title_key'],'title_rank':key['title_rank'],'ck3_source':key['ck3_source']})

for maa in NON_MAA_KEYS:
    MAA_SOURCE_KEYS.append({'ck3_maa':maa,'ck3_source':'CW'})

TITLE_NON_MAA_KEYS = ['GENERAL', 'KNIGHTS']

ATTILA_SOURCES = [item['attila_source'] for item in ATTILA_SOURCE_KEYS]
CK3_SOURCES = [item['ck3_source'] for item in CULTURES_SOURCE_KEYS] + [item['ck3_source'] for item in MAA_SOURCE_KEYS]
TITLE_SOURCES = [item['ck3_source'] for item in TITLE_SOURCE_KEYS]

def popup_mods_config(mods):
    cur_CK3_mods = [v for k,v in mods.items() if k == 'CK3']
    cur_ATTILA_mods = [v for k,v in mods.items() if k == 'Attila']

    display_CK3_mods = ''
    display_ATTILA_mods = ''

    if cur_CK3_mods:
        for v in cur_CK3_mods[0]:
            display_CK3_mods += v+'\n'
    if cur_ATTILA_mods:
        for v in cur_ATTILA_mods[0]:
            display_ATTILA_mods += v+'\n'
    
    ck3_col = [[sg.Text('CK3 Mod List', font=('Courier New', 12, 'bold'), text_color='#6D0000', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE, justification='center')],
               [sg.Text('(No load order, one item per line)\nFormat: "Mod Name":"Workshop ID"\nExample: "RICE:2273832430"', font=('Courier New', 10, 'bold'), text_color="#000000", background_color='#DDDDDD', justification='center')],
               [sg.Multiline(display_CK3_mods, size=(50, 20), key='CK3_MODS_LIST', expand_x=True, expand_y=True)]]
    attila_col = [[sg.Text('Attila Mod List', font=('Courier New', 12, 'bold'), text_color='#006D00', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE, justification='center')],
                [sg.Text('(Load order: Bottom is priority, one item per line)\nFormat: ".pack Name"\nExample: "@@ad_919_1.pack"', font=('Courier New', 10, 'bold'), text_color="#000000", background_color='#DDDDDD', justification='center')],
                [sg.Multiline(display_ATTILA_mods, size=(50, 20), key='ATTILA_MODS_LIST', expand_x=True, expand_y=True)]]

    layout = [
        [sg.Column(ck3_col, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD', expand_x=True, expand_y=True), sg.Column(attila_col, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD', expand_x=True, expand_y=True)],
        [sg.Button('OK', size=(15, 2), button_color=('white', '#444444')), sg.Button('Cancel', size=(15, 2), button_color=('white', '#444444'))]
    ]

    window = sg.Window('Edit mapper mod configuration', layout, element_justification='center', modal=True, resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Cancel':
            break

        elif event == 'OK':
            new_mods = {}
            new_CK3_mods = values['CK3_MODS_LIST'].splitlines()
            new_CK3_mods = [mod.strip() for mod in new_CK3_mods if mod.strip()]

            new_ATTILA_mods = values['ATTILA_MODS_LIST'].splitlines()
            new_ATTILA_mods = [mod.strip() for mod in new_ATTILA_mods if mod.strip()]
            
            new_mods['CK3'] = new_CK3_mods
            new_mods['Attila'] = new_ATTILA_mods
            window.close()
            return new_mods
    window.close()

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

def popup_levy_percentage(faction, data):
    headings = ['Levy','Unit_Key','Percentage']
    percentage_total = sum([int(row[2]) for row in data])
    layout = [
        [sg.Text(f'Total must add up to 100% or crashes will occur:\n\n{faction}')],
        [sg.Table(
            values=data,
            headings=headings,
            key='LEVY_PERCENTAGE_TABLE',
            max_col_width=30,          
            auto_size_columns=True,
            justification='left',
            num_rows=min(20, len(data)),
            row_height=25,
            enable_events=True
        )],
        [sg.HSeparator()],
        [sg.Text('Edit Selected Row: ', key='LEVY_SELECT_TEXT')],
        # Input fields for editing the data
        [sg.Text('Percentage %:  '), sg.Input(size=(10, 1), key='LEVY_PERCENTAGE_INPUT'),sg.Text(f'Total: {percentage_total}%', key='TOTAL_KEY')],
        [sg.Button('Update Row', key='UPDATE_LEVY'), sg.Button('Exit')]
    ]

    window = sg.Window('Edit levy percentages', layout, modal=True, finalize=True, resizable=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            window.close()
            return data

        elif event == 'LEVY_PERCENTAGE_TABLE':
            if values['LEVY_PERCENTAGE_TABLE']: # Check if a row is actually selected
                selected_row_index = values['LEVY_PERCENTAGE_TABLE'][0]
                current_row_data = data[selected_row_index]
                
                # Update the Input fields with the selected row's data
                window['LEVY_SELECT_TEXT'].update(f'Edit Selected Row: {current_row_data[0]}')
                window['LEVY_PERCENTAGE_INPUT'].update(current_row_data[2])

        if event == 'UPDATE_LEVY':
            if values['LEVY_PERCENTAGE_TABLE']:
                selected_row_index = values['LEVY_PERCENTAGE_TABLE'][0]
                
                # Get the new values from the Input fields
                try:
                    new_percentage = int(values['LEVY_PERCENTAGE_INPUT'])
                except (ValueError, TypeError):
                    sg.popup_error('Please enter a valid number for the percentage.')
                    continue

                # Update the data structure
                data[selected_row_index][2] = new_percentage
                
                # Crucial Step: Update the sg.Table element to show the new data
                percentage_total = sum([row[2] for row in data])
                window['TOTAL_KEY'].update(f'Total: {percentage_total}%')
                window['LEVY_SELECT_TEXT'].update(f'Edit Selected Row: ')
                window['LEVY_PERCENTAGE_INPUT'].update('')
                window['LEVY_PERCENTAGE_TABLE'].update(values=data)

            else:
                sg.popup_error('Please select a row in the table first.')

def popup_missing_keys(missing_keys):
    headings = ['Missing Key', 'Type and Source']
    layout = [
        [sg.Text("This is a list of missing keys that the currently loaded mapper is referencing, but not found in your files:\n\nIt is very likely that the missing source comes from a mod you currently do not have installed, or an Attila key you don't have exported.")],
        [sg.Table(
            values=missing_keys,
            headings=headings,
            key='LEVY_PERCENTAGE_TABLE',
            max_col_width=30,          
            auto_size_columns=True,
            justification='left',
            num_rows=min(20, len(missing_keys)),
            row_height=25,
            expand_x=True
        )]
    ]

    window = sg.Window('Missing mapper keys', layout, modal=True, resizable=True)
    event, values = window.read(close=True) # Closes the window after reading the event

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

def popup_help_guide():
    guide_text = (
        "GETTING STARTED\n"
        "===============\n"
        "The Custom Unit Mapper lets you create unit mappings between CK3 and Total War: Attila.\n"
        "The window has three columns:\n"
        "  - Left: CK3 Man-at-Arms keys (including special types like GENERAL, KNIGHTS, LEVY)\n"
        "  - Middle: Attila unit keys (the TW:A units to map to)\n"
        "  - Right: Your current mappings for the selected faction\n\n"

        "FACTION MAPPING (Main Window)\n"
        "=============================\n"
        "Each mapping links a CK3 MAA type to an Attila unit, organised by FACTION.\n"
        "A faction represents a group of units (e.g. 'Western European', 'Norse').\n\n"
        "To create a mapping:\n"
        "  1. Select a Faction from the dropdown (or create one via 'Edit faction list')\n"
        "  2. Click a CK3 MAA key from the left list\n"
        "  3. Click an Attila unit key from the middle list\n"
        "  4. Choose a unit size (INFANTRY, CAVALRY, RANGED, or a manual number)\n"
        "  5. Click 'Add Mapping'\n\n"
        "Special unit types (GENERAL, KNIGHTS, LEVY-*) are listed at the top of the CK3 list.\n"
        "  - GENERAL: The commander unit for a faction (one per faction)\n"
        "  - KNIGHTS: The knight unit for a faction (one per faction)\n"
        "  - LEVY-*: Levy units with percentage allocations that must total 100% per faction\n"
        "    Use 'Edit levy percentages' to adjust the split\n\n"
        "You can copy all mappings from one faction to another using 'Copy from faction'.\n\n"

        "HERITAGE MAPPING\n"
        "================\n"
        "Click 'Open Heritage mapping' to assign CK3 heritages/cultures to your factions.\n"
        "This determines which faction's units a culture uses in battle.\n\n"
        "  - A HERITAGE is a group of cultures (e.g. 'West Germanic' contains English, Dutch, etc.)\n"
        "  - You can assign a faction at the heritage level (all cultures inherit it)\n"
        "  - Or override individual cultures within a heritage to use a different faction\n"
        "  - Assign a faction to a heritage key to assign to all cultures with that heritage (overriden by culture level faction overides)\n\n"

        "TITLE MAPPING\n"
        "=============\n"
        "Click 'Open Title mapping' to create title-specific unit overrides.\n"
        "Title mappings let specific empires, kingdoms, or duchies use different units\n"
        "than their culture's default faction would give them.\n\n"
        "  - Title mappings support GENERAL, KNIGHTS, and MenAtArm types only (no levies)\n"
        "  - These override the faction mapping for holders of that title\n\n"

        "SAVING & LOADING\n"
        "================\n"
        "  - 'Save': Saves your mapper as a .txt file (JSON format) in the custom_mappers/ folder.\n"
        "    This is the working format for this tool. Use Save/Load to continue editing later.\n"
        "  - 'Load': Loads a previously saved .txt mapper file to continue editing.\n\n"

        "IMPORTING & EXPORTING XML\n"
        "=========================\n"
        "  - 'Import/Export XML' opens a dialog to convert between this tool and Crusader Wars.\n"
        "  - IMPORT: Reads an existing CW mapper folder (with Factions/, Cultures/, etc.) and\n"
        "    converts it into this tool's format so you can edit it. Use this to modify an\n"
        "    existing official or community mapper.\n"
        "  - EXPORT: Converts your saved mapper into the XML folder structure that Crusader Wars\n"
        "    actually reads (Factions/, Cultures/, Titles/, Mods.xml, etc.).\n"
        "    Export when your mapper is ready to be used in-game.\n\n"
        "  Save/Load = working format for editing | Import/Export XML = game-ready format for CW\n\n"

        "MOD CONFIGURATION\n"
        "=================\n"
        "Click 'Mod configuration' to set which CK3 mods and Attila .pack files your\n"
        "mapper requires. This is written into the exported Mods.xml for Crusader Wars and used\n"
        "when validating your mapper(s) in the tool's report window."
    )

    layout = [
        [sg.Text('Custom Mapper Instructions', font=('Courier New', 14, 'bold'))],
        [sg.Multiline(
            guide_text,
            size=(90, 35),
            font=('Courier New', 10),
            disabled=True,
            expand_x=True,
            expand_y=True,
            background_color='#F5F5F5',
            text_color='#000000'
        )],
        [sg.Button('Close', size=(10, 1))]
    ]
    window = sg.Window('Mapper Help Guide', layout, modal=True, resizable=True, element_justification='center')
    while True:
        event, _ = window.read()
        if event in (sg.WIN_CLOSED, 'Close'):
            break
    window.close()

def popup_xml_import_export(config):
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
                imported_maa_map, imported_heritage_map, imported_mods, imported_title_map, imported_title_names = import_xml(import_folder)
                # Finally, add to imported_mods if the name of mod is found in config
                with open(config, 'r') as f:
                    data = json.load(f)
                    ck3_mods_match = [v for k,v in data.items() if k == mapper_name]
                    imported_mods['CK3'] = []
                    if not ck3_mods_match:
                        sg.popup(f"Note: No CK3 mod configuration found for '{mapper_name}' in config.\nYou can configure mods after loading the mapper.")
                    else:
                        ck3_mods = ck3_mods_match[0]
                        for mod in ck3_mods:
                            imported_mods['CK3'] += [mod[0]+':'+str(mod[1])]

                sg.popup(f"Mapper '{mapper_name}' imported!\n\nLoad the mapper using the 'Load' button")
                window.close()
                return mapper_name, imported_maa_map, imported_heritage_map, imported_mods, imported_title_map, imported_title_names

    if event == 'Export':
        export_mapper_file = sg.popup_get_file(title='Find mapper file to export',message='Please select the mapping file you wish to export',initial_folder=CUSTOM_MAPPER_DIR)
        if export_mapper_file:
            tag = sg.popup_get_text(title='Assign mod tag',message='Define a tag used for your mapper set, which can be used to identify\nmulti-mappers for different time periods')
            s_date = sg.popup_get_text(title='Define start date',message='Define the start date (please enter numbers only, e.g.: 768)',default_text='0')
            e_date = sg.popup_get_text(title='Define end date',message='Define the end date (please enter numbers only, e.g.: 768)',default_text='9999')
            export_dir = export_xml(export_mapper_file, NON_MAA_KEYS, tag, s_date, e_date)
            sg.popup(f"Mapper exported to '{export_dir}'!")
            window.close()
    return None

def popup_title_pick(current_title_list, current_title_names):
    available_titles = [item['title_key'] for item in TITLE_SOURCE_KEYS if item['title_key'] not in current_title_list]
    rank_filter = ['ALL','Empire','Kingdom','Duchy']

    current_display = [f'{t} ({current_title_names.get(t, t)})' for t in current_title_list]

    add_col = [
        [sg.Text('Available Titles', font=('Courier New', 11, 'bold'), text_color='#006D00', background_color='#DDDDDD', relief=sg.RELIEF_RIDGE)],
        [sg.Text('Filter by rank:'), sg.Combo(
            values=rank_filter,
            default_value='ALL',
            size=(15, 1),
            key='TITLE_RANK_FILTER',
            readonly=True,
            enable_events=True
        ), sg.Text('Search:'), sg.Input(key='TITLE_SEARCH', enable_events=True, size=(25,1))],
        [sg.Listbox(
            values=sorted(available_titles),
            size=(40, 15),
            key='TITLE_AVAILABLE_LIST',
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            expand_x=True,
            expand_y=True
        )],
        [sg.Button('Add Title', size=(15, 2), button_color=('white', '#004D40'))]
    ]

    current_col = [
        [sg.Text('Current Titles', font=('Courier New', 11, 'bold'), text_color='#6D0000', background_color='#DDDDDD', relief=sg.RELIEF_RIDGE)],
        [sg.Listbox(
            values=current_display,
            size=(40, 15),
            key='TITLE_CURRENT_LIST',
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            enable_events=True,
            expand_x=True,
            expand_y=True
        )],
        [sg.Button('Remove Selected', size=(15, 2), button_color=('white', '#CC0000'), key='TITLE_REMOVE_BTN')]
    ]

    layout = [
        [sg.Text('Add or remove title keys for your title mapping')],
        [sg.Column(add_col, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD', expand_x=True, expand_y=True),
         sg.VSeparator(),
         sg.Column(current_col, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD', expand_x=True, expand_y=True)],
        [sg.Button('Done', size=(15, 2), button_color=('white', '#444444'))]
    ]

    window = sg.Window('Edit title list', layout, modal=True, resizable=True)
    added_titles = {}  # {title_key: display_name}
    removed_titles = []

    def refresh_available(window, values):
        rank = values['TITLE_RANK_FILTER']
        search = values['TITLE_SEARCH'].lower()
        all_current = current_title_list + list(added_titles.keys())
        all_current = [t for t in all_current if t not in removed_titles]
        filtered = [item['title_key'] for item in TITLE_SOURCE_KEYS if item['title_key'] not in all_current]
        if rank != 'ALL':
            filtered = [t for t in filtered if any(item['title_key'] == t and item['title_rank'] == rank for item in TITLE_SOURCE_KEYS)]
        if search:
            filtered = [t for t in filtered if search in t.lower()]
        window['TITLE_AVAILABLE_LIST'].update(sorted(filtered))

    def refresh_current(window):
        remaining = [t for t in current_title_list if t not in removed_titles]
        display = [f'{t} ({current_title_names.get(t, t)})' for t in remaining]
        display += [f'{t} ({added_titles[t]})' for t in added_titles]
        window['TITLE_CURRENT_LIST'].update(sorted(display))

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Done':
            break

        elif event == 'TITLE_RANK_FILTER' or event == 'TITLE_SEARCH':
            refresh_available(window, values)

        elif event == 'Add Title':
            selected = values['TITLE_AVAILABLE_LIST']
            if selected:
                title_key = selected[0]
                display_name = popup_title_name(title_key)
                if display_name is None:
                    continue
                added_titles[title_key] = display_name
                refresh_available(window, values)
                refresh_current(window)

        elif event == 'TITLE_REMOVE_BTN':
            selected = values['TITLE_CURRENT_LIST']
            if selected:
                for item in selected:
                    title_key = item.split(' (')[0]
                    if title_key in added_titles:
                        del added_titles[title_key]
                    elif title_key in current_title_list:
                        removed_titles.append(title_key)
                refresh_available(window, values)
                refresh_current(window)

    window.close()
    return added_titles, removed_titles

def popup_title_name(title_key):
    layout = [
        [sg.Text(f'Enter a display name for title: {title_key}')],
        [sg.Input(
            default_text=title_key,
            key='TITLE_NAME_INPUT'
        )],
        [sg.Button('OK'), sg.Button('Cancel')]
    ]

    window = sg.Window('Title display name', layout, modal=True)
    event, values = window.read(close=True)

    if event == 'OK':
        name = values['TITLE_NAME_INPUT']
        if name:
            return name
        return title_key
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
            if isinstance(item[0], tuple):
                sort_key = item[0]
                heritage = sort_key[0]
                culture = sort_key[1] 
            else:
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
        h_count = 0
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
        h_count = 0
        parent_faction = ''
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
            if matching_heritage == [''] or matching_heritage == []:
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
        [sg.Text('''⚠️ Important: It is highly recommended to manually map "Unassigned"\ncultures after export, as they're not specifically tied to a heritage\nand cannot fall back on heritage "Unassigned" (it doesn't exist in-game)''')],
        [sg.Listbox(
            values=available_heritages_display_list,
            size=(50, 20),
            key='HERITAGE_AVAILABLE_LIST',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            tooltip='Available list of heritages and their associated cultures.\nCultures that were not found in your sources are assigned to "Unassigned" and have source (None)\n\nYou can also press spacebar to quickly select with the arrow keys.',
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
            tooltip='Your list of heritages and cultures, with their associated factions.\nCultures that were not found in your sources are assigned to "Unassigned" and have source (None)\n\nYou can also press spacebar to quickly select with the arrow keys.',
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

    window = sg.Window('Edit heritage mapping', layout, modal=True, finalize=True, resizable=True)

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

def title_window(title_mapping_dict, title_names_dict):
    ATTILA_UNIT_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(ATTILA_SOURCES)))
    # For title mapping, only show regular MAA + GENERAL + KNIGHTS (no levies)
    TITLE_MAA_KEYS = [item for item in MAA_SOURCE_KEYS if item['ck3_maa'] not in NON_MAA_KEYS or item['ck3_maa'] in TITLE_NON_MAA_KEYS]
    MAA_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys([item['ck3_source'] for item in TITLE_MAA_KEYS])))
    SIZE_LIST = ['MANUAL','CAVALRY','INFANTRY','RANGED']

    TITLE_LIST = list(title_names_dict.keys()) if title_names_dict else []

    selected_ck3 = None
    selected_attila = None
    current_title = TITLE_LIST[0] if TITLE_LIST else ''

    def update_title_mappings_list(window, mappings_dict):
        mapping_widget = window['TITLE_MAPPING_LIST_KEY'].Widget
        current_y = mapping_widget.yview()[0]

        display_list = []
        formatted_list = []
        for (ck3, title_key), attila in mappings_dict.items():
            display_list = [t for t in mappings_dict.items() if t[0][1] == current_title]
        if display_list:
            for (ck3, title_key), attila in display_list:
                title_name = title_names_dict.get(title_key, title_key)
                formatted_list.append(f"[{title_name}] {ck3}   => {attila}")
        else:
            formatted_list = []

        window['TITLE_MAPPING_LIST_KEY'].update(sorted(formatted_list), visible=False)
        mapping_widget.yview_moveto(current_y)
        window['TITLE_MAPPING_LIST_KEY'].update(visible=True)
        window['TITLE_REMOVE_MAPPING_KEY'].update(disabled=len(formatted_list) == 0)

    def check_title_add_button(window, values):
        is_ready = selected_ck3 is not None and selected_attila is not None and current_title != ''
        window['TITLE_ADD_MAPPING_KEY'].update(disabled=not is_ready)

    # Column 1: CK3 MAA Selector (no levies)
    col1_layout = [
        [sg.Text('Available CK3 MAA (No Levies)', font=('Courier New', 12, 'bold'), text_color='#6D0000', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE),
         sg.Text('Filter CK3 source:'), sg.Combo(
            values=MAA_LIST_SOURCE,
            default_value=MAA_LIST_SOURCE[0],
            size=(20, 1),
            key='TITLE_CK3_SOURCE_KEY',
            readonly=True,
            enable_events=True
        )],
        [sg.Text('Search...',background_color='#DDDDDD',text_color="#000000"),sg.Input(key='TITLE_CK3_SEARCH_KEY', enable_events=True)],
        [sg.Listbox(
            values=sorted([item['ck3_maa'] for item in TITLE_MAA_KEYS]),
            size=(30, 15),
            key='TITLE_CK3_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected CK3:', size=(25, 1), key='TITLE_SELECTED_CK3_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN, expand_x=True, justification='center')]
    ]

    # Column 2: ATTILA UNIT KEY Selector (no LEVY size option)
    col2_layout = [
        [sg.Text('Available ATTILA UNIT KEYS', font=('Courier New', 12, 'bold'), text_color='#006D00', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE),
         sg.Text('Filter Attila source:'), sg.Combo(
            values=ATTILA_UNIT_LIST_SOURCE,
            default_value=ATTILA_UNIT_LIST_SOURCE[0],
            size=(20, 1),
            key='TITLE_ATTILA_SOURCE_KEY',
            readonly=True,
            enable_events=True
        )],
        [sg.Text('Search...',background_color='#DDDDDD',text_color="#000000"),sg.Input(key='TITLE_ATTILA_SEARCH_KEY', enable_events=True),sg.Text('Select unit size:'), sg.Combo(
            values=SIZE_LIST,
            default_value=SIZE_LIST[0],
            size=(10, 1),
            key='TITLE_MAA_SIZE_SELECT',
            readonly=True,
            enable_events=True
        )],
        [sg.Listbox(
            values=sorted([item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]),
            size=(30, 15),
            key='TITLE_ATTILA_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected ATTILA:', size=(25, 1), key='TITLE_SELECTED_ATTILA_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN, expand_x=True, justification='center')]
    ]

    # Column 3: Title Mapping Editor
    col3_layout = [
        [sg.Text('Title-Based Unit Mapping', font=('Courier New', 12, 'bold'), text_color='#00006D', background_color='#DDDDDD',relief=sg.RELIEF_RIDGE)],
        [sg.Text('Select Title:'), sg.Combo(
            values=TITLE_LIST,
            default_value=current_title,
            size=(30, 1),
            key='TITLE_SELECT_KEY',
            readonly=True,
            enable_events=True
        ), sg.Push(background_color='#DDDDDD'), sg.Button('Edit title list', key='TITLE_LIST_EDIT_KEY', size=(15, 2), button_color=('white', '#444444'))],
        [sg.Listbox(
            values=[],
            size=(35, 13),
            key='TITLE_MAPPING_LIST_KEY',
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            background_color='#E8E8FF',
            expand_x=True,
            expand_y=True,
            enable_events=True
        )],
        [sg.Button('Add Mapping', key='TITLE_ADD_MAPPING_KEY', size=(15, 2), button_color=('white', '#004D40'), disabled=True),
         sg.Button('Remove Selected', key='TITLE_REMOVE_MAPPING_KEY', size=(15, 2), button_color=('white', '#CC0000'), disabled=True),
         sg.Push(background_color='#DDDDDD'),
         sg.Button('OK', key='TITLE_OK_KEY', size=(15, 2), button_color=('white', '#444444'))]
    ]

    layout = [
        [sg.Text('Map CK3 MAA to Attila units per TITLE. Levies do NOT participate in title mapping.\nEvery unit MUST have a unit key (no DEFAULT fallback).', font=('Courier New', 10, 'bold'), justification='center', expand_x=True)],
        [
            sg.Column(col1_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col2_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col3_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True)
        ]
    ]

    window = sg.Window('Title-Based Unit Mapping', layout, finalize=True, element_justification='center', resizable=True, modal=True)

    if title_mapping_dict:
        update_title_mappings_list(window, title_mapping_dict)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            break

        elif event == 'TITLE_CK3_LIST_KEY':
            if values['TITLE_CK3_LIST_KEY']:
                selected_ck3 = values['TITLE_CK3_LIST_KEY']
                if len(selected_ck3) > 1:
                    window['TITLE_SELECTED_CK3_KEY'].update(f'Selected CK3: Multiple', background_color='#F5962A')
                else:
                    window['TITLE_SELECTED_CK3_KEY'].update(f'Selected CK3: {selected_ck3}', background_color='#F5962A')
            else:
                selected_ck3 = None
                window['TITLE_SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
            check_title_add_button(window, values)

        elif event == 'TITLE_ATTILA_LIST_KEY':
            if values['TITLE_ATTILA_LIST_KEY']:
                selected_attila = values['TITLE_ATTILA_LIST_KEY']
                window['TITLE_SELECTED_ATTILA_KEY'].update(f'Selected ATTILA: {selected_attila}', background_color="#F5962A")
            else:
                selected_attila = None
                window['TITLE_SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')
            check_title_add_button(window, values)

        elif event == 'TITLE_SELECT_KEY':
            current_title = values['TITLE_SELECT_KEY']
            update_title_mappings_list(window, title_mapping_dict)
            check_title_add_button(window, values)

        elif event == 'TITLE_CK3_SOURCE_KEY':
            current_ck3_source = values['TITLE_CK3_SOURCE_KEY']
            search_term = values['TITLE_CK3_SEARCH_KEY']
            if current_ck3_source == 'ALL':
                new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS]
                if search_term:
                    new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if search_term.lower() in item['ck3_maa'].lower()]
            else:
                new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if item['ck3_source'] == current_ck3_source]
                if search_term:
                    new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if search_term.lower() in item['ck3_maa'].lower() and item['ck3_source'] == current_ck3_source]
            window['TITLE_CK3_LIST_KEY'].update(sorted(new_list))

        elif event == 'TITLE_ATTILA_SOURCE_KEY':
            current_att_source = values['TITLE_ATTILA_SOURCE_KEY']
            search_term = values['TITLE_ATTILA_SEARCH_KEY']
            if current_att_source == 'ALL':
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]
                if search_term:
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower()]
            else:
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if item['attila_source'] == current_att_source]
                if search_term:
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower() and item['attila_source'] == current_att_source]
            window['TITLE_ATTILA_LIST_KEY'].update(sorted(new_list))

        elif event == 'TITLE_CK3_SEARCH_KEY':
            current_ck3_source = values['TITLE_CK3_SOURCE_KEY']
            search_term = values['TITLE_CK3_SEARCH_KEY']
            if current_ck3_source == 'ALL':
                new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS]
                if search_term:
                    new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if search_term.lower() in item['ck3_maa'].lower()]
            else:
                new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if item['ck3_source'] == current_ck3_source]
                if search_term:
                    new_list = [item['ck3_maa'] for item in TITLE_MAA_KEYS if search_term.lower() in item['ck3_maa'].lower() and item['ck3_source'] == current_ck3_source]
            window['TITLE_CK3_LIST_KEY'].update(sorted(new_list))

        elif event == 'TITLE_ATTILA_SEARCH_KEY':
            current_att_source = values['TITLE_ATTILA_SOURCE_KEY']
            search_term = values['TITLE_ATTILA_SEARCH_KEY']
            if current_att_source == 'ALL':
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS]
                if search_term:
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower()]
            else:
                new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if item['attila_source'] == current_att_source]
                if search_term:
                    new_list = [item['attila_map_key'] for item in ATTILA_SOURCE_KEYS if search_term.lower() in item['attila_map_key'].lower() and item['attila_source'] == current_att_source]
            window['TITLE_ATTILA_LIST_KEY'].update(sorted(new_list))

        elif event == 'TITLE_ADD_MAPPING_KEY' and selected_ck3 and selected_attila:
            if current_title:
                size = values['TITLE_MAA_SIZE_SELECT']
                if size == 'MANUAL':
                    size = popup_size_manual()
                for selected in selected_ck3:
                    mapping_key = (selected, current_title)

                    if mapping_key in title_mapping_dict:
                        del title_mapping_dict[mapping_key]

                    override_size = ''
                    if re.search(r'^GENERAL\b', mapping_key[0]):
                        override_size = 'GENERAL'
                    if re.search(r'^KNIGHTS\b', mapping_key[0]):
                        override_size = 'KNIGHTS'

                    if override_size:
                        title_mapping_dict[mapping_key] = selected_attila + [override_size]
                    else:
                        title_mapping_dict[mapping_key] = selected_attila + [size]

                    update_title_mappings_list(window, title_mapping_dict)
                    check_title_add_button(window, values)

                selected_ck3 = None
                selected_attila = None
                window['TITLE_CK3_LIST_KEY'].update(set_to_index=[])
                window['TITLE_ATTILA_LIST_KEY'].update(set_to_index=[])
                window['TITLE_SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
                window['TITLE_SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')

        elif event == 'TITLE_REMOVE_MAPPING_KEY':
            if values['TITLE_MAPPING_LIST_KEY']:
                for formatted_mapping in values['TITLE_MAPPING_LIST_KEY']:
                    if formatted_mapping.startswith('['):
                        parts = formatted_mapping.split('] ')
                        display_name = parts[0].strip('[')
                        ck3_key_to_remove = parts[1].split(' => ')[0].strip()
                        # Find title_key from display name
                        title_key_to_remove = current_title
                        for tk, tn in title_names_dict.items():
                            if tn == display_name:
                                title_key_to_remove = tk
                                break

                    key_to_remove = (ck3_key_to_remove, title_key_to_remove)
                    if key_to_remove in title_mapping_dict:
                        del title_mapping_dict[key_to_remove]
                        update_title_mappings_list(window, title_mapping_dict)

                window['TITLE_MAPPING_LIST_KEY'].update(set_to_index=[])

        elif event == 'TITLE_LIST_EDIT_KEY':
            added_titles, removed_titles = popup_title_pick(TITLE_LIST, title_names_dict)
            # Process added titles
            for title_key, display_name in added_titles.items():
                title_names_dict[title_key] = display_name
                TITLE_LIST.append(title_key)
            # Process removed titles
            for title_key in removed_titles:
                if title_key in TITLE_LIST:
                    TITLE_LIST.remove(title_key)
                if title_key in title_names_dict:
                    del title_names_dict[title_key]
                # Remove all mappings for this title
                keys_to_remove = [k for k in title_mapping_dict if k[1] == title_key]
                for k in keys_to_remove:
                    del title_mapping_dict[k]
            TITLE_LIST.sort()
            window['TITLE_SELECT_KEY'].update(values=TITLE_LIST)
            if current_title not in TITLE_LIST:
                current_title = TITLE_LIST[0] if TITLE_LIST else ''
                window['TITLE_SELECT_KEY'].update(value=current_title)
            update_title_mappings_list(window, title_mapping_dict)

        elif event == 'TITLE_OK_KEY':
            window.close()
            return title_mapping_dict, title_names_dict

    window.close()
    return title_mapping_dict, title_names_dict

def mapping_window():
    ATTILA_UNIT_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(ATTILA_SOURCES)))
    MAA_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(CK3_SOURCES)))

    FACTION_LIST = ['DEFAULT'] + [
    ]

    SIZE_LIST = ['MANUAL','CAVALRY','INFANTRY','RANGED']

    # Define global dictionaries of mappers to store the actual mappings (CK3 MAA: ATTILA UNIT KEY, per FACTION)
    # ==================================================
    MAPPER_NAME = ''
    # Format faction mapping: {(ck3_maa, faction): [attila_unit]} | {tuple: [value]}
    current_mappings = {}
    # Format heritage mapping: {heritage(faction,[culture[faction]]} | {key(value,list[value])}
    current_heritage_mappings = {}
    current_mods = {}
    # Format title mapping: {(ck3_maa, title_key): [attila_unit, size]} | {tuple: [value]}
    current_title_mappings = {}
    # Format title names: {title_key: display_name} | {str: str}
    current_title_names = {}
    # ==================================================

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
            expand_y=True,
            enable_events=True
        )],
        [sg.Button('Add Mapping', key='ADD_MAPPING_KEY', size=(15, 2), button_color=('white', '#004D40'), disabled=True),sg.Button('Remove Selected', key='REMOVE_MAPPING_KEY', size=(15, 2), button_color=('white', '#CC0000'), disabled=True),sg.Push(background_color='#DDDDDD'),sg.Button('Edit levy percentages', key='LEVY_PERCENTAGE_BUTTON_KEY',size=(20, 2), button_color=('white', "#444444")),sg.Button('Edit faction list', key='FACTION_LIST_EDIT_BUTTON_KEY', size=(15, 2), button_color=('white', '#444444')),sg.Button('Mod configuration', key='MOD_CONFIG_BUTTON', size=(15, 2), button_color=('white', '#444444'))],
        [sg.Button('Copy from faction', key='FACTION_COPY_BUTTON_KEY',size=(15, 2), button_color=('white', "#008670")),sg.Push(background_color='#DDDDDD'),sg.Button('Open Title mapping', key='TITLE_EDIT_BUTTON_KEY', size=(16, 2), button_color=('white', '#F78702')),sg.Button('Open Heritage mapping', key='HERITAGE_EDIT_BUTTON_KEY', size=(20, 2), button_color=('white', '#F78702'))]
    ]

    # Main layout
    mapper_layout = [
        [sg.Image(ASCII_ART_MAPPER)],
        [sg.Text('Create your "MAA => UNIT" mapping, per FACTION here. Each FACTION can have as many "MAA => UNIT" mappings as you like. Any missing "MAA => UNIT" mappings will fallback to faction DEFAULT, or crash if not present.', font=('Courier New', 10, 'bold'), justification='center', expand_x=True)],
        [sg.Column([[sg.Text('Each FACTION is assigned to one or many HERITAGE.', font=('Courier New', 10, 'bold'), key='SUBTEXT', justification='center'),sg.Button('⚠️ View missing keys', key='VIEW_MISSING_BUTTON', size=(20, 1), button_color=('white', "#CABD2E"), visible=False),sg.Button('? Help', key='HELP_GUIDE_BUTTON', size=(10, 1), button_color=('white', '#2266AA'))]],element_justification='center')],
        [
            sg.Column(col1_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col2_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col3_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True)
        ]
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

    def save_mapper(name, faction_mapping, heritage_mapping, mods, title_mapping=None, title_names=None):
        output_path = os.path.join(CUSTOM_MAPPER_DIR,f'{name}.txt')
        os.makedirs(CUSTOM_MAPPER_DIR, exist_ok=True)
        seperator = ','
        save_format = {
            'FACTIONS_AND_MAA': {
                seperator.join(k):v
                for k,v in faction_mapping.items()
                },
            'HERITAGES_AND_CULTURES': {
                seperator.join(k):[v]
                for k,v in heritage_mapping.items()
                },
            'TITLES_AND_MAA': {
                seperator.join(k):v
                for k,v in (title_mapping or {}).items()
                },
            'TITLE_NAMES': {
                k:v
                for k,v in (title_names or {}).items()
                },
            'MODS':{
                k:v
                for k,v in mods.items()
            }
        }
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(save_format,f,indent=4)

    def load_mapper(file):
        diff_message = ''
        maa_diff = 0
        attila_diff = 0
        heritage_diff = 0
        culture_diff = 0
        overall_diff = 0
        seperator = ','
        with open(file, 'r', encoding='utf-8-sig') as f:
            loaded_data = json.load(f)

        faction_data = loaded_data.get('FACTIONS_AND_MAA',{})
        heritage_data = loaded_data.get('HERITAGES_AND_CULTURES', {})
        mod_data = loaded_data.get('MODS',{})
        missing_keys = []

        loaded_faction_mapping = {
            tuple(k.split(seperator)):v
            for k, v in faction_data.items()
        }
        for k in loaded_faction_mapping.keys():
            maa = k[0]
            if maa not in NON_MAA_KEYS and maa not in [key['ck3_maa'] for key in MAA_SOURCE_KEYS]:
                maa_diff = 1
                if not re.search(r'^LEVY-', maa):
                    missing_keys.append([maa,'CK3 ManAtArms'])
        for v in loaded_faction_mapping.values():
            attila = v[0]
            if attila not in [key['attila_map_key'] for key in ATTILA_SOURCE_KEYS]:
                attila_diff = 1
                missing_keys.append([attila,'Attila Unit'])

        loaded_heritage_mapping = {
            tuple(k.split(seperator)):v[0]
            for k, v in heritage_data.items()
        }
        for k in loaded_heritage_mapping.keys():
            heritage = k[0]
            culture = k[1]
            if heritage not in [key['heritage'] for key in CULTURES_SOURCE_KEYS] and heritage != 'Unassigned':
                heritage_diff = 1
                missing_keys.append([heritage,'CK3 Heritage'])
            if culture != 'PARENT_KEY' and culture not in [key['ck3_culture'] for key in CULTURES_SOURCE_KEYS]:
                culture_diff = 1
                missing_keys.append([culture,'CK3 Culture'])

        loaded_mods = {
            k:v
            for k, v in mod_data.items()
        }

        # Load title data (backward compatible with old saves)
        title_data = loaded_data.get('TITLES_AND_MAA', {})
        title_names_data = loaded_data.get('TITLE_NAMES', {})
        loaded_title_mapping = {
            tuple(k.split(seperator)):v
            for k, v in title_data.items()
        }
        loaded_title_names = {
            k:v
            for k, v in title_names_data.items()
        }

        # Validate title keys
        title_diff = 0
        for k in loaded_title_mapping.keys():
            maa = k[0]
            if maa not in TITLE_NON_MAA_KEYS and maa not in [key['ck3_maa'] for key in MAA_SOURCE_KEYS]:
                maa_diff = 1
                missing_keys.append([maa,'CK3 ManAtArms (Title)'])
        for v in loaded_title_mapping.values():
            attila = v[0]
            if attila not in [key['attila_map_key'] for key in ATTILA_SOURCE_KEYS]:
                attila_diff = 1
                missing_keys.append([attila,'Attila Unit (Title)'])
        for tk in loaded_title_names.keys():
            if tk not in [item['title_key'] for item in TITLE_SOURCE_KEYS]:
                title_diff = 1
                missing_keys.append([tk,'CK3 Title'])

        if maa_diff == 1:
            diff_message = diff_message + '⚠️ Detected missing MAA source! (CK3/CK3 mods)\n'
        if attila_diff == 1:
            diff_message = diff_message + '⚠️ Detected missing Attila source! (Attila/Attila mods)\n'
        if heritage_diff == 1:
            diff_message = diff_message + '⚠️ Detected missing heritage source! (CK3/CK3 mods)\n'
        if culture_diff == 1:
            diff_message = diff_message + '⚠️ Detected missing culture source! (CK3/CK3 mods)\n'
        if title_diff == 1:
            diff_message = diff_message + '⚠️ Detected missing title source! (CK3/CK3 mods)\n'

        if diff_message:
            sg.popup(f'Warning: Missing sources were detected. This will cause issues with the mapper tool due to missing source keys\n\n{diff_message}\nPlease ensure you have all required sources for this mapper, both CK3 and Attila, for complete and issue free editing:\n• For CK3, ensure you have the required mods installed in Steam\n• For Attila, ensure you have exported all the correct unit key .tsv files')
            overall_diff = 1
            unique = sorted(set(tuple(x) for x in missing_keys))
            missing_keys = [list(x) for x in unique]

        return loaded_faction_mapping, loaded_heritage_mapping, loaded_mods, overall_diff, missing_keys, loaded_title_mapping, loaded_title_names

    # END FUNCTIONS
    # ==============================================

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
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
                save_mapper(MAPPER_NAME, current_mappings, current_heritage_mappings, current_mods, current_title_mappings, current_title_names)
                add_map_config(MAPPER_NAME, current_mods)

            else:
                name = popup_mapper_name_input()
                if name:
                    save_mapper(name, current_mappings, current_heritage_mappings, current_mods, current_title_mappings, current_title_names)
                    MAPPER_NAME = name
                    add_map_config(MAPPER_NAME, current_mods)
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')

        elif event == 'FILE_LOAD_KEY':
            loaded_faction_mapping, loaded_heritage_mapping, loaded_mods, diff, missing_keys, loaded_title_mapping, loaded_title_names = load_mapper(values['FILE_LOAD_KEY'])
            map_name, _ = os.path.splitext(os.path.basename(values['FILE_LOAD_KEY']))
            if loaded_faction_mapping:
                current_mappings = loaded_faction_mapping
                current_heritage_mappings = loaded_heritage_mapping
                current_mods = loaded_mods
                current_title_mappings = loaded_title_mapping
                current_title_names = loaded_title_names
                available_factions = list(set([item[0][1] for item in current_mappings.items()]))
                FACTION_LIST = sorted(available_factions)
            MAPPER_NAME = map_name
            update_mappings_list(window, current_mappings)
            window[FACTION_KEY].update(values=FACTION_LIST)
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')
            if diff:
                window['SUBTEXT'].update('⚠️ Warning: Missing sources for loaded mapper, continue at your own risk!\nRecommended to only add or modify existing maps',text_color="#E9D502")
                window['VIEW_MISSING_BUTTON'].update(visible=True)
            else:
                window['SUBTEXT'].update('Each FACTION is assigned to one or many HERITAGE.',text_color="#FFFFFF")
                window['VIEW_MISSING_BUTTON'].update(visible=False)

        elif event == 'VIEW_MISSING_BUTTON':
            popup_missing_keys(missing_keys)

        elif event == 'ADD_MAPPING_KEY' and selected_ck3 and selected_attila:
            current_faction = values[FACTION_KEY]
            if current_faction:
                size = values['MAA_SIZE_SELECT']
                if size == 'MANUAL':
                        size = popup_size_manual()
                for selected in selected_ck3:
                    mapping_key = (selected, current_faction)
                
                    # Check for conflicts (CK3 unit + Faction combination already mapped), and overwrite if so.
                    if mapping_key in current_mappings:
                        key_to_remove = (selected, current_faction)
                        del current_mappings[key_to_remove]
                    override_size = ''
                    if re.search(r'^LEVY-', mapping_key[0]):
                        override_size = 'LEVY'
                        levy_size = DEFAULT_LEVY_PERCENTAGES.get(mapping_key[0]) # Get default levy % from list, as levies can only be obtained from available units list
                    if re.search(r'^GENERAL\b', mapping_key[0]):
                        override_size = 'GENERAL'
                    if re.search(r'^KNIGHTS\b', mapping_key[0]):
                        override_size = 'KNIGHTS'

                    if override_size == 'LEVY':
                        current_mappings[mapping_key] = selected_attila + [override_size] + [levy_size]
                    elif override_size:
                        current_mappings[mapping_key] = selected_attila + [override_size]
                    else:
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
                    if mapping_key in current_mappings:
                        del current_mappings[mapping_key]
                    current_mappings[mapping_key] = copied_value
                    # Update the displayed list
                update_mappings_list(window, current_mappings)
                check_add_button(window)
        
        elif event == 'LEVY_PERCENTAGE_BUTTON_KEY':
            current_faction = values[FACTION_KEY]
            filtered_mapping = {}
            table_data = []
            if current_faction:
                filtered_mapping = {
                            key:value
                            for key, value in current_mappings.items() if re.search(r'^LEVY-', key[0]) and key[1] == current_faction
                        }
            
                for key, value in filtered_mapping.items():
                    table_data.append([key[0],value[0],value[2]])
                new_levy_data = popup_levy_percentage(current_faction, table_data)
                if new_levy_data:
                    for data in new_levy_data:
                        updated_key = (data[0],current_faction)
                        updated_value = data[2]
                        current_mappings[updated_key] = [data[1], 'LEVY', updated_value]


                    update_mappings_list(window, current_mappings)
                    

        elif event == 'FACTION_LIST_EDIT_BUTTON_KEY':
            new_faction_list = popup_faction_list(FACTION_LIST)
            if new_faction_list != None:
                FACTION_LIST = new_faction_list
                window[FACTION_KEY].update(values=FACTION_LIST)

        elif event == 'MOD_CONFIG_BUTTON':
            new_mods = popup_mods_config(current_mods)
            if new_mods:
                current_mods = new_mods
        
        elif event == 'TITLE_EDIT_BUTTON_KEY':
            current_title_mappings, current_title_names = title_window(
                current_title_mappings, current_title_names
            )

        elif event == 'HERITAGE_EDIT_BUTTON_KEY':
            current_heritage_mappings = heritage_window(current_heritage_mappings, FACTION_LIST)

        elif event == 'XML_BUTTON':
            xml_import = popup_xml_import_export(CONFIG)
            if xml_import:
                import_name = xml_import[0]
                import_maa = xml_import[1]
                import_heritage = xml_import[2]
                import_mods = xml_import[3]
                import_titles = xml_import[4] if len(xml_import) > 4 else {}
                import_title_names = xml_import[5] if len(xml_import) > 5 else {}
                save_mapper(import_name, import_maa, import_heritage, import_mods, import_titles, import_title_names)
                add_map_config(import_name, import_mods)

        elif event == 'HELP_GUIDE_BUTTON':
            popup_help_guide()

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
                try:
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
                except (FileNotFoundError, SystemExit, Exception) as e:
                    window['MLINE_KEY'].update(f'ERROR: Validation failed: {e}\n', append=True)
                window['VALIDATE_KEY'].update(disabled=False)

        elif event == 'CUSTOM_MAPPER_KEY':
                mapping_window()

    window.close()

if __name__ == '__main__':
        main_window()