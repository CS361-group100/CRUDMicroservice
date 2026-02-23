# test
import json
import time
from pathlib import Path


class CRUDService:
    def __init__(self, file="data.json"):
        self.file = file

    def create_resource(self):
        """
        TODO: Implement create method
        """
        print("Creating resource")  # DELETE ME

    def update_resource(self):
        """
        TODO: Implement update method
        """
        print("Updating resource")  # DELETE ME
        pass

    def delete_resource(self):
        """
        TODO: Implement delete method
        """
        print("Deleting resource")  # DELETE ME
        pass


def monitor_requests(router_fn):
    """
    Monitors the 'requests' directory for new request files.
    Takes a router function as a parameter to dictate what is done with the new file's
    contents.
    """
    main_dir = Path(__file__).resolve().parent  # path to main directory (contains script)
    request_dir = main_dir / "requests"  # path to requests directory (requests txt files ONLY)
    # create requests directory if it doesn't already exist
    request_dir.mkdir(exist_ok=True)
    checked_files = set()  # store processed files

    print("Checking requests directory..")

    # parsing files
    while True:
        for filepath in request_dir.glob("*.json"):
            if filepath.name in checked_files:
                continue  # skip files that have already been checked

            # for files that haven't yet been read:
            try:
                # read and pull data from text file
                with open(filepath, "r") as file:
                    data = json.load(file)

                route_request(data)  # decide which CRUD method to call for the data
                checked_files.add(filepath.name)  # add file to checked set to avoid re-reading

            # for issues w the text file's formatting/ parsing failed
            except json.JSONDecodeError:
                checked_files.add(filepath.name)  # add file to checked set to avoid re-reading
                print(f"Invalid JSON in {filepath.name}.")

            # to deal w any other issues that come up
            except Exception as error:
                checked_files.add(filepath.name)  # add file to checked set to avoid re-reading
                print(f"Error processing {filepath.name} : {error}")

        time.sleep(1)


def route_request(data_requested):
    """
    Takes data from a request file, parses for the requested operation,
    and reroutes to the appropriate method.
    """
    # pull 'operation' from text request
    operation = data_requested["operation"]

    # route to the appropriate CRUD Service
    if operation == "create":
        CRUDService.create_resource(data_requested)
    if operation == "update":
        CRUDService.update_resource(data_requested)
    if operation == "delete":
        CRUDService.delete_resource(data_requested)


def parse_request():
    """
    TODO: Implement to parse request files
    (may not need idk)
    """
    pass


def response():
    """
    TODO: Implement to generate response
    """
    pass


def main():
    while True:
        monitor_requests(route_request)


if __name__ == "__main__":
    main()
