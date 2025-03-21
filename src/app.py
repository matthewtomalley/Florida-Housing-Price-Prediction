# from utils import db_connect
# engine = db_connect()

# your code here
import pandas as pd
from pickle import load
import streamlit as st
import pgeocode
import requests
from bs4 import BeautifulSoup

model = load(open('matt_test_xgb.sav', "rb"))

st.title("Buying a Home in Florida")

# Treasury rate for the day
url = 'https://fred.stlouisfed.org/series/DGS10'
response = requests.get(url)
if response:
    soup = BeautifulSoup(response.text, 'html')
t_rate = soup.find_all("span", class_="series-meta-observation-value")
t_rate = float(t_rate[0].text) * 0.01

st.write("Predictions based on today's Treasury rate of: ", t_rate)

# Inputs with necessary transformations

# Property type
property_types = ['Single Family','Condo','Townhouse','Mobile']
property_type = st.selectbox("Property Type:", options=property_types)

# City
cities = ['Jacksonville','Miami','Orlando','Tampa','Naples','Ocala','Cape Coral','Saint Petersburg','Kissimmee','Fort Myers']
city = st.selectbox("City:", options=cities)

# Generating zip codes for chosen city to put into selectbox
nomi = pgeocode.Nominatim('US')
df = nomi._data

city_zips = df[
    (df['place_name'] == city) & (df['state_code'] == 'FL')]['postal_code'].tolist()

zip_code = st.selectbox("Zip Code:", options=city_zips)

# Getting approximate latitude and longitude from zip code
zip_info = nomi.query_postal_code(zip_code)

latitude = zip_info.latitude

longitude = zip_info.longitude

# Remaining inputs
beds = [0,1,2,3,4,5,6,7,8,9,10]
bedrooms = st.selectbox("Bedrooms:", options=beds)

baths = [1,2,3,4,5,6,7,8,9,10]
bathrooms = st.selectbox("Bathrooms:", options=baths)

sq_footage = st.number_input("Square Footage:", value=1612, placeholder='Enter a number') # median from FRED
lot_size = st.number_input("Lot Size in square feet (enter 0 for Condos):", value=10000, placeholder='Enter a number')

floors = [1, 2, 3, 4]
floor_count = st.selectbox("Floor Count", options=floors)

year_built = st.number_input("Year Built", value=2024, placeholder='Enter a number from 1920 to the present:')

y_n = ['yes','no']
y_n_map = {'yes':1,'no':0}

pool = st.selectbox("Pool:", options=y_n)
pool = y_n_map[pool]

garage = st.selectbox("Garage:", options=y_n)
garage = y_n_map[garage]

cooling = st.selectbox("Cooling:", options=y_n)
cooling = y_n_map[cooling]

heating = st.selectbox("Heating:", options=y_n)
heating = y_n_map[heating]

fireplace = st.selectbox("Fireplace:", options=y_n)
fireplace = y_n_map[fireplace]

# Creating a dataframe of the input
data = pd.DataFrame([{
    'bedrooms': bedrooms,
    'bathrooms': bathrooms,
    'squareFootage': sq_footage,
    'pool': pool,
    'latitude': latitude,
    'longitude': longitude,
    'floorCount': floor_count,
    'lotSize': lot_size,
    't_rate': t_rate,
    'cooling': cooling,
    'heating': heating,
    'fireplace': fireplace,
    'yearBuilt': year_built,
    'garage': garage,
    'propertyType': property_type,
    'zipCode': zip_code
}])

# Sending input through model
prediction = None

# Preparing variables for processing
cat_var = ['propertyType','zipCode']
num_var = ['latitude','longitude','bedrooms','bathrooms','squareFootage','floorCount','lotSize','yearBuilt','pool','garage','cooling','heating','fireplace']

# Getting dummies
cat_data = pd.get_dummies(data[cat_var])
processed_data = pd.concat([data[num_var], cat_data], axis=1)

# Reindexing with original model columns
model_cols = load(open('model_columns.sav', "rb"))
processed_data = processed_data.reindex(columns=model_cols, fill_value=0)

if st.button("Predict Price"):
    prediction = str(round(model.predict(processed_data)[0]))
    st.write(f"Price in USD: $ {prediction:,.2f}")