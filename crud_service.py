import json
import time
from pathlib import Path
import uuid


class CRUDService:
    def __init__(self, file_contents, filename="data.json"):
        self.file_contents = file_contents
        self.request_id = self.file_contents.get("request_id")
        self.user_id = self.file_contents.get("user_id")
        self.resource_type = self.file_contents.get("resource_type")
        self.resource_data = self.file_contents.get("resource_data")
        self.resource_id = self.file_contents.get("resource_id")
        if not self.resource_id:
            self.resource_id = str(uuid.uuid4())

        # setting up path to data directory
        main_dir = Path(__file__).resolve().parent  # path to main directory (contains script)
        data_dir = main_dir / "data"  # path to data directory (data txt files ONLY)
        data_dir.mkdir(exist_ok=True)  # create directory if non-existant

        # path to the json file
        self.file_path = data_dir / filename

        # open existing file or create one w an empty list
        if self.file_path.exists():
            with open(self.file_path, "r") as file:
                self.data_held = json.load(file)  # save data already inside file
        else:  # if file doesn't already exist, create and add empty list
            self.data_held = []
            with open(self.file_path, "w") as file:
                json.dump(self.data_held, file, indent=3)

    def create_resource(self):
        """
        TODO: Implement create method
        """
        try:
            new_resource = {
                "resource_id": self.resource_id,
                "user_id": self.user_id,
                "resource_type": self.resource_type,
                "is_deleted": False,
                "resource_data": self.resource_data
            }

            self.data_held.append(new_resource)

            with open(self.file_path, "w") as file:
                json.dump(self.data_held, file, indent=3)

            response_info = {
                "request_id": self.request_id,
                "status": "success",
                "message": "Resource created successfully",
                "code": 201,
                "data": new_resource,
            }

            response(response_info)

        except:
            error_response = {
                "request_id": "NULL",
                "status": "fail",
                "message": f"Error creating resource",
                "code": 500,
                "data": None
            }

            response(error_response)

    def update_resource(self):
        """
        TODO: Implement update method
        """
        try:
            resource = None
            for r in self.data_held:
                if r["resource_id"] == self.resource_id:
                    resource = r
                    break

            # resource not found
            if not resource:
                response_info = {
                    "request_id": self.request_id,
                    "status": "fail",
                    "message": "resource not found",
                    "code": 404,
                    "data": None
                }
                response(response_info)
                return

            # updating data file
            resource["resource_data"] = self.resource_data

            with open(self.file_path, "w") as file:
                json.dump(self.data_held, file, indent=3)

            response_info = {
                "request_id": self.request_id,
                "status": "success",
                "message": "resource updated",
                "code": 200,
                "data": resource
            }
            response(response_info)

        except:
            error_response = {
                "request_id": self.request_id,
                "status": "fail",
                "message": "error updating resource",
                "code": 500,
                "data": None
            }
            response(error_response)

    def delete_resource(self):
        """
        TODO: Implement delete method
        """
        try:
            resource = None
            for r in self.data_held:
                if r["resource_id"] == self.resource_id:
                    resource = r
                    break

            if not resource:
                response_info = {
                    "request_id": self.request_id,
                    "status": "fail",
                    "message": "resource not found",
                    "code": 404,
                    "data": None
                }
                response(response_info)
                return

            # delete
            resource["is_deleted"] = True

            with open(self.file_path, "w") as file:
                json.dump(self.data_held, file, indent=3)

            response_info = {
                "request_id": self.request_id,
                "status": "success",
                "message": "resource deleted",
                "code": 200,
                "data": resource
            }
            response(response_info)

        except:
            error_response = {
                "request_id": self.request_id,
                "status": "fail",
                "message": "error deleting resource",
                "code": 500,
                "data": None
            }
            response(error_response)


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
    Takes data saved from a request file, parses for the requested operation,
    and reroutes to the appropriate method.
    """
    # pull 'operation' from text request
    operation = data_requested["operation"]

    service = CRUDService(data_requested)

    # route to the appropriate CRUD Service
    if operation == "create":
        service.create_resource()
    if operation == "update":
        service.update_resource()
    if operation == "delete":
        service.delete_resource()


def response(crud_response):
    """
    call at the end of create/update/delete
    parameter is response generated by service
    """
    main_dir = Path(__file__).resolve().parent  # path to main directory (contains script)
    response_dir = main_dir / "responses"  # path to response directory (data txt files ONLY)
    response_dir.mkdir(exist_ok=True)  # create directory if non-existant

    filename = f"{crud_response["request_id"]}_response.json"
    file_path = response_dir / filename

    with open(file_path, "w") as file:
        json.dump(crud_response, file, indent=3)


def main():
    while True:
        monitor_requests(route_request)


if __name__ == "__main__":
    main()
