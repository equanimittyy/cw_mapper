## ⚔️ Crusader Wars (CW) Unit Mapper Readme

This program validates the unit mapping files used by the Crusader Wars mod. It compares unit keys exported from **Total War: Attila** against culture and Man-at-Arms (MAA) definitions found in **Crusader Kings III (CK3)** and its mods.

---

## 🛠️ Setup and Workflow

### 1. Setup
> **Location:** Ensure the `cw_mapper` folder is placed inside your **CW/TOOLS** directory.

### 2. Attila Data Export
1.  Use a tool like **PFM/RPFM** to export the unit database files (`db/main_units_tables`) from **Attila** as **`.tsv`** files.
2.  Place these exported `.tsv` files into the tool's subfolder: **`attila_exports/db/main_units_tables/`**.
    You may need to create this subfolder.
    > **Tip:** You may need to rename the `.tsv` files if you export from multiple Attila sources to prevent overwriting.

### 3. Application Use
1.  Run **`cw_mapper.exe`**.
2.  Click 'Refresh Current Mappers' The program will automatically process the exported Attila unit keys and compare them against the mapping files in the CW and CK3 installation directories.
3.  The program also includes a custom mapping functionality. Press 'Create Custom Mapper' to run this.
3.1.  **Optional:** The program will prompt you to enter the names of any **additional CK3 mods** you want to create custom mappers for.

### 4. Output
The program will generate several **`.csv` report files** (explained below) to help you identify broken or missing keys in both games.
As well as displaying a summary report of all mappers available, including any custom ones.

================================================================================

                                 REPORT EXPLANATIONS

================================================================================

### CULTURE MAPPING REPORTS ###

Report File: report_cw_cultures
Purpose: Shows CW cultures mapped against Crusader Kings III (CK3) cultures.
Warning: If ['ck3_source'] field is EMPTY, CW has culture(s) not found in CK3.

Report File: source_ck3_cultures_keys
Purpose: Lists all culture data found in CK3.

--------------------------------------------------------------------------------

### MAN-AT-ARMS (MAA) MAPPING REPORTS ###

Report File: report_cw_maa
Purpose: Shows CW MAA keys mapped against the Attila exported files.
Warning: If ['attila_source'] field is EMPTY, the Attila unit key was not found.
         This may mean: 1) The unit key has changed in Attila, or 2) You didn't export all necessary files.

Report File: source_attila_mapping_keys
Purpose: Lists all unit key data found in your 'attila_exports' folder.

Report File: source_ck3_maa_keys
Purpose: Lists all MAA data found in CK3.

================================================================================
```