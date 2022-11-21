import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 1024  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
	sock.bind((HOST,PORT))
	print(f"Server running...")
	sock.listen()
	conn, addr = sock.accept()
	with conn:
		print("Connection established")
		while True:
			data = conn.recv(10**8)
			if not data: 
				break
			conn.sendall(data)


