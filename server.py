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
    			socket.send(bytes(message_to_send[int(current_index_of_message):], 'utf-8'))


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
        	received_message_queue.put((address, full_message))
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

    user_addresses = set()
    names = set()
    user_names = {}
    private_chats = {}

    while True:
        while not received_message_queue.empty():
            address, message = received_message_queue.queue[0][0], received_message_queue.queue[0][1]
            received_message_queue.get()

            address_str = str(address[0]) + ':' + str(address[1])
            print('Message from ' + address_str + ': ' + message)
            
            if address_str not in user_addresses:
                user_addresses.add(address_str)
                
                if message not in names:
                    names.add(message)
                    send_message(server_socket, 'valid', receiving_status_message_queue, address)
                else:
                    send_message(server_socket, 'not valid', receiving_status_message_queue, address)


if __name__ == '__main__':
    UDP_SERVER_IP_ADDRESS = '192.168.1.57'
    UDP_SERVER_PORT = 5001

    run_server(UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
