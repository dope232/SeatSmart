import socket
import threading
import json
import ssl


HOST = '192.168.92.200'
PORT = 9999
CERT_FILE = 'server.crt'
KEY_FILE = 'server.key'


classes_info = {
    'AFLL': {'teacher': 'Mr. Sharma', 'timing': '10:00 AM', 'seats': 60},
    'OS': {'teacher': 'Ms. Preet', 'timing': '12:00 PM', 'seats': 65},
    'CN': {'teacher': 'Dr. Ganesh', 'timing': '2:00 PM', 'seats': 60},
    'DAA': {'teacher': 'Dr. Prasad', 'timing': '4:00 PM', 'seats': 60}
    
}

user_bookings = {}

def display_classes(classes_info):
    print("Classes:")
    for class_name, details in classes_info.items():
        print(f"\nClass: {class_name}")
        print(f"Teacher: {details['teacher']}")
        print(f"Timing: {details['timing']}")
        print(f"Available seats: {details['seats']}")


def handle_client(conn, addr):
    print(f"Connected by {addr}")
    conn = ssl.wrap_socket(conn, keyfile=KEY_FILE, certfile=CERT_FILE, server_side=True)

    while True:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            print(f"Disconnected from {addr}")
            break

        if data == 'get_classes':
            conn.send(json.dumps(classes_info).encode('utf-8'))
        elif data.startswith('book_class'):
            _, class_name, num_seats_str = data.split()
            num_seats = int(num_seats_str)
            if class_name in classes_info and classes_info[class_name]['seats'] >= num_seats:
                if class_name not in user_bookings:
                    user_bookings[class_name] = {}
                if addr not in user_bookings[class_name]:
                    user_bookings[class_name][addr] = 0
                if user_bookings[class_name][addr] + num_seats <= 3:
                    classes_info[class_name]['seats'] -= num_seats
                    user_bookings[class_name][addr] += num_seats
                    conn.send("Booking successful".encode('utf-8'))
                else:
                    conn.send("Booking failed. Maximum 3 seats allowed per user for this class".encode('utf-8'))
            else:
                conn.send("Booking failed. Not enough seats available".encode('utf-8'))
        elif data.startswith('cancel_booking'):
            _, class_name, num_seats_str = data.split()
            num_seats = int(num_seats_str)
            if class_name in classes_info and addr in user_bookings[class_name]:
                if user_bookings[class_name][addr] >= num_seats:
                    classes_info[class_name]['seats'] += num_seats
                    user_bookings[class_name][addr] -= num_seats
                    conn.send("Booking cancelled successfully".encode('utf-8'))
                else:
                    conn.send("Cancellation failed. You have not booked this many seats".encode('utf-8'))
            else:
                conn.send("Class not found or no booking found".encode('utf-8'))

    conn.close()


def main():
    #  SSL 
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
    except KeyboardInterrupt:
        print("Server shutting down...")
        server.close()

if __name__ == "__main__":
    main()
