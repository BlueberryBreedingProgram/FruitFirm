import os
import csv
import numpy as np
import datetime
import requests
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from collections import deque

def send_data_to_firebase(url, node_name, data):
    json_data = json.dumps(data)
    full_url = f"{url}/{node_name}.json"
    response = requests.patch(full_url, data=json_data)
    if response.status_code == 200:
        print("Data sent successfully")
    else:
        print(f"Failed to send data: {response.text}")

def process_dat_file(file_path):
    firmness_values = []
    diameter_values = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            firmness_values.append(float(row[1]))
            diameter_values.append(float(row[2]))
    avg_firmness = round(np.mean(firmness_values), 3)
    avg_diameter = round(np.mean(diameter_values), 3)
    std_firmness = round(np.std(firmness_values), 3)
    std_diameter = round(np.std(diameter_values), 3)
    return {
        "avgFirmness": str(avg_firmness),
        "avgDiameter": str(avg_diameter),
        "sdFirmness": str(std_firmness),
        "sdDiameter": str(std_diameter),
    }

class FileWatcher(FileSystemEventHandler):
    def __init__(self, directory, url):
        self.directory = directory
        self.url = url
        self.processed_files = set()
        self.file_queue = deque()
        self.file_last_modified = {}

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith(".dat"):
            self.file_queue.append(event.src_path)
            self.file_last_modified[event.src_path] = os.path.getmtime(event.src_path)

    def process_files(self):
        while self.file_queue:
            file_path = self.file_queue.popleft()
            if time.time() - self.file_last_modified[file_path] < 10:
                self.file_queue.append(file_path)
                continue

            if file_path not in self.processed_files:
                self.process_file(file_path)
                self.processed_files.add(file_path)

    def process_file(self, file_path):
        data = process_dat_file(file_path)
        dummy_code = os.path.basename(file_path).split(".")[0]
        current_year = datetime.datetime.now().year
        ref_path = f"fruit_quality_{current_year}/{dummy_code}"

        check_url = f"{self.url}/{ref_path}.json"
        response = requests.get(check_url)
        json_response = response.json()

        default_values = {
            'dummyCode': dummy_code,
            'dateAndTime': datetime.datetime.now().isoformat(),
            'genotype': "Not Yet Imported",
            'Brix': "",
            'Juice Mass': "",
            'TTA': "",
            'bush': "",
            'mass': "",
            'ml Added': "",
            'notes': "",
            'numOfBerries': "",
            'project': "",
            'ph': "",
            'site': "",
            'stage': "",
            'postHarvest': "",
            'week': "100",
            'xBerryMass': ""
        }

        for field, default_value in default_values.items():
            if json_response is None or field not in json_response or json_response[field] == "":
                data[field] = default_value

        send_data_to_firebase(self.url, ref_path, data)
        self.processed_files.add(file_path)

if __name__ == "__main__":
    # ****************** PATH TO UPDATE WITH CORRECT RASPBERRT PI USB DIR **********
    #TARGET_DIRECTORY = os.path.expanduser("/media/pi/usb/")
    TARGET_DIRECTORY = os.path.expanduser("/Users/savaglisic/Desktop/datafiles")
    # ****************** PATH TO UPDATE WITH CORRECT RASPBERRT PI USB DIR **********

    firebase_url = "https://berrymaster-c0093-default-rtdb.firebaseio.com"

    event_handler = FileWatcher(TARGET_DIRECTORY, firebase_url)
    observer = Observer()
    observer.schedule(event_handler, path=TARGET_DIRECTORY, recursive=False)
    observer.start()

    try:
        while True:
            event_handler.process_files()
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
