import socket
import threading
import queue

HEADER_SIZE = 8
PACKAGE_SIZE = 30

def send_message(socket, message, receiving_status_message_queue):
	message_to_send = f'{len(message):<{HEADER_SIZE}}' + message
	socket.send(bytes(message_to_send, 'utf-8'))

	while True:
		if not receiving_status_message_queue.empty():
			message = receiving_status_message_queue.get()

			if message == 'sent':
				return True
			else:
				current_index_of_message = message
				socket.send(bytes(message_to_send[int(current_index_of_message):], 'utf-8'))


def receive_message(socket, received_message_queue, receiving_status_message_queue, server_address):
	full_message = ''
	is_new_message = True

	while True:
		part_of_message, address = socket.recvfrom(PACKAGE_SIZE)
		part_of_message = part_of_message.decode('utf-8')

		# if sender is not server or message is showing receiving status
		if address != server_address:
			continue

		# if receiving status message is received
		if part_of_message[:HEADER_SIZE] == ' ' * HEADER_SIZE:
			receiving_status_message_queue.put(part_of_message[HEADER_SIZE:])
			continue

		# continue receiving message
		if not is_new_message:
			full_message += part_of_message

		# start receiving message
		else:
			message_len = int(part_of_message[:HEADER_SIZE])
			is_new_message = False
			full_message += part_of_message

		# send to client current receiving status
		if len(full_message[HEADER_SIZE:]) == message_len:
			socket.send(bytes(' ' * HEADER_SIZE + 'sent', 'utf-8'))

			# add data from client to queue
			received_message_queue.put(full_message[HEADER_SIZE:])

			is_new_message = True
			full_message = ''
		else:
			socket.send(bytes(' ' * HEADER_SIZE + str(len(full_message)), 'utf-8'))


def run_client(server_address):
	client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	client_socket.connect(server_address)

	received_message_queue = queue.Queue()
	receiving_status_message_queue = queue.Queue()
	threading.Thread(target=receive_message, args=(client_socket, received_message_queue, receiving_status_message_queue, server_address)).start()

	name = input('Please type your name: ')
	send_message(client_socket, name, receiving_status_message_queue)

	# get the answer from server is typed name valid
	while True:
		if not received_message_queue.empty():
			message = received_message_queue.get()
			if message == 'valid':
				is_name_valid = True
				break
			elif message == 'not valid':
				print('This name already exists.')
				name = input('Please type your name: ')

	print('Hello, ' + name + '!')


if __name__ == '__main__':
	UDP_SERVER_IP_ADDRESS = '192.168.1.57'
	UDP_SERVER_PORT = 5001
	SERVER_ADDRESS = (UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
	UDP_CLIENT_IP_ADDRESS = '127.0.0.1'

	run_client(SERVER_ADDRESS)


