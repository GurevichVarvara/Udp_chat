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


def receive_message(socket, received_message_queue):
    full_message = ''
    is_new_message = True

    while True:
        part_of_message, address = socket.recvfrom(PACKAGE_SIZE)
        part_of_message = part_of_message.decode('utf-8')

        # continue receiving message
        if not is_new_message:
            full_message += part_of_message

        # start receiving message
        else:
            message_len = int(part_of_message[:HEADER_SIZE])
            is_new_message = False
            full_message += part_of_message[HEADER_SIZE:]

        # send to client current receiving status
        if len(full_message) == message_len:
            socket.sendto(bytes('sent', 'utf-8'), address)

            # add data from client to queue
            received_message_queue.put((str(address[0]) + ' ' + str(address[1]), full_message))

            is_new_message = True
            full_message = ''
        else:
            socket.sendto(bytes(str(HEADER_SIZE + len(full_message)) + ' ' + str(PACKAGE_SIZE), 'utf-8'), address)


def run_client(server_address):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_socket.connect(server_address)

	while True:
		data = input()

		if data == '':
			continue

		send_message(client_socket, data)



if __name__ == '__main__':
	UDP_SERVER_IP_ADDRESS = '127.0.0.1'
	UDP_SERVER_PORT = 5000
	SERVER_ADDRESS = (UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
	UDP_CLIENT_IP_ADDRESS = '127.0.0.1'

	run_client(SERVER_ADDRESS)


