import pandas as pd
import networkx as nx

def clean_data(input_csv):
    """Data cleaning: remove missing values, duplicate values, and standardize time fields"""
    data = pd.read_csv(input_csv)

    # Remove missing and duplicate values
    data = data.dropna()
    data = data.drop_duplicates()

    # Convert to a standard time format and extract time features(date, hour, and weekday)
    data['start_time'] = pd.to_datetime(data['started_at'])
    data['end_time'] = pd.to_datetime(data['ended_at'])
    data['start_date'] = data['start_time'].dt.date
    data['start_hour'] = data['start_time'].dt.hour
    data['start_weekday'] = data['start_time'].dt.weekday

    # Clean station name
    data['start_station_name'] = data['start_station_name'].str.strip()
    data['end_station_name'] = data['end_station_name'].str.strip()

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

def filter_week_data(input_csv, output_csv, start_date, end_date):
    """Filter one week of data"""
    data = pd.read_csv(input_csv)

    # Convert time fields to datetime format
    data['start_time'] = pd.to_datetime(data['started_at'])
    data['end_time'] = pd.to_datetime(data['ended_at'])

    # Filter for one week of data
    filtered_data = data[(data['start_time'] >= start_date) & (data['start_time'] <= end_date)]

    # Save to a new CSV file
    filtered_data.to_csv(output_csv, index=False)

def main():
    input_csv = '202004-divvy-tripdata.csv'
    weekly_csv = '1week_time_series_data.csv'
    output_gml = '1week_bike_network.gml'

    # Filter one week of data
    filter_week_data(input_csv, weekly_csv, '2020-04-01', '2020-04-07')
    
    # Data cleaning
    data = clean_data(weekly_csv)

    # Build network graph
    build_network(data, output_gml)

if __name__ == "__main__":
    main()
