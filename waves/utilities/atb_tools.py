"""Provides a set of tools to process and verify config files needed for ATB work."""

__author__ = "Nick Riccobono"
__email__ = "nicholas.riccobono@nrel.gov"

import shutil
from pathlib import Path

import numpy as np
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
        file = files_to_check[i]
        # parse out useful strings/filenames/etc
        # filename = file.split(".")[0]
        if file in missing:
            print(f"{file} is missing.")

        if "Monopile" in row["Foundation type"]:
            # print(f"{row['Site']} is a monopile")
            for m in missing:
                if file in m:
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
                if file in m:
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
        if int(row["Plant capacity, MW"]) == 1000:
            layout_file = "1000mw_fixed_bottom_2023_layout"
            project_capacity = 996
        else:
            layout_file = "base_fixed_bottom_2022_layout"
            project_capacity = 600

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
                "num_turbines": int(project_capacity / row["Turbine rating, MW"]),
                "turbine_spacing": int(row["Spacing between turbines, km"][0]),
            },
            "turbine": str(row["Turbine rating, MW"]) + "MW_generic",
            "array_system_design": {"cables": {"location_data": layout_file}}
            # "design_phases" : design_phases,
            # "install_phases" : install_phases,
        }

        need_change = _check_config_for_changes(
            path, files_to_check[i], site_config_mapping, verbose=verbose
        )
        # print(need_change)

        if need_change:
            # print(need_change[0])
            config = load_yaml(path, need_change[0])

            for k, v in site_config_mapping.items():
                # print("Update: ", k, v)

                if isinstance(v, dict):
                    for k2, v2 in v.items():
                        # print("Update2: ", k, k2, v2)
                        # print(type(config), type(k), type(k2), type(v2))
                        # print(config[k])
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
            if files_to_check[i] in m:
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

        if int(row["Plant capacity, MW"]) == 1000:
            layout_file = "1000mw_fixed_bottom_2023_layout.csv"
            project_capacity = 996
        else:
            layout_file = "base_fixed_bottom_2022_layout.csv"
            project_capacity = 600

        site_config_mapping = {
            "name": filename,
            "weather": weather_file,
            "layout": layout_file,
            "project_capacity": project_capacity,
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

    floris_config = load_yaml(path.parent, "base_floating_2023_floris_jensen.yaml")

    for i, row in df.iterrows():
        for m in missing:
            if files_to_check[i] in m:
                shutil.copy(path.parent / "base_floating_2023_floris_jensen.yaml", path / m)

        file = files_to_check[i]
        # parse out useful strings/filenames/etc
        filename = "_".join(file.split("_")[:-1])

        # assign to a mapping dictionary to rewrite config files
        # TODO: Add floris tool to update 1000MW or 600MW farms and layouts
        floris_996mw_df = pd.read_csv(Path(path.parent / "floris_layout_996MW.csv"))

        if int(row["Plant capacity, MW"]) == 1000:
            plant_capacity = 996  # 83 turbines x 12MW
            layout_x = list(floris_996mw_df["layout_x"])
            layout_y = list(floris_996mw_df["layout_y"])

            turbine_type = list(floris_996mw_df["turbine_type"])
        else:
            plant_capacity = 600  # 50 x 12MW
            layout_x = floris_config["farm"]["layout_x"]
            layout_y = floris_config["farm"]["layout_y"]

            turbine_type = floris_config["farm"]["turbine_type"]

        # print(layout_x)

        site_config_mapping = {
            "description": filename + " Layout using Jensen-Jimenez",
            "name": filename + " Layout Jensen",
            "farm": {
                "layout_x": layout_x,
                "layout_y": layout_y,
                "turbine_type": turbine_type,
            },
        }
        # print(len(site_config_mapping["farm"]["layout_y"]))

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


def _isPerfect(N):
    """Function to check if a number is perfect square or not

    taken from:
    https://www.geeksforgeeks.org/closest-perfect-square-and-its-distance/
    by sahishelangia
    """
    if np.sqrt(N) - np.floor(np.sqrt(N)) != 0:
        return False
    return True


def _getClosestPerfectSquare(N):
    """Function to find the closest perfect square taking minimum steps to
        reach from a number

    taken from:
    https://www.geeksforgeeks.org/closest-perfect-square-and-its-distance/
    by sahishelangia
    """
    if _isPerfect(N):
        distance = 0
        return N, distance

    # Variables to store first perfect square number above and below N
    aboveN = -1
    belowN = -1
    n1 = 0

    # Finding first perfect square number greater than N
    n1 = N + 1
    while True:
        if _isPerfect(n1):
            aboveN = n1
            break
        else:
            n1 += 1

    # Finding first perfect square number less than N
    n1 = N - 1
    while True:
        if _isPerfect(n1):
            belowN = n1
            break
        else:
            n1 -= 1

    # Variables to store the differences
    diff1 = aboveN - N
    diff2 = N - belowN

    if diff1 > diff2:
        return belowN, -diff2
    else:
        return aboveN, diff1


def make_floris_grid_layout(n_wt, D, grid_spc):
    """Make a grid layout (close as possible to a square grid)

    Inputs:
    -------
        n_wt : float
            Number of wind turbines in the plant
        D : float (or might want array_like if diff wt models are used)
            Wind turbine rotor diameter(s) in meters
        grid_spc : float
            Spacing between rows and columns in number of rotor diams D
        plant_cap_MW : float
            Total wind plant capacity in MW

    Returns
    -------
        layout_x : array_like
            X positions of the wind turbines in the plant
        layout_y : array_like
            Y positions of the wind turbines in the plant
    """
    # Initialize layout variables
    layout_x = []
    layout_y = []

    # Find the closest square root
    close_square, dist = _getClosestPerfectSquare(n_wt)
    side_length = int(np.sqrt(close_square))

    # Build a square grid
    for i in range(side_length):
        for k in range(side_length):
            layout_x.append(i * grid_spc * D)
            layout_y.append(k * grid_spc * D)

    # Check dist and determine what to do
    if dist == 0:
        # do nothing
        pass
    elif dist > 0:
        # square>n_wt : remove locations
        del layout_x[close_square - dist : close_square]
        del layout_y[close_square - dist : close_square]
    else:
        # square < n_w_t : add a partial row
        for i in range(abs(dist)):
            layout_x.append(np.sqrt(close_square) * grid_spc * D)
            layout_y.append(i * grid_spc * D)

    return layout_x, layout_y


import matplotlib.pyplot as plt


# import seaborn as sns


def breakdown_plots(df):
    """"""

    # Raw CapEx
    fig = plt.figure(figsize=(8, 5), dpi=200)
    ax = fig.add_subplot(111)

    # Set all the columns as x labels (strip some of the )
    xlabels = list(df.columns)

    x_data = df.column

    # print(df[x_data[4]].index.tolist())
    # df.T.plot(kind='bar', stacked=True, ax=ax)
    new_df = pd.DataFrame()

    # have to drop soft cost columns again.
    # soft_costs=['construction_insurance_capex',
    #            'decomissioning_costs', 'construction_financing', 'procurement_contingency_costs',
    #            'install_contingency_costs', 'project_completion_capex']

    # for x in x_data:
    #    new_df = pd.concat([new_df, df[x].T.drop(labels=soft_costs, axis=1)])

    # new_df.plot(kind='bar', stacked=True, ax=ax, color=sns.color_palette("Set1", len(new_df.iloc[0])))
    plt.xticks(range(0, len(x_data)), xlabels, rotation=45)
    plt.tight_layout()

    ax.set_xlabel("")
    ax.set_ylabel("CapEx ($)")

    # handles, labels = ax.get_legend_handles_labels()
    ax.legend(bbox_to_anchor=(1.5, 0), loc="lower right", reverse=True)
