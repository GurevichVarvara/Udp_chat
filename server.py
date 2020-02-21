import socket
import threading
import queue

HEADER_SIZE = 8
PACKAGE_SIZE = 10

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


def run_server(address, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((address, port))
    print('Server running...')

    received_message_queue = queue.Queue()
    threading.Thread(target=receive_message, args=(server_socket, received_message_queue)).start()

    while True:
        while not received_message_queue.empty():
            address, message = received_message_queue.queue[0][0], received_message_queue.queue[0][1]
            received_message_queue.get()
            print('Message from ' + address + ' is: ' + message)


if __name__ == '__main__':
    UDP_SERVER_IP_ADDRESS = '127.0.0.1'
    UDP_SERVER_PORT = 5000

    run_server(UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT)
