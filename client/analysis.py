# metrics.py
import os

METRIC = False

def calculate_file_size(file_path):
    return os.path.getsize(file_path) * 8

def calculate_duration(start_time, end_time):
    return end_time - start_time

def calculate_speed(file_size_bits, duration_seconds):
    if duration_seconds > 0:
        return file_size_bits / (duration_seconds * (10**6))
    return 0

def log_download_metircs(send_request_time, got_request_time, finished_download_time, initial_download_time, file_path):
    file_size = calculate_file_size(file_path)
    duration = calculate_duration(initial_download_time, finished_download_time)
    speed = calculate_speed(file_size, duration)
    print(f"Server Response Time: {(got_request_time - send_request_time) * (10**3):.6f} ms")
    print(f"File Download Time: {duration * (10**3):.6f} ms")
    print(f"Download Speed: {speed:.4f} Mbps\n")

def log_upload_metircs(send_request_time, got_request_time, finished_upload_time, initial_upload_time, file_path):
    file_size = calculate_file_size(file_path)
    duration = calculate_duration(initial_upload_time, finished_upload_time)
    speed = calculate_speed(file_size, duration)
    print(f"Server Response Time: {(got_request_time - send_request_time) * (10**3):.6f} ms")
    print(f"File Upload Time: {duration * (10**3):.6f} ms")
    print(f"Upload Speed: {speed:.4f} Mbps\n")
