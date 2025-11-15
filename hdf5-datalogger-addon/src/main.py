import datetime
import time

def main():
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("HDF5 DataLogger: Hello World")
    print(f"Start time: {start_time}", flush=True)

    # Keep the container alive
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
