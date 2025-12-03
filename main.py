import os
import webbrowser
import FreeSimpleGUI as sg

import cw_mapper
import cw_map_checker

ASCII_ART = os.path.join('ascii-art-text.png')
SUMMARY_LOG = os.path.join("summary_log.txt")

MOD_LIST = []

if os.path.exists(SUMMARY_LOG):
    with open(SUMMARY_LOG, 'r', encoding="utf-8-sig") as f:
        TEXT = f.read()
else:
    TEXT = ""

def main_window():
    layout = [
    [sg.Image(ASCII_ART)],
    [sg.Text(text='A mapping tool for Crusader Wars.',font=('Courier New', 10))],
    [sg.Text(text='Instructions: Use the "Refresh Current Mappers" button to refresh the summary.',font=('Courier New', 10))],
    
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

            window['MLINE_KEY'].update(f'Validating mappers with additional mods: {MOD_LIST}')

            # Re-enable validation button and refresh the window
            window['MLINE_KEY'].update(TEXT)
            window['VALIDATE_KEY'].update(disabled=False)

    window.close()

if __name__ == '__main__':
    main_window()