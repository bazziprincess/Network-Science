import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from geopy.distance import geodesic

# Load bike trip data
data = pd.read_csv('zhong.csv')

# ----------------------------
# Step 1: Count visits by hour
# ----------------------------
# Convert time columns to datetime format and extract hourly intervals
data['start_time'] = pd.to_datetime(data['start_time'])
data['end_time'] = pd.to_datetime(data['end_time'])
data['hour'] = data['start_time'].dt.floor('H')  # Round to the nearest hour

# Count hourly outflows (departures)
hourly_outflow = data.groupby(['start_station_name', 'hour']).size().rename('outflow')

# Count hourly inflows (arrivals)
hourly_inflow = data.groupby(['end_station_name', 'hour']).size().rename('inflow')

# Combine inflow and outflow statistics
hourly_stats = pd.concat([hourly_outflow, hourly_inflow], axis=1).fillna(0)

# Calculate total visits (sum of inflow and outflow)
hourly_stats['total_visits'] = hourly_stats['inflow'] + hourly_stats['outflow']

# ----------------------------
# Step 2: Filter records with total_visits > 20
# ----------------------------
# Reset index to convert multi-level index into columns
hourly_stats_reset = hourly_stats.reset_index()

# Filter records where total visits exceed 20
top_visits = hourly_stats_reset[hourly_stats_reset['total_visits'] > 20]

# Count the number of hours with visits > 20 for each station
top_visits_count = top_visits.groupby('level_0').size().reset_index(name='hours_above_20')

# Sort the results by the number of hours in descending order
top_visits_count = top_visits_count.sort_values(by='hours_above_20', ascending=False)

# Print the data
print("Number of hours with visits > 20 for each station:")
print(top_visits_count)

# ----------------------------
# Plot bar chart
# ----------------------------
y_ticks = np.arange(0, top_visits_count['hours_above_20'].max() + 1, 1)

plt.figure(figsize=(12, 8))
plt.bar(top_visits_count['level_0'], top_visits_count['hours_above_20'], color='skyblue')
plt.xticks(rotation=90)
plt.yticks(y_ticks)  # Set y-axis ticks to integers
plt.xlabel('Station Name')
plt.ylabel('Number of Hours with Visits > 20')
plt.title('Number of Hours with Total Visits > 20 per Station (One Month)')
plt.tight_layout()
plt.show()

# ----------------------------
# Step 3: Count stations with more than 25 days without visits
# ----------------------------
# Extract the date from the start_time column
data['date'] = data['start_time'].dt.date

# Count daily visits for each station
station_daily_visits = data.groupby(['start_station_name', 'date']).size().unstack(fill_value=0)

# Count the number of days each station had no visits
days_not_visited = (station_daily_visits == 0).sum(axis=1)

# Filter stations with more than 25 days without visits
stations_over_25_days_no_visits = days_not_visited[days_not_visited > 25]

# Sort the results by the number of days in descending order
stations_over_25_days_no_visits = stations_over_25_days_no_visits.sort_values(ascending=False)

# Print the results
print("Stations with more than 25 days without visits:")
print(stations_over_25_days_no_visits)

# ----------------------------
# Step 4: Check proximity of alternative stations
# ----------------------------
# Extract station coordinates
station_coords = data[['start_station_name', 'start_lat', 'start_lng']].drop_duplicates()
station_coords.columns = ['station_name', 'lat', 'lng']

# Define a function to find nearby stations
def find_nearby_stations(station_name, lat, lng, radius=0.5):
    nearby_stations = []
    for _, row in station_coords.iterrows():
        distance = geodesic((lat, lng), (row['lat'], row['lng'])).kilometers
        if distance <= radius and row['station_name'] != station_name:
            nearby_stations.append((row['station_name'], distance))
    return nearby_stations

# Check each station with more than 25 days without visits
no_visit_station_details = []
stations_with_alternatives = []  # Track stations with nearby alternatives
for station in stations_over_25_days_no_visits.index:
    station_detail = station_coords[station_coords['station_name'] == station]
    if not station_detail.empty:
        lat, lng = station_detail.iloc[0]['lat'], station_detail.iloc[0]['lng']
        nearby = find_nearby_stations(station, lat, lng)
        no_visit_station_details.append({'station': station, 'no_visit_days': stations_over_25_days_no_visits[station], 'nearby_stations': nearby})
        if nearby:
            stations_with_alternatives.append(station)

# Print details of stations with nearby alternatives
print("Details of stations with more than 25 days without visits and their nearby alternatives:")
for detail in no_visit_station_details:
    print(f"Station: {detail['station']}, No-Visit Days: {detail['no_visit_days']}, Nearby Stations: {detail['nearby_stations']}")

# Print stations with nearby alternatives
print("\nStations with nearby alternatives:")
print(stations_with_alternatives)

# ----------------------------
# Plot bar chart for stations with more than 25 days without visits
# ----------------------------
plt.figure(figsize=(12, 8))
plt.bar(stations_over_25_days_no_visits.index, stations_over_25_days_no_visits.values, color='salmon')
plt.xticks(rotation=90)
plt.xlabel('Station Name')
plt.ylabel('Number of Days Not Visited')
plt.title('Stations with More Than 25 Days Not Visited (One Month)')
plt.ylim(25, 30)
plt.tight_layout()
plt.show()
