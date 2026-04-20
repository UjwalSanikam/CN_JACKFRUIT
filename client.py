import socket
import time
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# GLOBAL VARIABLES
SERVER_IP = '10.30.200.207' # Change to your server's IP if using two laptops!
SERVER_PORT = 65432
download_progress = 0
status_message = "Waiting for request..."

# --- NEW: FUNCTION TO FETCH MP3 FILES ---
def get_available_songs():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Set a 2-second timeout so the webpage doesn't freeze if the server is offline
            s.settimeout(2.0) 
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(b"LIST_FILES")
            
            data = s.recv(4096).decode('utf-8')
            if data == "EMPTY" or not data:
                return []
                
            # Split the string back into a Python list
            return data.split("|")
    except Exception as e:
        print(f"Error fetching songs: {e}")
        return []

# --- TCP DOWNLOAD LOGIC ---
def start_tcp_download(song_name):
    global download_progress, status_message
    download_progress = 0
    CHUNK_SIZE = 4096
    OUTPUT_FILENAME = f"downloaded_{song_name}"

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            client_socket.sendall(song_name.encode('utf-8'))
            server_response = client_socket.recv(1024).decode('utf-8')
            
            if server_response == "ERROR":
                status_message = "File not found on server."
                return
            
            if server_response.startswith("FOUND"):
                _, file_size_str = server_response.split("|")
                total_size = int(file_size_str)
                
                status_message = f"Downloading {song_name}..."
                
                with open(OUTPUT_FILENAME, 'wb') as audio_file:
                    chunk_count = 0
                    downloaded_bytes = 0
                    start_time = time.time() 
                    
                    while True:
                        data = client_socket.recv(CHUNK_SIZE)
                        if not data:
                            break
                        audio_file.write(data)
                        
                        chunk_count += 1
                        downloaded_bytes += len(data)
                        
                        download_progress = int((downloaded_bytes / total_size) * 100)
                        print(f"Received chunk {chunk_count}...") 
                        
                        if chunk_count % 10 == 0:
                            elapsed_time = time.time() - start_time
                            if elapsed_time > 0.5:
                                client_socket.sendall(b"LOW_Q")
                            else:
                                client_socket.sendall(b"HIGH_Q")
                            start_time = time.time()
                            
                status_message = "Download Complete!"
                download_progress = 100
                print(f"\nStream complete. Saved as '{OUTPUT_FILENAME}'.")
    except Exception as e:
        status_message = f"Connection failed."
        print(status_message)

# --- FLASK WEB ROUTES ---

@app.route('/')
def index():
    # Fetch the live list of songs before loading the page!
    live_songs = get_available_songs()
    # Pass the list to the HTML file
    return render_template('index.html', songs=live_songs)

@app.route('/download', methods=['POST'])
def trigger_download():
    song_name = request.json.get('song_name')
    thread = threading.Thread(target=start_tcp_download, args=(song_name,))
    thread.start()
    return jsonify({"status": "Started"})

@app.route('/progress')
def get_progress():
    return jsonify({"progress": download_progress, "message": status_message})

if __name__ == '__main__':
    print("Starting Local Web Client UI...")
    app.run(port=5000, debug=False)