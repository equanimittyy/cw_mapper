import os
import FreeSimpleGUI as sg

import cw_mapper
import cw_map_checker

ASCII_ART = os.path.join('ascii-art-text.png')
SUMMARY_LOG = os.path.join("summary_log.txt")

if os.path.exists(SUMMARY_LOG):
    with open(SUMMARY_LOG, 'r', encoding="utf-8-sig") as f:
        TEXT = f.read()
else:
    TEXT = ""

def main_window():
    layout = [
        [sg.Image(ASCII_ART)],
        [[sg.Button('Validate and Refresh',key="VALIDATE_KEY")],
        [sg.Multiline(
            TEXT,
            enable_events=False,
            size=(80, 25),              # Set a large initial size
            font=('Courier New', 10),   # 1. Monospace Font
            horizontal_scroll=True,     # 2. Enables Horizontal Scrolling
            expand_x=True,              # Allows it to stretch horizontally on resize
            expand_y=True,            # Allows it to stretch vertically on resize
            disabled=True,
            key="MLINE_KEY")]
        ]
    ]

    window = sg.Window('Crusader Wars Mapper', layout, resizable=True).Finalize()
    window.Maximize()

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        elif event == 'VALIDATE_KEY':
            window["MLINE_KEY"].update('')
            window["MLINE_KEY"].update(disabled=False)

            window["VALIDATE_KEY"].update(disabled=True)

            # Init config in the event it is missing
            # cw_mapper.init_map_config()
            # # Validate and update keys, producing reports
            # cw_map_checker.mapping_validation(*cw_map_checker.get_keys(cw_map_checker.get_cw_config()))
            # cw_map_checker.summary()

    window.close()

if __name__ == '__main__':
    main_window()