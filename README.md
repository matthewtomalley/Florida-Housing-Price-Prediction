# Predicting home prices in Florida

This project uses data from RentCast API to predict home prices in Florida using machine learning software.
## Structure

The project is organized as follows:

- `src` - contains app.py, the main Python script that runs a streamlit app to make predictions using XGBoostRegressor, as well as any other files needed by the app
- `images` - some saved png files from the exploratory data analysis
- `EDA` - Various notebooks exploring the data and machine learning algorithms.
- `utils.py` - This file contains utility code for operations like database connections.
- `requirements.txt` - This file contains the list of necessary python packages. There is a second requirements.txt in the src folder used by the streamlit app.
- `models/` - This directory contains saved versions of the models developed, including the one connected to the app
- `data/` - This directory contains the following subdirectories:
  - `interin/` - For intermediate data that has been transformed.
  - `processed/` - For the final data to be used for modeling.
  - `raw/` - For raw data without any processing.
 
## Running the Application

To run the application, execute the app.py script from the src folder of the project directory:

```bash
streamlit run app.py
```

## Link to the dedicated website for this project

[FusionAIntellect](https://fusionaintellect.com/index.html)
