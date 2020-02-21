import socket

HEADER_SIZE = 8
PACKAGE_SIZE = 10


def send_message(socket, message):
	message_to_received = f'{len(message):<{HEADER_SIZE}}' + message
	print(message)

	socket.send(bytes(message_to_received, 'utf-8'))
	is_received = False

	while not is_received:
		ans_from_server, address = socket.recvfrom(1024)
		ans_from_server = ans_from_server.decode('utf-8')
		if address == SERVER_ADDRESS:
			if ans_from_server == 'sent':
				print('sent')
				break
			else:
				current_index_of_message, package_size = ans_from_server.split()[0], ans_from_server.split()[1]
				socket.send(bytes(message_to_received[int(current_index_of_message):], 'utf-8'))


def run_client(client_address, server_address):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_socket.connect(SERVER_ADDRESS)

	send_message(client_socket, 'Test message. Hello my name is Varvara Im doing this')


if __name__ == '__main__':
	UDP_SERVER_IP_ADDRESS = '127.0.0.1'
	UDP_SERVER_PORT = 5000
	SERVER_ADDRESS = (UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
	UDP_CLIENT_IP_ADDRESS = '127.0.0.1'

	run_client(UDP_CLIENT_IP_ADDRESS, SERVER_ADDRESS)


