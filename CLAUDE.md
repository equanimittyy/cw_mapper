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
  cli.py                # CLI interface for Claude-assisted mapper creation
  source_data.py        # Shared source data loading (used by both GUI and CLI)
  constants.py          # Shared constants: paths, directories, domain constants (NON_MAA_KEYS, etc.)
  cw_map_checker.py     # Validation logic - reads CK3/Attila data, parses CW XMLs, produces reports
  utils.py              # Utilities - config management, XML import/export, save/load mapper, list filtering
  cw_mapper.ico         # Application icon (used by PyInstaller build)
  main.spec             # PyInstaller build spec - run: pyinstaller main.spec
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

  cli_data/             # CK3 source exports for CLI use (gitignored, produced via GUI or CLI)
  reports/              # Generated CSV reports from validation runs
  summary_log.txt       # Human-readable validation summary
```

## Module Responsibilities

### constants.py
Single source of truth for all shared constants and paths. All other modules import from here instead of redefining paths.
- **Paths**: APPLICATION_PATH, WORKING_DIR, CW_DIR, ATTILA_EXPORT_DIR, REPORT_OUTPUT_DIR, CUSTOM_MAPPER_DIR, MAP_CONFIG, etc.
- **Domain constants**: NON_MAA_KEYS, DEFAULT_LEVY_PERCENTAGES, TITLE_NON_MAA_KEYS, RANK_MAP, CW_CUSTOM_VALUES

### utils.py
Business logic utilities — no GUI imports, no module-level side effects.
- **Config**: `init_map_config()`, `get_config()`, `get_full_config()`, `get_ck3_mods_from_config()`, `add_map_config()`, `resolve_import_mods()`
- **Save/Load**: `save_mapper()`, `load_mapper()` — JSON serialization/deserialization with key validation
- **XML I/O**: `import_xml()`, `export_xml()`
- **Mapping rules**: `build_mapping_entry()` — shared business logic for GENERAL/KNIGHTS/LEVY auto-sizing (used by both GUI and CLI)
- **Helpers**: `filter_source_list()`, `filter_culture_list()` — shared filter+search for list data

### source_data.py
Shared source data loading — used by both GUI (`main.py`) and CLI (`cli.py`). No GUI imports.
- **`SourceData`**: NamedTuple holding loaded source keys
- **`load_source_data()`**: Reads Attila keys from TSV exports + CK3 keys from `cli_data/` (or `reports/` fallback)
- **`export_cli_source_data()`**: Exports CK3 source data to `cli_data/` for CLI use
- **`run_validation()`**: Full validation pipeline (lazy-imports `cw_map_checker`)

### cli.py
CLI interface for Claude-assisted mapper creation. Argparse with subcommands. JSON output to stdout, status/warnings to stderr.
- **Source queries**: `source maa|attila|cultures|titles|list-sources|export`
- **Mapper lifecycle**: `mapper list|create|show|copy|delete`
- **Mapping operations**: `mapping add|remove|copy-faction|set-levy|batch`
- **Heritage operations**: `heritage add|add-parent|remove|batch`
- **Title operations**: `title add-key|remove-key|add|remove|batch`
- **Mod config**: `mod show|add-ck3|remove-ck3|add-attila|remove-attila`
- **Import/Export**: `export`, `import`

### cw_map_checker.py
Validation engine — reads game data, validates mappers, writes reports.
- **Parsing helpers**: `_parse_culture_files()`, `_parse_maa_files()`, `_parse_title_files()` — deduplicated file parsing
- **Data loading**: `get_keys()` returns a `GameKeys` NamedTuple (cultures, maa, attila, titles)
- **Validation**: `mapping_validation()` returns in-memory results (no file I/O)
- **Report writing**: `write_reports()` writes CSVs from validation results (separated from validation)
- **Summary**: `summary()` reads reports and writes summary_log.txt

### main.py
GUI layer — FreeSimpleGUI windows and event loops. Delegates all business logic to utils/source_data/cw_map_checker.
- Imports `SourceData`, `load_source_data()`, `run_validation()`, `export_cli_source_data()` from `source_data.py`
- **Window functions**: `main_window()`, `mapping_window(src)`, `heritage_window(..., src)`, `title_window(..., src)` — all receive SourceData explicitly
- **"Export Source Data for CLI"** button in main window — calls `export_cli_source_data()` to write CK3 data to `cli_data/`

## Key Data Flows

### Validation Flow

```
CK3 Install Dir (cultures, MAA) ──┐
CK3 Mod Dir (Steam Workshop)  ────┤
                                   ├──> cw_map_checker.get_keys() ──> GameKeys NamedTuple
Attila .tsv exports ───────────────┘           │
                                               v
CW Mapper XMLs (../../unit mappers/attila/) ──> mapping_validation(game_keys)
                                                       │
                                                       v
                                              (mapper_results, game_keys)  [in-memory]
                                                       │
                                                       ├──> write_reports()  ──> CSV Reports
                                                       v
                                                 summary() ──> summary_log.txt
