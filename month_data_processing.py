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

    # time series analysis data
    time_series_data = data[['start_station_name', 'end_station_name', 'start_time', 'end_time']]
    time_series_data.to_csv('month_time_series_data.csv', index=False)
    print("Time series data saved to time_series_data.csv")

    # Create the network graph 
    build_network(data, output_gml)
    print("Network building completed")

if __name__ == "__main__":
    main()

