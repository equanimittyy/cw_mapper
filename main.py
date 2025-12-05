import os
import sys
import csv
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

with open (os.path.join(REPORT_OUTPUT_DIR,'source_attila_keys.csv'), 'r') as f:
    key_data = csv.DictReader(f)
    for key in key_data:
        ATTILA_SOURCE_KEYS.append({'attila_map_key':key['attila_map_key'],'attila_source':key['attila_source']})

with open(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_cultures_keys.csv'), 'r') as f:
    key_data = csv.DictReader(f)
    for key in key_data:
        CULTURES_SOURCE_KEYS.append({'ck3_culture':key['ck3_culture'],'ck3_source':key['ck3_source']})

with open(os.path.join(REPORT_OUTPUT_DIR,'source_ck3_maa_keys.csv'), 'r') as f:
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

def heritage_window():
    pass

def mapping_window():
    MAPPER_NAME = ''
    ATTILA_UNIT_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(ATTILA_SOURCES)))
    MAA_LIST_SOURCE = ['ALL'] + sorted(list(dict.fromkeys(CK3_SOURCES)))

    FACTION_LIST = ['DEFAULT'] + [
    ]

    # Dictionary to store the actual mappings (CK3 MAA: ATTILA UNIT KEY, per FACTION)
    # Format: { (ck3_maa, faction): attila_unit ] }
    current_mappings = {}
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
        [sg.Text('Search...',background_color='#DDDDDD',text_color="#000000"),sg.Input(key='ATTILA_SEARCH_KEY', enable_events=True)]
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
        ),sg.Push(background_color='#DDDDDD'),sg.Button('Save', key='SAVE_BUTTON_KEY',size=(15, 2), button_color=('white', '#444444')),sg.Input(key='FILE_LOAD_KEY',visible=False,enable_events=True),sg.FileBrowse('Load', target='FILE_LOAD_KEY',size=(15, 2), initial_folder=CUSTOM_MAPPER_DIR, button_color=('white', '#444444'),file_types=((('Text Files', '*.txt'),))),sg.Button('Import/Export XML', size=(15, 2), button_color=('white', "#008670"))],
        [sg.Listbox(
            values=[],
            size=(35, 13), # Adjusted size to fit the Combo element
            key='MAPPING_LISTS_KEY',
            select_mode=sg.LISTBOX_SELECT_MODE_EXTENDED,
            background_color='#E8E8FF',
            expand_x=True,
            expand_y=True
        )],
        [sg.Button('Add Mapping', key='ADD_MAPPING_KEY', size=(15, 2), button_color=('white', '#004D40'), disabled=True),sg.Button('Remove Selected', key='REMOVE_MAPPING_KEY', size=(15, 2), button_color=('white', '#CC0000'), disabled=True),sg.Push(background_color='#DDDDDD'),sg.Button('Open Faction-Heritage mapping', size=(25, 2), button_color=('white', '#444444'))],
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
        display_list = []
        formatted_list = []
        # Key is a tuple (ck3_maa, faction), value is attila_unit
        for (ck3, faction), attila in mappings_dict.items():
            display_list = [t for t in mappings_dict.items() if t[0][1] == current_faction]
        if display_list:
            for (ck3, faction), attila in display_list:
                formatted_list.append(f"[{faction}] {ck3} => {attila}")
        else:
            formatted_list = []
        
        window['MAPPING_LISTS_KEY'].update(sorted(formatted_list))
        # Re-enable/disable the Remove button based on whether there are mappings
        window['REMOVE_MAPPING_KEY'].update(disabled=len(formatted_list) == 0)

    # Function to check if the 'Add Mapping' button should be active
    def check_add_button(window):
        """Enables the Add button only if both CK3 and Attila units are selected."""
        is_ready = selected_ck3 is not None and selected_attila is not None and values[FACTION_KEY] != ''
        window['ADD_MAPPING_KEY'].update(disabled=not is_ready)

    def save_mapper(name, custom_mapping):
        output_path = os.path.join(CUSTOM_MAPPER_DIR,f'{name}.txt')
        os.makedirs(CUSTOM_MAPPER_DIR, exist_ok=True)
        seperator = ','
        save_format = {
            seperator.join(k):v
            for k,v in custom_mapping.items()
        }
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(save_format,f,indent=4)

    def load_mapper(file):
        seperator = ','
        with open(file, 'r', encoding='utf-8-sig') as f:
            loaded_data = json.load(f)
        loaded_mapping = {
            tuple(k.split(seperator)):v
            for k, v in loaded_data.items()
        }
        return loaded_mapping
    
    def export_xml():
        pass

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
                save_mapper(MAPPER_NAME, current_mappings)
            else:
                name = popup_mapper_name_input()
                if name:
                    save_mapper(name,current_mappings)
                    MAPPER_NAME = name
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')

        elif event == 'FILE_LOAD_KEY':
            loaded_mapper = load_mapper(values['FILE_LOAD_KEY'])
            map_name, _ = os.path.splitext(os.path.basename(values['FILE_LOAD_KEY']))
            if loaded_mapper:
                current_mappings = loaded_mapper
                available_factions = list(set([item[0][1] for item in current_mappings.items()]))
                FACTION_LIST = sorted(available_factions)
            MAPPER_NAME = map_name
            update_mappings_list(window, current_mappings)
            window[FACTION_KEY].update(values=FACTION_LIST)
            window['MAPPER_COL_TITLE_KEY'].update(f'Unit Key Mapper: {MAPPER_NAME}')

        elif event == 'ADD_MAPPING_KEY' and selected_ck3 and selected_attila:
            current_faction = values[FACTION_KEY]
            if current_faction:
                for selected in selected_ck3:
                    mapping_key = (selected, current_faction)
                
                    # Check for conflicts (CK3 unit + Faction combination already mapped), and overwrite if so.
                    for key in mapping_key:
                        if key in current_mappings:
                            key_to_remove = (selected, current_faction)
                            del current_mappings[key_to_remove]
                    
                    current_mappings[mapping_key] = selected_attila

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
                utils.init_map_config()
                cw_map_checker.mapping_validation(*cw_map_checker.get_keys(cw_map_checker.get_cw_config()))
                cw_map_checker.summary()

                window['MLINE_KEY'].update(f'Crusader Wars mappers refreshed! \n', append=True)
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