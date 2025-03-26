import pandas as pd
from pickle import load
import streamlit as st
import pgeocode
import requests
from bs4 import BeautifulSoup

model = load(open('matt_xgbr_opt.sav', "rb"))

st.title("Buying a Home in Florida")

# Treasury rate for the day
url = 'https://fred.stlouisfed.org/series/DGS10'
response = requests.get(url)
if response:
    soup = BeautifulSoup(response.text, features='html.parser')
t_rate = soup.find_all("span", class_="series-meta-observation-value")
t_rate = float(t_rate[0].text) * 0.01

st.write("Predictions based on today's Treasury rate of: ", t_rate)

# Inputs with necessary transformations

# Property type
property_types = ['Single Family','Condo','Townhouse','Mobile']
property_type = st.selectbox("Property Type:", options=property_types)

# City
cities = load(open('model_cities.sav', "rb"))
city = st.selectbox("City:", options=cities)

# Generating zip codes for chosen city to put into selectbox
nomi = pgeocode.Nominatim('US')
df = nomi._data

city_zip_dict = load(open('city_zip_dict.sav', "rb"))
city_zips = city_zip_dict.get(city, [])
zip_code = st.selectbox("Zip Code:", options=city_zips)

# Getting approximate latitude and longitude from zip code
zip_info = nomi.query_postal_code(zip_code)
latitude = zip_info.latitude
longitude = zip_info.longitude

# Getting county from zip code

zip_county_dict = load(open('zip_county_dict.sav', "rb"))
county = zip_county_dict.get(zip_code)

# Remaining inputs
beds = [0,1,2,3,4,5]
bedrooms = st.selectbox("Bedrooms:", options=beds)

baths = [1,2,3,4,5]
bathrooms = st.selectbox("Bathrooms:", options=baths)

sq_footage = st.number_input("Square Footage:", value=1612, placeholder='Enter a number') # median from FRED
lot_size = st.number_input("Lot Size in square feet (enter 0 for Condos):", value=10000, placeholder='Enter a number')

floors = [1, 2, 3, 4]
floor_count = st.selectbox("Floor Count", options=floors)

year_built = st.number_input("Year Built (1980 to 2025):", value=2024, placeholder='Enter a number from 1920 to the present:')
years_old = 2025 - year_built

y_n = ['yes','no']
y_n_map = {'yes':1,'no':0}

pool = st.selectbox("Pool:", options=y_n)
pool = y_n_map[pool]

garage = st.selectbox("Garage:", options=y_n)
garage = y_n_map[garage]

spaces_num = [1,2,3,4,5,6]
garage_spaces = garage = st.selectbox("Number of garage spaces:", options=spaces_num)

cooling = st.selectbox("Cooling:", options=y_n)
cooling = y_n_map[cooling]

heating = st.selectbox("Heating:", options=y_n)
heating = y_n_map[heating]

fireplace = st.selectbox("Fireplace:", options=y_n)
fireplace = y_n_map[fireplace]

# Creating a dataframe of the input
data = pd.DataFrame([{
    'latitude': latitude,
    'longitude': longitude,
    'bedrooms': bedrooms,
    'bathrooms': bathrooms,
    'squareFootage': sq_footage,
    'lotSize': lot_size,
    'floorCount': floor_count,
    'years_old': years_old,
    'pool': pool,
    'cooling': cooling,
    'heating': heating,
    'fireplace': fireplace,
    'garage': garage,
    'garageSpaces': garage_spaces,
    't_rate': t_rate,
    'city':city,
    'zipCode': zip_code,
    'county':county,
    'propertyType': property_type
}])

num_var = data.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_var = data.select_dtypes(include='object').columns.tolist()

# Getting dummies
cat_data = pd.get_dummies(data[cat_var])
processed_data = pd.concat([data[num_var], cat_data], axis=1)

# Reindexing with original model columns
model_cols = load(open('model_columns.sav', "rb"))
processed_data = processed_data.reindex(columns=model_cols, fill_value=0)

# Sending input through model
prediction = None
if st.button("Predict Price"):
    prediction = round(model.predict(processed_data)[0])
    st.write(f"Price in USD: $ {prediction:,.2f}")