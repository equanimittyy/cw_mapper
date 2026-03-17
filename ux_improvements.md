# UX Improvements Backlog

Remaining UX improvements for the Crusader Wars Mapper GUI, organized by priority.

**Previously implemented** (high-priority): unsaved changes warning, save feedback, XML import
auto-load, levy validation, wrong popup title.

**Fixed by decoupling refactor**:
- ~~Duplicated search/filter logic~~ — `filter_source_list()` in `utils.py:565` now handles all 4 call sites
- ~~Duplicate popup on XML import validation~~ — `load_mapper()` moved to `utils.py` as pure business logic; no longer shows popups

---

## Robustness / Edge Case Fixes

### Narrow save exception handler
The `except Exception` on the save button (`main.py:1357`) catches all exceptions including
programming bugs (TypeError, AttributeError). Should be narrowed to `(OSError, json.JSONDecodeError)`
so actual code bugs surface as tracebacks during development instead of generic "save error" popups.

### Shallow copy for change detection is fragile
`dict(current_title_mappings)` (`main.py:1507`) creates a shallow copy — the list values are shared
with the original. Currently safe because `title_window` replaces values with new lists rather
than mutating in-place, but any future in-place mutation would silently defeat the comparison.
Using `copy.deepcopy()` for the "before" snapshot would be more robust. Same pattern applies
to heritage mappings (`main.py:1516`), though that one is safe since values are strings.

### Partial load sets `has_unsaved_changes = False` incorrectly
When `FILE_LOAD_KEY` fires and `loaded_faction_mapping` is empty/falsy, `MAPPER_NAME` and
`has_unsaved_changes` (`main.py:1386-1387`) still update even though the actual data wasn't
replaced. This leaves the editor in an inconsistent state: old data with a new mapper name and
no unsaved changes flag. Should only reset `has_unsaved_changes` and `MAPPER_NAME` when data
is actually loaded.

### Non-atomic file writes risk data loss
`save_mapper` (`utils.py:150`) opens with `'w'` mode which truncates the existing file before
writing. If the write fails mid-way (disk full, process killed), the original mapper file is
destroyed. Consider writing to a `.tmp` file first then using `os.replace()` for an atomic swap.

### Levy percentage type inconsistency
`main.py:166` uses `sum([int(row[2]) for row in data])` (with explicit `int()` cast) but
`main.py:195` and `main.py:228` use `sum([row[2] for row in data])` without the cast. Both
should be consistent — if a non-integer value ever slips in from a corrupted mapper file, the
uncast lines would silently break.

### XML button warns about import even for export
The unsaved-changes dialog on `XML_BUTTON` (`main.py:1524`) says "Importing will discard them"
but the popup offers both Import and Export. Exporting doesn't discard anything. Consider
rewording or moving the check to after the user chooses Import vs Export.

### `WIN_CLOSED` + confirmation popup is fragile
In `popup_levy_percentage` (`main.py:194-204`), showing `popup_yes_no` after receiving
`WIN_CLOSED` then calling `continue` to re-enter `window.read()` works in FreeSimpleGUI but is
a fragile pattern — the window handle may be partially destroyed. Consider handling `WIN_CLOSED`
separately from the `Exit` button.

### Empty faction list after import shows "DEFAULT"
If an imported mapper has no faction mappings, `FACTION_LIST` is `[]` and `current_faction`
falls back to `'DEFAULT'` (`main.py:1552`). The combo dropdown shows no options but displays
`'DEFAULT'` — a faction that doesn't exist. Edge case but confusing if encountered.

---

## Medium Priority

### No keyboard shortcuts
Power users creating hundreds of mappings must click "Add Mapping" every time. Adding
keyboard shortcuts (e.g. Enter to add, Delete to remove) would significantly speed up
workflow in the main mapper and title mapper windows.

### Heritage window ">>>"/"<<<" buttons are cryptic
In `heritage_window()` (`main.py:823`), the ">>>" and "<<<" buttons are not self-explanatory.
Renaming them to "Add >>>" and "<<< Remove" (or adding tooltips) would help new users
understand which direction moves items.

### No progress indicator during validation
"Refresh Current Mappers" (`main.py:1646-1677`) blocks the UI while running
`mapping_validation()` + `summary()`. On large mod sets this can hang for several seconds
with no visual feedback. A spinner, progress bar, or status text update would help.

---

## Lower Priority

### No "Save As" option
Currently you can only save to the current mapper name or set a name once. There is no way
to fork a mapper under a new name without manually renaming the file on disk. A "Save As"
button that prompts for a new name would support this workflow.

### Heritage window has no search/filter
The CK3 MAA and Attila unit lists both have search bars and source filters, but the heritage
list (which can be equally long with many cultures) has no search capability. Adding a search
bar to `heritage_window()` would improve usability for large mod sets.

### Faction list editing is text-based
`popup_faction_list()` (`main.py:279`) uses a raw multiline text field for editing factions.
A listbox with Add/Remove/Rename buttons would be less error-prone, avoiding issues with
accidental whitespace, empty lines, or formatting mistakes.

### Missing keys popup reuses wrong element key name
In `popup_missing_keys()` (`main.py:245`), the table uses `key='LEVY_PERCENTAGE_TABLE'` — a
copy-paste leftover from the levy popup. Not functionally broken since the popup has no
event handling, but confusing for maintenance. Should be renamed to something like
`'MISSING_KEYS_TABLE'`.

### Export workflow requires too many sequential popups
The export path in `popup_xml_import_export()` (`main.py:503-510`) chains 4 popups in a row:
file picker, tag input, start date, and end date. Consolidating these into a single export
configuration dialog with all fields visible at once would be a smoother experience.

### No visual distinction for special unit types in mapping list
GENERAL, KNIGHTS, and LEVY entries in the mappings listbox look identical to regular MAA
entries. Color-coding or grouping special types would improve scannability when reviewing
a faction's mappings.
