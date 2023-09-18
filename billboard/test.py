import socket
import json

# Server configuration
server_ip = '10.42.100.100'  # Replace with the actual server's IP address
server_port = 1010  # Choose the same port as in the server script

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
client_socket.connect((server_ip, server_port))

print("Connected to {}:{}".format(server_ip, server_port))

# Load team name and time from another source (e.g., another database)
game_type = "team"
group_type = "black"
team_name = "manggogas"  # Replace with your actual team name
time = "00:5:253"  # Replace with your actual time

# Create a dictionary to hold the data
data_to_send = {
    "GameType": game_type,
    "Group": group_type,
    "TeamName": team_name,
    "Time": time
}

# Serialize data to JSON
json_data = json.dumps(data_to_send)

# Send JSON data to the server
client_socket.send(json_data.encode('utf-8'))

# Close the client socket
client_socket.close()