import socket
import json

# Server configuration
server_ip = '192.168.0.168'  # Replace with the actual server's IP address
server_port = 12345  # Choose an available port

# Create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the server address and port
server_socket.bind((server_ip, server_port))

# Listen for incoming connections
server_socket.listen(5)  # Accept up to 5 connections in the queue

print("Listening on {}:{}".format(server_ip, server_port))

def read_data_from_file(file_path):
    data = []
    try:
        with open(file_path, 'r') as file:
            lines = file.read().splitlines()
            team_name = ""
            time = ""
            for line in lines:
                if line.startswith("Team Name:"):
                    team_name = line.split(': ')[1]
                elif line.startswith("Time:"):
                    time = line.split(': ')[1]
                    data.append((team_name, time))
    except IOError:
        print("File 'siege_team_data.txt' not found.")
    return data

def time_to_milliseconds(time_str):
    minutes, seconds, milliseconds = map(int, time_str.split(":"))
    return minutes * 60 * 1000 + seconds * 1000 + milliseconds

def display_rankings(data):
    sorted_data = sorted(data, key=lambda x: time_to_milliseconds(x[1]))  # Sort data by time
    print("Rankings:")
    for rank, (team_name, time) in enumerate(sorted_data, start=1):
        print("{} Team: {}, Time: {}".format(rank, team_name, time))

data_from_file = read_data_from_file('siege_team_data.txt')
if data_from_file:
    display_rankings(data_from_file)

while True:
    # Accept a connection
    client_socket, client_address = server_socket.accept()
    print("Connected to", client_address)

    # Receive and process data
    received_data = client_socket.recv(1024).decode('utf-8')
    
    # Parse received JSON data
    try:
        data = json.loads(received_data)
        team_name = data.get("TeamName", "")
        time = data.get("Time", "")
        
        print("Data received:")
        print("Team Name:", team_name)
        print("Time:", time)
        
        # Close the client socket
        client_socket.close()

        # Append the received data to the text file
        with open('data.txt', 'a') as file:
            file.write("Team Name: {}\nTime: {}\n\n".format(team_name, time))

        # Read data from text file and display rankings
        data_from_file = read_data_from_file('siege_team_data.txt')
        display_rankings(data_from_file)

    except ValueError:
        print("Failed to decode JSON data")

# Close the server socket
server_socket.close()
