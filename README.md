# Tennis Data Processing and Analysis

This project processes and analyzes tennis match data, including singles, doubles, futures, and qualification matches. The data is sourced from [Jeff Sackmann's](https://github.com/JeffSackmann/tennis_atp/) comprehensive tennis dataset repository, hosted on GitHub. The script consolidates and cleans the data, providing statistical insights on players' performance, rankings, and more.


## Table of Contents

1. [Project Structure](#project-structure)
2. [Data Sources](#data-sources)
3. [Functionality](#functionality)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Outputs](#outputs)
7. [Tableau de bord interactif](#tableau-de-bord-interactif)
8. [License](#license)
9. [Acknowledgements](#acknowledgements)

## Project Structure

The project includes the following key components:

- `tennis_data_processing.py`: Main script for loading, cleaning, and processing tennis match data.
- `rawData.csv`: Consolidated raw tennis match data.
- `jsonData/`: Directory storing processed data in JSON format.
- `Tableau/`: Directory storing CSV versions of the processed data for further analysis or visualization.

## Data Sources

The data used in this project comes from the **Tennis ATP** dataset, compiled and maintained by **Jeff Sackmann** and available on [GitHub](https://github.com/JeffSackmann). This dataset includes the following categories:

- **Singles Matches (1968-2024)**: Historical data for ATP singles matches.
- **Doubles Matches (2000-2019)**: Historical data for ATP doubles matches.
- **Futures Matches (1991-2024)**: Futures tournament matches.
- **Qualification & Challenger Matches (1978-2024)**: Qualification and Challenger tournaments.

All data is publicly available under Jeff Sackmann’s repository: [tennis_atp](https://github.com/JeffSackmann/tennis_atp).

## Functionality

### Main Functions

1. **`update_data()`**: 
   - Downloads, merges, and processes match data from multiple sources.
   - Saves the consolidated raw data to `rawData.csv`.

2. **`clean_data(final_df)`**:
   - Cleans the raw data, unifying player information and match results for both winners and losers.
   - Calculates statistics like win/loss records, rankings, surface performance, and serve stats.
   - Saves processed data in JSON format under the `jsonData` directory.

## Dashboard link

[click here if you want to access to the Dashboard](https://public.tableau.com/views/Tennis_V2/Tableaudebord1)

## License

No specific license is provided for this project. However, ensure compliance with the terms of usage for Jeff Sackmann’s tennis dataset before using the data for commercial purposes.

## Acknowledgements

This project is made possible thanks to the **Tennis ATP** dataset compiled by **Jeff Sackmann**. You can find the original repository and further datasets on [GitHub](https://github.com/JeffSackmann/tennis_atp).