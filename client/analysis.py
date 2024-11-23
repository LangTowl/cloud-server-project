import os

# Desc: calcaulte file size times 8 to bytes
# Auth: Lukas Kelk
# Date: 11/21/2024
def calculate_file_size(file_path):
    return os.path.getsize(file_path) * 8

# Desc: calculate duration using delta
# Auth: Lukas Kelk
# Date: 11/21/2024
def calculate_duration(start_time, end_time):
    return end_time - start_time

# Desc: calculate speed
# Auth: Lukas Kelk
# Date: 11/21/2024
def calculate_speed(file_size_bits, duration_seconds):
    if duration_seconds > 0:
        return file_size_bits / (duration_seconds * (10**6))
    return 0

# Desc: logging download metrics, needed dif function for string
# Auth: Lukas Kelk
# Date: 11/21/2024
def log_download_metircs(send_request_time, got_request_time, finished_download_time, initial_download_time, file_path):
    file_size = calculate_file_size(file_path)
    duration = calculate_duration(initial_download_time, finished_download_time)
    speed = calculate_speed(file_size, duration)
    print(f"Server Response Time: {(got_request_time - send_request_time) * (10**3):.6f} ms")
    print(f"File Download Time: {duration * (10**3):.6f} ms")
    print(f"Download Speed: {speed:.4f} Mbps\n")

# Desc: logging upload metrics, needed dif function for string
# Auth: Lukas Kelk
# Date: 11/21/2024
def log_upload_metircs(send_request_time, got_request_time, finished_upload_time, initial_upload_time, file_path):
    file_size = calculate_file_size(file_path)
    duration = calculate_duration(initial_upload_time, finished_upload_time)
    speed = calculate_speed(file_size, duration)
    print(f"Server Response Time: {(got_request_time - send_request_time) * (10**3):.6f} ms")
    print(f"File Upload Time: {duration * (10**3):.6f} ms")
    print(f"Upload Speed: {speed:.4f} Mbps\n")

# Desc: set toggles metric flag on and off
# Auth: Lukas Kelk
# Date: 11/16/24
def set_METRIC(METRIC):
    if(METRIC):
        print("\nThe Client will no longer give performance metrics\n")
        return False
    else:
        print("\nThe Client will now give performance metrics\n")
        return True