"""Provides a set of tools to process and verify config files needed for ATB work."""

__author__ = "Nick Riccobono"
__email__ = "nicholas.riccobono@nrel.gov"

import shutil
from pathlib import Path

import pandas as pd

from waves.utilities import load_yaml, write_yaml


def check_ref_sites(path=str | Path, filename=str | Path, verbose=True):
    """Read in the reference site excel file. Skip the first row."""
    path = Path(path).resolve()

    df = pd.read_excel(path / filename, skiprows=[0])

    year = 2023
    files_to_check = [f"Site{row['Site']}_atb_{year}.yaml" for _, row in df.iterrows()]

    # determine which files are present based on the reference site table.
    template_path = Path(path.parent / "config")
    # find_missing_files(
    #    path, files_to_check, Path(template_path / "base_fixed_bottom_2023.yaml"), verbose=verbose
    # )

    # update the files based on data in the reference site table.
    update_waves_files(path, files_to_check, df, verbose=verbose)

    orbit_path = Path(path / "orbit_config").resolve()

    orbit_files_to_check = [
        f"Site{row['Site']}_atb_{year}_install.yaml" for _, row in df.iterrows()
    ]

    update_orbit_files(orbit_path, orbit_files_to_check, df, verbose=verbose)

    wombat_path = Path(path / "wombat_config").resolve()

    wombat_files_to_check = [
        f"Site{row['Site']}_atb_{year}_operations.yaml" for _, row in df.iterrows()
    ]

    # find_missing_files(
    #    wombat_path,
    #    wombat_files_to_check,
    #    Path(template_path / "base_fixed_bottom_2023_operations.yaml"),
    #    verbose=verbose,
    # )

    update_wombat_files(wombat_path, wombat_files_to_check, df, verbose=verbose)

    floris_path = Path(path / "floris_config").resolve()
    floris_str = "floris_jensen"
    floris_files_to_check = [
        f"Site{row['Site']}_atb_{year}_{floris_str}.yaml" for _, row in df.iterrows()
    ]

    # find_missing_files(
    #    floris_path,
    #    floris_files_to_check,
    #    Path(template_path / f"base_fixed_bottom_2023_{floris_str}.yaml"),
    # )

    update_floris_files(floris_path, floris_files_to_check, df, verbose=verbose)

    if verbose:
        # print(f"Length: {len(df)}")
        # print(df.columns)
        print(df.head())

    return df


def find_missing_files(path, files_to_check, verbose=False):
    """Check if files exist or are missing for summary prints, then copy a new config file."""
    _found = _found = [file for file in files_to_check if (path / file).exists()]

    found = pd.Series(_found).to_list()

    _missing = [file for file in files_to_check if (path / file).exists() is False]

    missing = pd.Series(_missing).to_list()

    if verbose:
        print("Found files: ", _found)
        print("Missing files: ", _missing)

    return found, missing
    # if not path.is_dir(): path.mkdir(parents=True, exist_ok=True)

    # for m in _missing:
    #    shutil.copy(file_temp, path / m)


def update_waves_files(path, files_to_check, df, verbose=False):
    """Update the files that exist."""
    found, missing = find_missing_files(path, files_to_check, verbose=verbose)

    # Generate missing files from a template
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)

    for m in missing:
        shutil.copy(path / "base_fixed_bottom_2023.yaml", path / m)

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
            "orbit_config": f"orbit_config/{filename}_install.yaml",
            "wombat_config": f"wombat_config/{filename}_operations.yaml",
            "floris_config": f"floris_config/{filename}_floris_jensen.yaml",
            "weather_profile": weather_file,
            "report_config": {"name": f"{filename.replace('_', ' ').upper()}"},
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(config)
        # print(need_change)

        if need_change:
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        config[k][k2] = v2

                else:
                    config[k] = v

            # with open(Path(path / files_to_check[i]), 'w') as fw:
            write_yaml(path, files_to_check[i], config)

        # print("After: ", config)
        # print(f"{row}")


