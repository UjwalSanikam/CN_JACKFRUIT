import socket
import threading
import select  
import time    
import os      

HOST = '0.0.0.0' # Keep this as 0.0.0.0 for LAN testing
PORT = 65432
CHUNK_SIZE = 4096

def handle_client(conn, addr):
    print(f"\n[NEW CONNECTION] Client {addr} connected.")
    current_quality = "HIGH"
    
    try:
        # 1. READ THE COMMAND
        requested_data = conn.recv(1024).decode('utf-8').strip()
        
        # --- NEW: DIRECTORY LISTING LOGIC ---
        if requested_data == "LIST_FILES":
            print(f"[{addr}] Requested directory listing.")
            # Scan the current folder for any files ending in .mp3
            mp3_files = [f for f in os.listdir() if f.endswith('.mp3')]
            
            # Join the list into a single string separated by the pipe symbol '|'
            file_string = "|".join(mp3_files)
            
            # If there are no mp3 files, send a fallback message
            if not file_string:
                file_string = "EMPTY"
                
            conn.sendall(file_string.encode('utf-8'))
            return # Close connection after sending the list
        # -----------------------------------
        
        # 2. THE HANDSHAKE (If they asked for a specific file, not a list)
        print(f"[{addr}] Requested file: {requested_data}")
        
        if not os.path.exists(requested_data):
            print(f"[{addr}] ERROR: {requested_data} not found. Closing connection.")
            conn.sendall(b"ERROR") 
            return 
            
        file_size = os.path.getsize(requested_data)
        conn.sendall(f"FOUND|{file_size}".encode('utf-8'))
        time.sleep(0.1) 
        
        # 3. STREAMING
        with open(requested_data, 'rb') as audio_file:
            while True:
                ready_to_read, _, _ = select.select([conn], [], [], 0.0)
                
                if ready_to_read:
                    qos_report = conn.recv(1024).decode('utf-8')
                    if "LOW_Q" in qos_report and current_quality != "LOW":
                        print(f"[{addr}] QoS ALERT: Adapting to LOW quality...")
                        current_quality = "LOW"
                    elif "HIGH_Q" in qos_report and current_quality != "HIGH":
                        print(f"[{addr}] QoS RECOVERY: Returning to HIGH quality...")
                        current_quality = "HIGH"

                audio_chunk = audio_file.read(CHUNK_SIZE)
                if not audio_chunk:
                    break
                conn.sendall(audio_chunk)
                time.sleep(0.1)
                
        print(f"\n[FINISHED] Done streaming {requested_data} to {addr}.")
    except Exception as e:
        print(f"\n[ERROR] Connection lost: {e}")
    finally:
        conn.close()

# MAIN SERVER LOGIC
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"[LISTENING] Server is listening on port {PORT}...")
    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()