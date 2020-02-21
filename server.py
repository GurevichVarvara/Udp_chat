import socket

UDP_SERVER_IP_ADDRESS = '127.0.0.1'
UDP_SERVER_PORT = 1234

HEADER_SIZE = 8
PACKAGE_SIZE = 10

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_SERVER_IP_ADDRESS, UDP_SERVER_PORT))

print('Server running...')

full_message = ''
is_new_message = True

while True:
    part_of_message, address = server_socket.recvfrom(PACKAGE_SIZE)
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
        print('message from ' + str(address[0]) + str(address[1]) + ': ' + full_message)
        is_new_message = True
        full_message = ''
        server_socket.sendto(bytes('received', 'utf-8'), address)
    else:
        server_socket.sendto(bytes(str(HEADER_SIZE + len(full_message)) + ' ' + str(PACKAGE_SIZE), 'utf-8'),
                             address)