def update_orbit_files(path, files_to_check, df, verbose=False):
    """Update the orbit files that exist."""
    found, missing = find_missing_files(path, files_to_check, verbose=verbose)

    # Generate missing files from a template
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)

    # for m in missing:
    # site_num =
    # if
    #   shutil.copy(path.parent/ "base_fixed_bottom_2023_install.yaml", path / m)

    for i, row in df.iterrows():
        # file = files_to_check[i]
        # parse out useful strings/filenames/etc
        # filename = file.split(".")[0]

        if "Monopile" in row["Foundation type"]:
            # print(f"{row['Site']} is a monopile")
            for m in missing:
                if str(row["Site"]) in m:
                    shutil.copy(path.parent / "base_fixed_bottom_2023_install.yaml", path / m)

            monopile_design = {"monopile_steel_cost": 3487.5, "tp_steel_cost": 5006.5}
            design_phases = [
                "CustomArraySystemDesign",
                "ElectricalDesign",
                "MonopileDesign",
                "ScourProtectionDesign",
            ]

            semisubmersible_design = {}

        elif "Semisubmersible" in row["Foundation type"]:
            # print(f"{row['Site']} is a semisub")
            for m in missing:
                if str(row["Site"]) in m:
                    shutil.copy(path.parent / "base_floating_2023_install.yaml", path / m)

            monopile_design = {}
            design_phases = [
                "CustomArraySystemDesign",
                "ElectricalDesign",
                "SemisubmersibleDesign",
                "MooringSystemDesign",
            ]
            semisubmersible_design = {}

        # TODO: Include dynamic cables if floating
        if "HVAC" in row["Export system"]:
            cables = (
                "XLPE_1000mm_220kV"
                if "Monopile" in row["Foundation type"]
                else "XLPE_1000mm_220kV_dynamic"
            )

        elif "HVDC" in row["Export system"]:
            cables = (
                "HVDC_2000mm_320kV"
                if "Monopile" in row["Foundation type"]
                else "HVDC_2000mm_320kV_dynamic"
            )

        # assign to a mapping dictionary to rewrite config files

        site_config_mapping = {
            # "monopile_design": monopile_design,
            # "semisubmersible_design": semisubmersible_design,
            "export_system_design": {"cables": cables},
            "site": {
                "depth": row["Water depth, m"],
                "mean_windspeed": row["Mean wind speed (at 137 m), m/s"],
                "distance": row["Distance to port, km"],
                "distance_to_landfall": row["Export cable length, km"],
            },
            "plant": {
                "num_turbines": int(600 / row["Turbine rating, MW"]),
                "turbine_spacing": int(row["Spacing between turbines, km"][0]),
            },
            "turbine": str(row["Turbine rating, MW"]) + "MW_generic",
            # "design_phases" : design_phases,
            # "install_phases" : install_phases,
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(need_change)

        if need_change:
            print(need_change[0])
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                print("Update: ", k, v)

                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        print("Update2: ", k, k2, v2)
                        print(type(config), type(k), type(k2), type(v2))
                        print(config[k])
                        # if isinstance(v2, dict):
                        #    for k3, v3 in v2.items():

                        # print("Update3: ", k3, v3)
                        config[k][k2] = v2

                else:
                    config[k] = v

            write_yaml(path, files_to_check[i], config)


def update_wombat_files(path, files_to_check, df, verbose=False):
    """Update the wombat files that exist."""
    found, missing = find_missing_files(path, files_to_check, verbose=verbose)

    # Generate missing files from a template
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)

    for i, row in df.iterrows():
        for m in missing:
            if str(row["Site"]) in m:
                shutil.copy(path.parent / "base_floating_2023_operations.yaml", path / m)

        file = files_to_check[i]
        # parse out useful strings/filenames/etc
        filename = "_".join(file.split("_")[:-1])
        weather_file = (
            "era5_40.0N_72.5W_1990_2020.csv"
            if row["Fixed/floating"] == "Fixed"
            else "era5_41.0N_125.0W_1989_2019.csv"
        )
        # assign to a mapping dictionary to rewrite config files

        site_config_mapping = {
            "name": filename,
            "weather": weather_file,
            "project_capacity": 600,
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(need_change)

        if need_change:
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                print("check: ", k, v)
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        print("check2: ", k2, v2)
                        if isinstance(v2, dict):
                            for k3, v3 in v2.items():
                                print("check3: ", k3, v3)
                                config[k][k2][k3] = v3

                        else:
                            config[k][k2] = v2

                else:
                    config[k] = v

            write_yaml(path, files_to_check[i], config)


def update_floris_files(path, files_to_check, df, verbose=False):
    """Update the floris files that exist."""
    found, missing = find_missing_files(path, files_to_check, verbose=verbose)

    # Generate missing files from a template
    if not path.is_dir():
        path.mkdir(parents=True, exist_ok=True)

    for i, row in df.iterrows():
        for m in missing:
            if str(row["Site"]) in m:
                shutil.copy(path.parent / "base_floating_2023_floris_jensen.yaml", path / m)

        file = files_to_check[i]
        # parse out useful strings/filenames/etc
        filename = "_".join(file.split("_")[:-1])

        # assign to a mapping dictionary to rewrite config files
        # TODO: Add floris tool to update 1000MW or 600MW farms and layouts
        site_config_mapping = {
            "description": filename + " Layout using Jensen-Jimenez",
            "name": filename + " Layout Jensen",
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(config)
        # print(need_change)

        if need_change:
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        if isinstance(v2, dict):
                            for k3, v3 in v2.items():
                                config[k][k2][k3] = v3

                        else:
                            config[k][k2] = v2

                else:
                    config[k] = v

            # with open(Path(path / files_to_check[i]), 'w') as fw:
            write_yaml(path, files_to_check[i], config)


def _check_config_for_changes(path, filename, mapping_dict, verbose=False):
    """Check the config yaml file for any key/value updates based on the config_mapping."""
    config = load_yaml(path, filename)

    _to_update = []
    for k, v in mapping_dict.items():
        try:
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    if isinstance(v2, dict):
                        for k3, v3 in v2.items():
                            if config[k][k2][k3] != v3:
                                print(f"{filename} {k2} has different value. ")

                            _to_update.append(filename)

                    else:
                        # if config[k][k2] != v2 or config[k]:
                        #    print(f"{filename} {k2} has different value. ")

                        _to_update.append(filename)

            else:
                if config[k] != v:
                    print(f"{filename} {k} has different value. ")

                    _to_update.append(filename)

        except KeyError:
            print(f"{filename} {k} doesn't exist. ")

            config[k] = v

    return list(set(_to_update))
