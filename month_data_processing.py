import pandas as pd
import networkx as nx

def clean_data(input_csv):
    """Data cleaning: remove missing values, duplicate values, and standardize time fields"""

    data = pd.read_csv(input_csv)

    # Remove missing and duplicate values
    data = data.dropna()
    data = data.drop_duplicates()

    # Convert to a standard time format and extract time features(date, hour, and weekday)
    data['start_time'] = pd.to_datetime(data['started_at'], errors='coerce')
    data['end_time'] = pd.to_datetime(data['ended_at'], errors='coerce')
    data['start_date'] = data['start_time'].dt.date
    data['start_hour'] = data['start_time'].dt.hour
    data['start_weekday'] = data['start_time'].dt.weekday

    # Clean station name
    data['start_station_name'] = data['start_station_name'].str.strip()
    data['end_station_name'] = data['end_station_name'].str.strip()

    # Remove rows with invalid latitude and longitude (e.g., 0, 0 or out-of-range values)
    data = data[
        (data['start_lat'].between(-90, 90)) & 
        (data['start_lng'].between(-180, 180)) &
        (data['end_lat'].between(-90, 90)) & 
        (data['end_lng'].between(-180, 180))
    ]

    print(f"Total trips: {len(data)}")
    print(f"Unique start stations: {data['start_station_name'].nunique()}")
    print(f"Unique end stations: {data['end_station_name'].nunique()}")

    return data


def build_network(data, output_gml):
    """Construct the network graph and save as a GML file."""

    # Calculate the traffic as the edge weights
    edges = data.groupby(['start_station_name', 'end_station_name']).size().reset_index(name='weight')

    G = nx.DiGraph() #Directed weighted graph

    nodes = set(edges['start_station_name']).union(set(edges['end_station_name']))
    G.add_nodes_from(nodes)
    for _, row in edges.iterrows():
        G.add_edge(row['start_station_name'], row['end_station_name'], weight=row['weight'])

    # save as GML file
    nx.write_gml(G, output_gml)
    print(f"The network graph has been saved as {output_gml}.")


def main():
    input_csv = '202004-divvy-tripdata.csv'
    output_gml = 'month_bike_network.gml'

    # data cleaning
    data = clean_data(input_csv)
    print("Data cleaning completed")

    # Save cleaned data for time series analysis
    data.to_csv('cleaned_bike_data.csv', index=False)
    print("Cleaned data saved to cleaned_bike_data.csv.")

    # month data
    month_data = data[[
        'ride_id', 'rideable_type', 'start_station_name', 'end_station_name', 
        'start_lat', 'start_lng', 'end_lat', 'end_lng', 
        'start_time', 'end_time', 'start_date', 'start_hour', 'start_weekday', 'member_casual'
    ]]
    month_data.to_csv('month_data.csv', index=False)
    print("Time series data saved to month_data.csv")

    # Create the network graph 
    build_network(data, output_gml)
    print("Network building completed")

if __name__ == "__main__":
    main()

