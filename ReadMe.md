# MPL and OSC Data Processing Script

## Overview
This project provides a Python script to process and visualize data from MPL (Micro Pulse Lidar) and OSC (Oscilloscope) systems. The script supports:

- Reading MPL and OSC data from CSV files.
- Processing the data to compute digitizer signals and distances.
- Visualizing the processed data in combined plots.
- Saving and loading additional calibration data from JSON files.

## Features

1. **MPL Data Processing**:
   - Extracts required columns (`copol_raw`, `copol_background`, `range_raw`) from a CSV file.
   - Calculates adjusted distances and R-squared values.

2. **OSC Data Processing**:
   - Reads multiple CSV files from a specified folder.
   - Filters and processes time and amplitude data to calculate distances and digitizer signals.

3. **Visualization**:
   - Combines MPL and OSC data in a single plot with dual axes.
   - Displays calibration data for comparison.

4. **JSON Integration**:
   - Loads calibration data from a JSON file.
   - Saves processed MPL and OSC data to a JSON file.

5. **Dynamic File Browsing**:
   - Supports file selection using a GUI dialog.

## Requirements

- Python 3.6 or later
- Required libraries:
  - `pandas`
  - `matplotlib`
  - `tkinter`
  - `os`
  - `datetime`
  - `json`

Install dependencies using pip:
```bash
pip install pandas matplotlib
```

## File Structure

- `mplfile(csv_file)`: Processes MPL data from a CSV file.
- `oscfile(folder_path)`: Processes OSC data from multiple CSV files in a folder.
- `range_mpl(range_raw)`: Converts MPL raw ranges to meters.
- `R_squared_mpl(copol_raw, copol_background, Distance)`: Computes R-squared values for MPL.
- `cal_osc(combined_data)`: Processes OSC data to calculate distances and digitizer signals.
- `plot_data(...)`: Visualizes MPL and OSC data on dual-axis plots.
- `load_json_data(json_file_path)`: Loads calibration data from a JSON file.
- `save_to_json(...)`: Saves processed MPL and OSC data to a JSON file.

## How to Use

### 1. Prepare Input Files
- Ensure your MPL data file contains the following columns:
  - `copol_raw`
  - `range_raw`
  - `copol_background`
- Place your OSC CSV files in a folder.
- Optionally, provide a JSON file with calibration data.

### 2. Run the Script

Navigate to the folder containing the script `osc&mpl-chart-add-flip.py`:
```bash
cd compla
```

Run the script with Python:
```bash
python osc&mpl-chart-add-flip.py
```

### 3. Input Data
Place your input files in the `excample-file` folder:
- Example MPL data: `excample-file/mpl/your_mpl_file.csv`
- Example OSC data: `excample-file/osc/your_osc_folder`
- Example JSON calibration data: `excample-file/your_json_file.json`

Update the script paths if necessary to point to the correct input files.

### 4. Visualize Results
- The script will display a plot with MPL and OSC data.
- Results will be saved in a JSON file in the working directory.

### 5. Debugging
Use the `debug(...)` function to inspect intermediate data.

## Example Output

1. **Plot**: Combined MPL and OSC data with distances and digitizer signals.
2. **JSON File**: Contains processed MPL and OSC data.

## Error Handling
- Missing columns in MPL or OSC data will raise an error.
- Empty OSC folders or incorrect file paths will notify the user.

## Future Improvements
- Add automated testing for individual functions.
- Enhance GUI support for better user interaction.
- Add support for additional data formats.

## License
This project is licensed under the MIT License.

## Author
วิทยา คำตัน (Wittaya Kamtan)

