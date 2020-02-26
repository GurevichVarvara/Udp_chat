import socket
import threading
import queue

HEADER_SIZE = 8
PACKAGE_SIZE = 30


def send_message(socket, message, receiving_status_message_queue, address):
	message_to_send = f'{len(message):<{HEADER_SIZE}}' + message

	socket.sendto(bytes(message_to_send, 'utf-8'), address)

	while True:
		if not receiving_status_message_queue.empty():
			message = receiving_status_message_queue.get()

			if message == 'sent':
				return True
			else:
				current_index_of_message = message
				socket.sendto(bytes(message_to_send[int(current_index_of_message):], 'utf-8'), address)


def receive_message(socket, received_message_queue, receiving_status_message_queue):
	full_message = ''
	is_new_message = True

	while True:
		part_of_message, address = socket.recvfrom(PACKAGE_SIZE)
		part_of_message = part_of_message.decode('utf-8')

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
			socket.sendto(bytes(' ' * HEADER_SIZE + 'sent', 'utf-8'), address)

			# add data from client to queue
			received_message_queue.put((address, full_message[HEADER_SIZE:]))
			is_new_message = True
			full_message = ''
		else:
			socket.sendto(bytes(' ' * HEADER_SIZE + str(len(full_message)), 'utf-8'), address)


def run_server(address, port):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	server_socket.bind((address, port))
	print('Server running...')

	received_message_queue = queue.Queue()
	receiving_status_message_queue = queue.Queue()
	threading.Thread(target=receive_message, args=(server_socket, received_message_queue, receiving_status_message_queue)).start()

	user_addresses = {}
	user_names = {}

	private_chats = {}
	rooms = {}
	user_chat = {}

	while True:
		while not received_message_queue.empty():
			message_from_queue = received_message_queue.get()
			address, message = message_from_queue[0], message_from_queue[1]
			address_str = str(address[0]) + ':' + str(address[1])

			print('\nMessage from ' + address_str + ': ' + message)

			# if new user
			if address not in user_addresses.values():
				if message not in user_addresses.keys():
					user_addresses.update({message: address})
					user_names.update({address_str: message})
					send_message(server_socket, 'valid', receiving_status_message_queue, address)

					print('user names:', user_addresses)
					print('user addresses:', user_names)
				else:
					send_message(server_socket, 'not valid', receiving_status_message_queue, address)

			# if existing user is not in any chats
			elif address_str not in user_chat.keys() and user_names[address_str] not in private_chats.keys():

				try:
					chat_type, chat_name = int(message.split(':')[0]), message.split(':')[1]

					if chat_type == 1:
						if chat_name not in rooms.keys():
							rooms[chat_name] = []

						rooms[chat_name].append(address)
						user_chat[user_names[address_str]] = chat_name
						send_message(server_socket, 'You are in the chat room ' + chat_name + '!', receiving_status_message_queue, address)

						print('rooms:', rooms)
						print('user_chats:', user_chat)

					elif chat_type == 2:

						# if user client like to chat with exists and he's not in any room and nobody
						if chat_name in user_names.values() and chat_name not in user_chat.keys():
							print('User client like to chat with exists and not in any room')
							private_chats[user_names[address_str]] = chat_name

							# if this user waits for this client's connection
							if chat_name in private_chats.keys() and private_chats[chat_name] == user_names[address_str]:
								print('User client like to chat with waits for client connection')
								send_message(server_socket, 'You are in the private chat with ' + chat_name, receiving_status_message_queue, address)
								send_message(server_socket, 'You are in the private chat with ' + user_names[address_str], receiving_status_message_queue, user_addresses[chat_name])

								# delete all clients's connections who was waiting for this user
								for name in private_chats.keys():
									if private_chats[name] == user_names[address_str] and name != chat_name:
										print('Delete connectoin ' + name)
										del private_chats[name]
										send_message(server_socket, 'not valid', receiving_status_message_queue, user_addresses[name])

							# if this user waits for another client's connection
							elif chat_name in private_chats.keys() and private_chats[chat_name] != user_names[address_str]:
								print('User client like to chat with waits for another client connection')
								raise Exception

							# if this user doesn't wait for client's connection
							else:
								print('User client like to chat with doesnt wait for any client connection')
								send_message(server_socket, 'You are waiting for another side connection', receiving_status_message_queue, address)

							print('private chats:', private_chats)
						else:
							raise Exception

					else:
						raise Exception


				except Exception as e:
					send_message(server_socket, 'not valid', receiving_status_message_queue, address)



if __name__ == '__main__':
	UDP_SERVER_IP_ADDRESS = '192.168.1.57'
	UDP_SERVER_PORT = 5001

	run_server(UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