```

### Custom Mapper Flow

```
User selects CK3 MAA + Attila Unit Key + Faction ──> current_mappings dict
User maps Heritages/Cultures to Factions ──────────> current_heritage_mappings dict
User maps Titles (Empire/Kingdom/Duchy) to MAA ───> current_title_mappings dict + current_title_names dict
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
    "ck3_maa_key,faction_name": ["attila_unit_key", "size_or_type", optional_levy_percentage]
  },
  "HERITAGES_AND_CULTURES": {
    "heritage_name,culture_or_PARENT_KEY": ["assigned_faction"]
  },
  "TITLES_AND_MAA": {
    "ck3_maa_key,title_key": ["attila_unit_key", "size_or_type"]
  },
  "TITLE_NAMES": {
    "title_key": "display_name"
  },
  "MODS": {
    "CK3": ["ModName:SteamWorkshopID", ...],
    "Attila": ["mod_pack_file.pack", ...]
  }
}
```

NOTE: Title mappings do NOT support levies. Only GENERAL, KNIGHTS, and MenAtArm types are valid for title mappings.

### CW XML Format (What Crusader Wars Reads)

NOTE: If 'Levies', the 'porcentage' (mispelling of percentage) of all Levies must add up to 100% for a given Faction

- **Factions XML**: `<FactionsGroups>` > `<Faction name="...">` > `<MenAtArm type="ck3_maa" key="attila_key" max="size"/>` + `<General>`, `<Knights>`, `<Levies>`
- **Cultures XML**: `<Cultures>` > `<Heritage name="..." faction="...">` > `<Culture name="..." faction="..."/>`
- **Titles XML**: `<Titles>` > `<Faction title_key="e_byzantium" name="Byzantine Empire">` > `<General>`, `<Knights>`, `<MenAtArm>` (no Levies). Grouped by rank: `Empires.xml`, `Kingdoms.xml`, `Duchies.xml`
- **Mods XML**: `<Mods>` > `<Mod>packfile.pack</Mod>`
- **Time Period XML**: `<TimePeriod>` > `<StartDate>` + `<EndDate>`

## Special Unit Types

- **GENERAL**: Commander unit, one per faction
- **KNIGHTS**: Knight unit, one per faction
- **LEVY\***: Levy units with percentage allocations (must sum to 100% per faction)
- **MenAtArm**: Regular MAA with size types: INFANTRY, CAVALRY, RANGED, or a manual number

## Default Faction Requirement

**Every MAA added to any faction MUST also have a corresponding mapping in the `Default` faction.** The Default faction acts as a crash-prevention fallback: if a culture doesn't have a specific MAA in its assigned faction (e.g. a Norse culture triggers a Chinese MAA that doesn't exist in the Viking faction), CW falls back to the Default faction's mapping for that MAA. Without a Default entry, this causes a crash.

**Rule:** When adding a new MAA mapping to a faction, always ensure the same MAA key also exists in the Default faction.

## MAA Faction Assignment Rules

When determining which faction a CK3 MAA belongs to, **always research the actual CK3/mod source** to find which culture, heritage, or tradition unlocks that MAA in-game. Do NOT guess from the unit name or historical inference alone — names can be misleading (e.g. `black_armor_cavalry` sounds Abbasid but is actually a Chinese MAA in CK3). If uncertain, ask the user for confirmation rather than guessing — they can check the game directly.

East Asian MAA (Chinese, Japanese, SEA, etc.) should be assigned to **Tibetan** or **Eastern Steppe** factions as a fallback, since Total War: Attila has no unit packs for those regions.

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

## CLI (cli.py) — Claude-Assisted Mapper Creation

See **[CLI_GUIDE.md](docs/CLI_GUIDE.md)** for the full CLI documentation including setup, collaborative workflow, command reference, and batch JSON formats.

**Limitation:** The CLI `validate` command runs the validation pipeline but only returns a status message — it does not surface the summary/missing-key data as JSON. To see what's missing per mapper, read `summary_log.txt` or the CSVs in `reports/` after the user runs validation through the GUI. Source data export also requires the user's CK3/Attila install, so it must be done manually on their machine.

## Post-Code Agent Suite

After completing code changes, **prompt the user** to run the post-code review agents. These live in `.claude/agents/` and should be offered as a follow-up step after any non-trivial implementation or refactor.

**Agents (run any combination relevant to the change):**

- **`coupling-reviewer`** — Analyzes coupling, dependency direction, and separation of concerns. Use after adding new modules, refactoring existing code, or introducing new interactions between files/functions.
- **`dead-code-finder`** — Identifies unused imports, unreferenced functions, redundant logic, and stale code. Use after refactoring or removing features to keep the codebase lean.
- **`edge-case-finder`** — Finds unguarded boundary conditions, empty-state bugs, string-parsing fragility, and GUI state inconsistencies. Use after adding new user-facing features or modifying event handlers.
- **`robustness-reviewer`** — Reviews file I/O safety, data integrity, input validation, error recovery, and XML generation correctness. Use after modifying save/load, import/export, or any code that touches the filesystem.

**How to prompt:**
After finishing a code change, say something like:
> "Would you like me to run the post-code review agents? Based on this change, I'd recommend: [agent names]"

Only suggest agents relevant to the change — don't offer all four for a one-line fix. For large changes touching multiple concerns, offer to run multiple agents in parallel.
