import os
import json

from typing import List, Tuple

CONFIG_DIR = os.path.join('config')
MAP_CONFIG = os.path.join(CONFIG_DIR,'mapper_config.json')

DEFAULT_CONFIG = {
    "CW_VANILLA": [
        ['CK3 Vanilla', 0],
        ['Africa Plus', 3401420817],
        ['Buffed Mongol Invasion', 2796578078],
        ['Cultures Expanded', 2829397295],
        ['More Traditions v2', 2893793966],
        ['Muslim Enhancements', 2241658518],
        ['RICE', 2273832430],
    ],
    "OfficialCW_FallenEagle_Fireforged-Empire": [
        ['The Fallen Eagle', 2243307127]
    ],
    "OfficialCW_FallenEagle_AgeOfJustinian": [
        ['The Fallen Eagle', 2243307127]
    ],
    "7K_AGOT_ARR": [
        ['A Game of Thrones', 2962333032]
    ],
    "7K_AGOT_BRR": [
        ['A Game of Thrones', 2962333032]
    ],
    "OfficialCW_RealmsInExile_TheDawnlessDays": [
        ['Realms In Exile', 2291024373]
    ],
}

def init_map_config():
    # Initialise the default config, if none present
    os.makedirs(CONFIG_DIR,exist_ok=True)
    if not os.path.exists(MAP_CONFIG):
        try:
            with open(MAP_CONFIG, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception as e:
            print('Error: {e}')
            exit(1) # Exit with an error

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