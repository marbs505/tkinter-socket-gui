import tkinter as tk
from tkinter import scrolledtext
import socket
import threading
import asyncio
from tkinter import ttk

class SocketGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("boring asf")
        
        window_width = 500
        window_height = 500
        
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        position_x = (screen_width // 2) - (window_width // 2)
        position_y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")
        self.root.configure(bg="#2c3e50")
        
        self.server_thread = None
        self.server_socket = None
        self.client_socket = None
        
        style = ttk.Style()
        style.configure("TButton", font=("Arial", 12), padding=5)
        style.configure("TLabel", font=("Arial", 12), background="#2c3e50", foreground="white")
        style.configure("TEntry", font=("Arial", 12))
        
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        self.server_label = ttk.Label(self.main_frame, text="Server Console")
        self.server_label.pack(pady=5, fill=tk.X)
        
        self.server_log = scrolledtext.ScrolledText(self.main_frame, height=5, bg="#34495e", fg="white", font=("Arial", 10))
        self.server_log.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.start_server_button = ttk.Button(self.main_frame, text="Start Server", command=self.start_server)
        self.start_server_button.pack(pady=5, fill=tk.X)
        
        self.client_label = ttk.Label(self.main_frame, text="Client Console")
        self.client_label.pack(pady=5, fill=tk.X)
        
        self.client_log = scrolledtext.ScrolledText(self.main_frame, height=5, bg="#34495e", fg="white", font=("Arial", 10))
        self.client_log.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.message_entry = ttk.Entry(self.main_frame)
        self.message_entry.pack(pady=5, fill=tk.X)
        
        self.send_button = ttk.Button(self.main_frame, text="Send Message", command=self.send_message)
        self.send_button.pack(pady=5, fill=tk.X)
        
        self.connect_client_button = ttk.Button(self.main_frame, text="Connect Client", command=self.connect_client)
        self.connect_client_button.pack(pady=5, fill=tk.X)
        
    def start_server(self):
        try:
            self.server_thread = threading.Thread(target=asyncio.run, args=(self.run_server(),), daemon=True)
            self.server_thread.start()
            self.server_log.insert(tk.END, "Server started on port 12345...\n")
        except Exception as e:
            self.server_log.insert(tk.END, f"Error starting server: {e}\n")

    async def run_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(("0.0.0.0", 12345))
            self.server_socket.listen(5)
            self.server_socket.setblocking(False)
            
            loop = asyncio.get_event_loop()
            while True:
                client_socket, addr = await loop.sock_accept(self.server_socket)
                self.server_log.insert(tk.END, f"Connection from {addr}\n")
                loop.create_task(self.handle_client(client_socket))
        except Exception as e:
            self.server_log.insert(tk.END, f"Server error: {e}\n")
    
    async def handle_client(self, client_socket):
        try:
            loop = asyncio.get_event_loop()
            data = await loop.sock_recv(client_socket, 1024)
            self.server_log.insert(tk.END, f"Received: {data.decode()}\n")
            await loop.sock_sendall(client_socket, b"Message received by server")
            client_socket.close()
        except Exception as e:
            self.server_log.insert(tk.END, f"Error handling client: {e}\n")

    def connect_client(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("127.0.0.1", 12345))
            self.client_log.insert(tk.END, "Connected to server\n")
        except Exception as e:
            self.client_log.insert(tk.END, f"Error connecting to server: {e}\n")
    
    def send_message(self):
        try:
            message = self.message_entry.get()
            if self.client_socket and message:
                self.client_socket.send(message.encode())
                data = self.client_socket.recv(1024).decode()
                self.client_log.insert(tk.END, f"Server: {data}\n")
        except Exception as e:
            self.client_log.insert(tk.END, f"Error sending message: {e}\n")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SocketGUI(root)
    root.mainloop()
