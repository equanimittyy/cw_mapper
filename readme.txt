// An executible to validate Crusader Wars (CW) Unit Mappers. //

## ⚠ ENSURE THE 'cw_mapping_validator' FOLDER IS PLACED IN THE CW/TOOLS FOLDER

# Workflow
1. Use PFM/RPFM to export the unit db's from Attila as .tsv, and place in the "attila_exports" folder, allowing it to create subfolders as necessary. 
You may need to rename the .tsv's to ensure you don't overwrite it when you repeat it for each of the Attila sources for unit keys.
    The file structure should look like:
    /attila_exports/db/main_units_tables/*.tsv

2. Run 'cw_mapping_validator.exe'. It will process all of the Attila unit key .tsv's you exported, and compare that to the mapping files in the 
CW installation directory, as well as the CK3 installation directory.


============================================================================================================================


## Explanation on the reports
The purpose of the report .csv's is to assist you in finding broken or missing keys in either Attila or CK3.

# For culture mapping:
report_cw_cultures = Attempts to map the current cultures found in CW to files found in CK3. 
⚠ If the ['ck3_source'] field is empty, it means CW has additional culture(s) not found in CK3.

source_ck3_cultures = The source information from CK3. 
⚠ If the ['used_in_cw'] field is False, it means this culture is not found in any CW mapping preset.


# For man-at-arms mapping:
report_cw_maa = Attempts to map the current MAA found in CW to files found in the "attila_exports" folder (follow the structure mentioned above). 
⚠ If the ['attila_source'] field is empty, it means the ['attila_map_key'] was not found in the exported files from Attila.
This may be because:
    > The unit key has changed in Attila.
    > You didn't export all of the files from Attila.

source_attila_mapping = The source information from the "attila_exports" folder, presumably exported by you from Attila using PFM/RPFM.
⚠ If the ['used_in_cw'] field is False, it means the Attila unit key is not found in any CW mapping presets. (Not necessarily bad, since not all units from Attila are being used by CW.)

source_ck3_maa = The source information from the CK3 installation.
⚠ If the ['used_in_cw'] field is False, it means the MAA from CK3 is not found in any CW mapping presets.