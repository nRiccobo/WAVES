"""Provides a set of tools to process and verify config files needed for ATB work."""

__author__ = "Nick Riccobono"
__email__ = "nicholas.riccobono@nrel.gov"

import shutil
from pathlib import Path

import pandas as pd

from waves.utilities import load_yaml, write_yaml


def check_ref_sites(path=str | Path, filename=str | Path, verbose=True):
    """Read in the reference site excel file. Skip the first row"""
    path = Path(path).resolve()

    df = pd.read_excel(path / filename, skiprows=[0])

    year = 2023
    files_to_check = [f"Site{row['Site']}_atb_{year}.yaml" for _, row in df.iterrows()]

    # determine which files are present based on the reference site table.
    find_missing_files(path, files_to_check, "base_fixed_bottom_2023.yaml", verbose=verbose)

    # update the files based on data in the reference site table.
    update_waves_file(path, files_to_check, df, verbose=verbose)

    orbit_path = Path(path / "orbit").resolve()

    orbit_files_to_check = [
        f"Site{row['Site']}_atb_{year}_install.yaml" for _, row in df.iterrows()
    ]

    # find_missing_files(orbit_path, orbit_files_to_check, "base_fixed_bottom_2023_install.yaml", verbose=verbose)
    # update_orbit_file(orbit_path, orbit_files_to_check)

    if verbose:
        # print(f"Length: {len(df)}")
        # print(df.columns)
        print(df.head())

    return df


def find_missing_files(path, files_to_check, file_temp, verbose=False):
    """Check if files exist or are missing for summary prints, then copy a new config file."""
    _missing = [file for file in files_to_check if (path / file).exists() is False]

    if verbose:
        print("Missing files: ", _missing)

    for m in _missing:
        shutil.copy(path.parent / "config" / file_temp, path / m)


def update_waves_file(path, files_to_check, df, verbose=False):
    """Update the files that exist."""
    _found = [file for file in files_to_check if (path / file).exists()]

    _found = pd.Series(_found).to_list()

    if verbose:
        print("Found files: ", _found)

    for i, row in df.iterrows():
        file = files_to_check[i]
        # parse out useful strings/filenames/etc
        turbine_type = row["Fixed/floating"]
        filename = file.split(".")[0]
        weather_file = (
            "era5_40.0N_72.5W_1990_2020.csv"
            if turbine_type == "Fixed"
            else "era5_41.0N_125.0W_1989_2019.csv"
        )

        # assign to a mapping dictionary to rewrite config files
        site_config_mapping = {
            "turbine_type": turbine_type,
            "orbit_config": f"{filename}_installation.yaml",
            "wombat_config": f"{filename}_operations.yaml",
            "floris_config": f"{filename}_floris_jensen.yaml",
            "weather_profile": weather_file,
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(config)
        print(need_change)

        if need_change:
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                config[k] = v

            config["report_config"]["name"] = f"{filename.replace('_', ' ').upper()}"

            # with open(Path(path / files_to_check[i]), 'w') as fw:
            write_yaml(path, files_to_check[i], config)

        # print("After: ", config)
        # print(f"{row}")


def _check_config_for_changes(path, filename, mapping_dict, verbose=False):
    """Check the config yaml file for any key/value updates based on the config_mapping"""
    config = load_yaml(path, filename)

    if verbose:
        print("File: ", filename)

    _to_update = []
    for k, v in mapping_dict.items():
        if config[k] != v:
            print(f"{k} has different value. ")

            _to_update.append(filename)

    return _to_update
