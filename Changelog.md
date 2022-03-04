# 0.3.1
* Required Python version bumped to >=3.10
* Type hinting added to modules
* Added support for reading/writing gzipped flow field files (files with `.gz` extension)
* Most scripts now work with both specified files and file ranges
* Fixed bug where `average_data` did not correctly add velocities from the first flow field of the given set
* Various bugfixes

# 0.3
* `GmxFlow` has been added as a class to contain the flow field data
* Reading is now done with `gmx_flow.read_flow`, writing with `gmx_flow.write_flow`
* Added `draw_flow_map.py` and `draw_flow_field.py` scripts
* Submodule `data` has been renamed to `flow`

# 0.2.1
* Added `draw_flow_map.py` script for simple plotting of 1D data
* `matplotlib` is now a requirement
* `get_files_from_range` can now generate files for multiple input base paths
* `get_files_from_range` can now generate file names without checking that
  they exist using the kwarg `no_check=True`
* `get_files_from_range` can now generate files with a non-1 stride between them

# 0.2
* Package created for use with `setuptools`
* `gmx_flow` added as full module with submodules for data manipulation
  and utilities
* Scripts added to be installed along with the modules
* Added `convert_gmx_flow_1_to_2.py` script

# 0.1
* `gmx_flow.py` created as a single-file module
* `average_flow_fields.py` created as script for averaging flow fields
