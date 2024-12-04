import pandas as pd
import networkx as nx


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

def filter_week_data(cleaned_data, start_date, end_date):
    """Filter one week of data"""
    # Convert start_date and end_date to datetime for filtering
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data within the given date range
    filtered_data = cleaned_data[
        (cleaned_data['start_time'] >= start_date) & 
        (cleaned_data['start_time'] < end_date)
    ]
    print(f"Filtered data contains {len(filtered_data)} trips from {start_date.date()} to {end_date.date()}.")
    return filtered_data

def main(cleaned_csv='cleaned_bike_data.csv', weekly_csv='1week_data.csv', 
         output_gml='1week_bike_network.gml', start_date='2020-04-01', end_date='2020-04-07'):
    """
    Main function to filter weekly data and build a network graph.
    """
    # Load cleaned data
    cleaned_data = pd.read_csv(cleaned_csv, parse_dates=['start_time', 'end_time'])

    # Filter data for the specified week
    weekly_data = filter_week_data(cleaned_data, start_date, end_date)

    # Save the filtered data for future use
    weekly_data.to_csv(weekly_csv, index=False)
    print(f"Filtered weekly data saved to {weekly_csv}.")

    # Build network graph
    build_network(weekly_data, output_gml)

if __name__ == "__main__":
    main()
