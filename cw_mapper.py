import os
import json

CONFIG_DIR = os.path.join('config')
MAP_CONFIG = os.path.join(CONFIG_DIR,'mapper_config.json')

DEFAULT_CONFIG = {
    "CW_VANILLA": [
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

def map_config():
    # Initialise the default config, if none present
    os.makedirs(CONFIG_DIR,exist_ok=True)
    if not os.path.exists(MAP_CONFIG):
        try:
            with open(MAP_CONFIG, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=4)
        except Exception as e:
            print('Error: {e}')
            exit(1) # Exit with an error
    print(MAP_CONFIG)
    pass