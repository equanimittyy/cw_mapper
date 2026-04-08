'''Copyright (c) 2025 equanimittyy. All Rights Reserved.'''

import os
import sys

# Determine application root
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
elif __file__:
    APPLICATION_PATH = os.path.dirname(__file__)

# Identify working directories
WORKING_DIR = APPLICATION_PATH
CW_DIR = os.path.dirname(os.path.dirname(APPLICATION_PATH))  # Expected: CW/tools/cw_mapper

# Asset paths
ASCII_ART_MAIN = os.path.join('ascii-art-main.png')
ASCII_ART_MAPPER = os.path.join('ascii-art-mapper.png')
SUMMARY_LOG = os.path.join('summary_log.txt')

# Directory paths
ATTILA_EXPORT_DIR = os.path.join(WORKING_DIR, 'attila_exports', 'db', 'main_units_tables')
REPORT_OUTPUT_DIR = 'reports'
CUSTOM_MAPPER_DIR = 'custom_mappers'
CONFIG_DIR = os.path.join('config')
MAP_CONFIG = os.path.join(CONFIG_DIR, 'mod_config.json')
DEFAULT_CONFIG_PATH = os.path.join('config', 'default.json')

# CW mapper paths (absolute, built from CW_DIR)
MAPPER_DIR = os.path.join(CW_DIR, 'unit mappers', 'attila')
SETTINGS_DIR = os.path.join(CW_DIR, 'data', 'settings')

# Source report paths (used by validation)
ATTILA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR, 'source_attila_keys.csv')
CULTURES_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_cultures_keys.csv')
MAA_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_maa_keys.csv')
TITLE_SOURCE_PATH = os.path.join(REPORT_OUTPUT_DIR, 'source_ck3_title_keys.csv')

# CLI data paths (CK3 source exports for CLI use — Attila keys read directly from TSVs)
CLI_DATA_DIR = 'cli_data'
CLI_CULTURES_PATH = os.path.join(CLI_DATA_DIR, 'ck3_cultures.csv')
CLI_MAA_PATH = os.path.join(CLI_DATA_DIR, 'ck3_maa.csv')
CLI_TITLE_PATH = os.path.join(CLI_DATA_DIR, 'ck3_titles.csv')

# Domain constants
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
    'LEVY-SPEAR': 50,
    'LEVY-SWORD': 25,
    'LEVY-ARCHER': 25,
    'LEVY-SKIRM': 0,
    'LEVY-CAV': 0,
    'LEVY-CUSTOM1': 0,
    'LEVY-CUSTOM2': 0,
    'LEVY-CUSTOM3': 0
}

TITLE_NON_MAA_KEYS = ['GENERAL', 'KNIGHTS']

# Title rank map
RANK_MAP = {'e': 'Empire', 'k': 'Kingdom', 'd': 'Duchy', 'c': 'County'}

# CW custom values excluded from missing key validation
CW_CUSTOM_VALUES = {'DEFAULT', 'Default'}
