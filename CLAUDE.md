# Crusader Wars Mapper (cw-mapping-validator)

## Overview

A Python desktop tool built to support **FarayC's Crusader Wars** mod for Crusader Kings 3.
Crusader Wars bridges CK3 and Total War: Attila, allowing battles to be fought in Attila's engine.
This tool handles the **unit mapping** between the two games - ensuring CK3 Man-at-Arms types and cultures are correctly mapped to Attila unit keys.

**Author:** equanimittyy

## What the Program Does

### 1. Mapping Validation (cw_map_checker.py)

Validates the existing XML mapper files used by Crusader Wars by:

- Reading **Attila unit keys** from `.tsv` files exported via RPFM/PFM (stored in `attila_exports/db/main_units_tables/`)
- Reading **CK3 cultures** from the CK3 installation directory (vanilla + Steam Workshop mods)
- Reading **CK3 Man-at-Arms types** from the CK3 installation directory (vanilla + Steam Workshop mods)
- Parsing the **CW mapper XML files** (located in `../../unit mappers/attila/` relative to the tool - i.e. typically `crusader-wars/unit mappers/attila/[mapper-folder]/`) where [mapper-folder] is the folder name of a mapper such as 'OfficialCW_EarlyMedieval_919Mod'
- Cross-referencing all keys and producing CSV reports in `reports/`
- Generating a `summary_log.txt` showing missing keys per mapper

### 2. Custom Mapper Creator (main.py - GUI)

A FreeSimpleGUI desktop application that lets users create their own custom unit mappers:

- **Three-column layout**: CK3 MAA list | Attila Unit Key list | Mapping editor (per faction)
- Users map CK3 Man-at-Arms => Attila Unit Keys, organized by **Factions**
- Users map CK3 Heritages/Cultures => Factions (determines which faction's units a culture uses)
- Supports special unit types: General, Knights, Levies (with percentage allocation), and sized MAA units
- Save/Load mappers as `.txt` (JSON format) in `custom_mappers/`
- Import/Export to Crusader Wars XML format (the format CW actually reads)

## Project Structure

```
/workspace
  main.py               # GUI application (FreeSimpleGUI) - main window + custom mapper window
  cw_map_checker.py     # Validation logic - reads CK3/Attila data, parses CW XMLs, produces reports
  utils.py              # Utilities - config management, XML import/export
  pyproject.toml        # Project config (Python >=3.13, deps: configparser, freesimplegui, pandas)

  config/
    default.json        # Default mod configuration (shipped with tool) - defines what CK3 mods are supported by a mapper
    mod_config.json     # Active mod configuration (maps mapper names to CK3 mods with Steam Workshop IDs) - defines what CK3 mods are supported by a mapper

  attila_exports/
    db/main_units_tables/
      *.tsv             # Attila unit key exports (from RPFM). Each row = unit key. Must be manually exported using RPFM (shipped with tool).

  custom_mappers/
    *.txt               # Saved custom mappers (JSON format with FACTIONS_AND_MAA, HERITAGES_AND_CULTURES, MODS sections)
    example_mapper/     # Example of exported XML mapper format (what CW reads)
      OfficialCW_EarlyMedieval_919Mod/
        Factions/       # XML files: <FactionsGroups> > <Faction> > <MenAtArm|General|Knights|Levies>
        Cultures/       # XML files: <Cultures> > <Heritage> > <Culture> (with faction assignments)
        Titles/         # XML files: title-based mappings (Empires, Kingdoms)
        Mods.xml        # Mod load order list of required Attila .pack mods, loaded from top to bottom
        Time Period.xml # Start/end date for this mapper set
        tag.txt         # Identifier tag for multi-mapper sets
        background.png  # UI background image

  reports/              # Generated CSV reports from validation runs
  summary_log.txt       # Human-readable validation summary
```

## Key Data Flows

### Validation Flow

```
CK3 Install Dir (cultures, MAA) ──┐
CK3 Mod Dir (Steam Workshop)  ────┤
                                   ├──> cw_map_checker.get_keys() ──> DataFrames
Attila .tsv exports ───────────────┘           │
                                               v
CW Mapper XMLs (../../unit mappers/attila/) ──> mapping_validation() ──> CSV Reports
                                                       │
                                                       v
                                                 summary() ──> summary_log.txt
```

### Custom Mapper Flow

```
User selects CK3 MAA + Attila Unit Key + Faction ──> current_mappings dict
User maps Heritages/Cultures to Factions ──────────> current_heritage_mappings dict
User maps Title (Empire/Kingdom/Dutchy etc.) based mapping (NOT YET IMPLEMENTED)
User configures mod list ──────────────────────────> current_mods dict
     │
     ├──> Save as .txt (JSON) in custom_mappers/
     └──> Export as XML (CW-ready format) in custom_mappers/export/
```

### Mapper Save Format (.txt / JSON)

NOTE: "optional_levy_percentage" must be included if the type is 'LEVY' it must also add up to 100% for all LEVY maps in a given faction

```json
{
  "FACTIONS_AND_MAA": {
    "ck3_maa_key,faction_name": ["attila_unit_key", "size_or_type", optional_levy_percentage
  },
  "HERITAGES_AND_CULTURES": {
    "heritage_name,culture_or_PARENT_KEY": ["assigned_faction"]
  },
  "MODS": {
    "CK3": ["ModName:SteamWorkshopID", ...],
    "Attila": ["mod_pack_file.pack", ...]
  }
}
```

### CW XML Format (What Crusader Wars Reads)

NOTE: If 'Levies', the 'porcentage' (mispelling of percentage) of all Levies must add up to 100% for a given Faction

- **Factions XML**: `<FactionsGroups>` > `<Faction name="...">` > `<MenAtArm type="ck3_maa" key="attila_key" max="size"/>` + `<General>`, `<Knights>`, `<Levies>`
- **Cultures XML**: `<Cultures>` > `<Heritage name="..." faction="...">` > `<Culture name="..." faction="..."/>`
- **Mods XML**: `<Mods>` > `<Mod>packfile.pack</Mod>`
- **Time Period XML**: `<TimePeriod>` > `<StartDate>` + `<EndDate>`

## Special Unit Types

- **GENERAL**: Commander unit, one per faction
- **KNIGHTS**: Knight unit, one per faction
- **LEVY\***: Levy units with percentage allocations (must sum to 100% per faction)
- **MenAtArm**: Regular MAA with size types: INFANTRY, CAVALRY, RANGED, or a manual number

## Configuration

- `mod_config.json`: Maps mapper names to lists of `[mod_name, steam_workshop_id]` pairs
- Steam Workshop ID `0` = CK3 Vanilla
- The tool expects to live at `CW/tools/cw_mapper/` relative to the Crusader Wars installation
- CK3 install path is read from `../../data/settings/GamePaths.ini`

## Dependencies

- Python >=3.13
- FreeSimpleGUI (PySimpleGUI fork)
- pandas
- configparser

## Build

- Built as executable via PyInstaller (`main.spec`)
- Distributed as `cw_mapper.zip`

## Reporting

- Any code changes and implementations are to be summarised in a human-readable format in workspace/.claude/code_reports in .txt format.
