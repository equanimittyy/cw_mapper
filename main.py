import os
import sys
import webbrowser
import FreeSimpleGUI as sg

import cw_mapper
import cw_map_checker

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)

# Identify working directories
WORKING_DIR = application_path

ASCII_ART = os.path.join('ascii-art-text.png')
SUMMARY_LOG = os.path.join("summary_log.txt")
ATTILA_EXPORT_DIR = os.path.join(WORKING_DIR, 'attila_exports','db','main_units_tables')

MOD_LIST = []

# Initialise the text in the summary log, if it exists
if os.path.exists(SUMMARY_LOG):
    with open(SUMMARY_LOG, 'r', encoding="utf-8-sig") as f:
        TEXT = f.read()
else:
    TEXT = "No summary_log.txt was found. Refresh your mappers using 'Refresh Current Mappers'"

def mapping_window():
    # Load available keys
    CK3_MAA_LIST = [
        'maa_heavy_infantry',
        'maa_light_cavalry_scout',
        'maa_archer_longbow',
        'maa_pikemen_landsknechte',
        'maa_onagers_siege',
        'maa_war_elephants',
        'maa_horse_archers'
    ]

    ATTILA_UNIT_LIST = [
        'att_foot_warriors',
        'att_shock_cavalry',
        'att_skirmishers_bow',
        'att_spearmen_elite',
        'att_artillery_catapult',
        'att_camel_riders',
        'att_mounted_archers'
    ]

    CULTURE_LIST = [
        'culture_roman',
        'culture_germanic',
        'culture_saxon',
        'culture_hunnish',
        'culture_sarmatian',
        'culture_byzantine'
    ]

    # Dictionary to store the actual mappings (CK3 MAA: ATTILA UNIT KEY, per CULTURE)
    # Format: { (ck3_maa, culture): attila_unit ] }
    current_mappings = {}
    CULTURE_KEY = 'CULTURE_SELECT_KEY'


    # Column Definitions and layout
    # Column 1: CK3 MAA Selector
    col1_layout = [
        [sg.Text('Available CK3 MAA', font=('Courier New', 12, 'bold'), text_color='#6D0000',relief=sg.RELIEF_RIDGE)],
        [sg.Listbox(
            values=sorted(CK3_MAA_LIST),
            size=(30, 15),
            key='CK3_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected CK3:', size=(25, 1), key='SELECTED_CK3_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN)]
    ]

    # Column 2: ATTILA UNIT KEY Selector
    col2_layout = [
        [sg.Text('Available ATTILA UNIT KEY', font=('Courier New', 12, 'bold'), text_color='#006D00',relief=sg.RELIEF_RIDGE)],
        [sg.Listbox(
            values=sorted(ATTILA_UNIT_LIST),
            size=(30, 15),
            key='ATTILA_LIST_KEY',
            enable_events=True,
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            expand_x=True,
            expand_y=True
        )],
        [sg.Text('Selected ATTILA:', size=(25, 1), key='SELECTED_ATTILA_KEY', background_color='#F0F0F0', relief=sg.RELIEF_SUNKEN)]
    ]

    # Column 3: Mappings Display and Action Button (with new Culture selector)
    col3_layout = [
        [sg.Text('Contextual Mapping Culture: (CK3 <> TWA)', font=('Courier New', 12, 'bold'), text_color='#00006D',relief=sg.RELIEF_RIDGE)],
        # New Culture Selector Dropdown
        [sg.Text('Select Culture:'), sg.Combo(
            values=CULTURE_LIST, 
            default_value=CULTURE_LIST[0], 
            size=(20, 1), 
            key=CULTURE_KEY, 
            readonly=True,
            enable_events=True
        )],
        [sg.Listbox(
            values=[],
            size=(35, 13), # Adjusted size to fit the Combo element
            key='MAPPING_LISTS_KEY',
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            background_color='#E8E8FF',
            expand_x=True,
            expand_y=True
        )],
        [sg.Button('Add Mapping', key='ADD_MAPPING_KEY', size=(15, 2), button_color=('white', '#004D40'), disabled=True)],
        [sg.Button('Remove Selected', key='REMOVE_MAPPING_KEY', size=(15, 2), button_color=('white', '#CC0000'))]
    ]

    # Main layout
    mapper_layout = [
        [sg.Text('Unit Mapper Configuration', font=('Courier New', 26, 'bold'), justification='center', expand_x=True, pad=(0, 15))],
        [
            sg.Column(col1_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col2_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True),
            sg.VSeparator(),
            sg.Column(col3_layout, element_justification='center', vertical_alignment='top', pad=(10, 10), background_color='#DDDDDD',expand_x=True,expand_y=True)
        ],
        [sg.Button('Save', size=(15, 2), button_color=('white', '#444444')),sg.Button('Exit', size=(15, 2), button_color=('white', '#444444'))]
    ]

    window = sg.Window('Custom Unit Mapper', mapper_layout, finalize=True, element_justification='center',resizable=True)

    # Variables to hold the currently selected items
    selected_ck3 = None
    selected_attila = None

    # Mapping handler function
    # Function to update the Mappings Listbox values based on the state dictionary
    def update_mappings_list(window, mappings_dict):
        """Formats the mapping dictionary into a list of strings for the Listbox."""
        formatted_list = []
        # Key is a tuple (ck3_maa, culture), value is attila_unit
        for (ck3, culture), attila in mappings_dict.items():
            display_list = [t for t in mappings_dict.items() if t[0][1] == current_culture]
            formatted_list.append(f"{[item[0][1] for item in display_list]} {[item[0][0] for item in display_list]}  =>  {[item[1] for item in display_list]}")
        
       

        window['MAPPING_LISTS_KEY'].update(sorted(formatted_list))
        # Re-enable/disable the Remove button based on whether there are mappings
        window['REMOVE_MAPPING_KEY'].update(disabled=len(formatted_list) == 0)

    # Function to check if the 'Add Mapping' button should be active
    def check_add_button(window):
        """Enables the Add button only if both CK3 and Attila units are selected."""
        is_ready = selected_ck3 is not None and selected_attila is not None
        window['ADD_MAPPING_KEY'].update(disabled=not is_ready)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        
        elif event == 'CK3_LIST_KEY':
            if values['CK3_LIST_KEY']:
                selected_ck3 = values['CK3_LIST_KEY'][0]
                window['SELECTED_CK3_KEY'].update(f'Selected CK3: {selected_ck3}', background_color='#F5962A')
            else:
                selected_ck3 = None
                window['SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
            check_add_button(window)

        elif event == 'ATTILA_LIST_KEY':
            if values['ATTILA_LIST_KEY']:
                selected_attila = values['ATTILA_LIST_KEY'][0]
                window['SELECTED_ATTILA_KEY'].update(f'Selected ATTILA: {selected_attila}', background_color="#F5962A")
            else:
                selected_attila = None
                window['SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')
            check_add_button(window)
            
        # elif event == CULTURE_KEY:
        #     pass
        
        elif event == 'ADD_MAPPING_KEY' and selected_ck3 and selected_attila:
            current_culture = values[CULTURE_KEY]
            mapping_key = (selected_ck3, current_culture)
            
            # Check for conflicts (CK3 unit + Culture combination already mapped)
            if mapping_key in current_mappings:
                sg.popup_ok(f"Error: Mapping for '{selected_ck3}' under culture '{current_culture}' already exists.", title="Mapping Conflict")
            else:
                # Add the new mapping
                current_mappings[mapping_key] = selected_attila
                
                # Reset unit selections for the next mapping
                selected_ck3 = None
                selected_attila = None
                window['CK3_LIST_KEY'].update(set_to_index=[])
                window['ATTILA_LIST_KEY'].update(set_to_index=[])
                window['SELECTED_CK3_KEY'].update('Selected CK3:', background_color='#F0F0F0')
                window['SELECTED_ATTILA_KEY'].update('Selected ATTILA:', background_color='#F0F0F0')

                # Update the displayed list
                update_mappings_list(window, current_mappings)
                check_add_button(window)

        elif event == 'REMOVE_MAPPING_KEY':
            if values['MAPPING_LISTS_KEY']:
                # The listbox value is a formatted string. We need to parse it back to find the key tuple.
                formatted_mapping = values['MAPPING_LISTS_KEY'][0]
                
                # 1. Determine if the mapping has a culture prefix
                if formatted_mapping.startswith('['):
                    # Format: [culture] ck3_unit => attila_unit
                    parts = formatted_mapping.split('] ')
                    culture_key = parts[0].strip('[')
                    ck3_key_to_remove = parts[1].split('  =>')[0].strip()
                else:
                    # Format: ck3_unit => attila_unit (implies 'any_culture')
                    culture_key = CULTURE_LIST[0]
                    ck3_key_to_remove = formatted_mapping.split('  =>')[0].strip()

                key_to_remove = (ck3_key_to_remove, culture_key)

                if key_to_remove in current_mappings:
                    del current_mappings[key_to_remove]
                    update_mappings_list(window, current_mappings)
                
                # Clear selection in case the user immediately clicks remove again
                window['MAPPING_LISTS_KEY'].update(set_to_index=[])
    window.close()

def main_window():
    layout = [
    [sg.Image(ASCII_ART)],
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
                cw_mapper.init_map_config()
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

    window.close()

if __name__ == '__main__':
    main_window()
    # mapping_window()