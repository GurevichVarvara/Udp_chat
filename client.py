import socket

UDP_CLIENT_ADDRESS = '127.0.0.1'
UDP_SERVER_IP_ADDRESS = '127.0.0.1'
UDP_SERVER_PORT = 5000
SERVER_ADDRESS = (UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)

HEADER_SIZE = 8

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client_socket.connect(SERVER_ADDRESS)

message = 'Test message. Hello my name is Varvara Im doing this'
message_to_received = f'{len(message):<{HEADER_SIZE}}' + message
print(message)

client_socket.send(bytes(message_to_received, 'utf-8'))
is_received = False

while not is_received:
	ans_from_server, address = client_socket.recvfrom(1024)
	ans_from_server = ans_from_server.decode('utf-8')
	if address == SERVER_ADDRESS:
		if ans_from_server == 'sent':
			print('sent')
			received = True
			break
		else:
			current_index_of_message, package_size = ans_from_server.split()[0], ans_from_server.split()[1]
			client_socket.send(bytes(message_to_received[int(current_index_of_message):], 'utf-8'))
