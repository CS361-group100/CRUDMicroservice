# CRUD Microservice
## Overview
The CRUD microservice is a headless Python microservice that provides Create, Read, Update, and Delete functionality for other programs through a file-based JSON communication pipe. 
The microservice will:
* Manage resources that are stored in JSON files (i.e data.json)
* Supports create, update, and delete operations
* Runs as a standalone proccess
* Doesn't expose any UI
* Doesn't allow for other programs to call functions directly

# Architecture
* Language: Python 3.12.2
* JSON Library: Built-in json module
* IPC method: Single control file, json, in /requests and responses/ directory
* Process Model: Runs its own process, continuously monitors for new requests
* Team Setup: Will support multiple programs in Python or C++

# Environment Variables
## Required
* CRUD_DATA_DIR
  - Must be set
  - Must point to a directory that exists
  - All input/output files (data.json, request/response files) have to be inside the working directory

# Communication Protocol
## Request Format
Requests must be valid JSON written to a request files in the requests/ directory:
{
  "request_id": "string",           
  "user_id": "string",              
  "resource_type": "string",        
  "operation": "create|update|delete",
  "resource_data": {                
      "field1": "value1",
      "field2": "value2"
  },
  "resource_id": "string (optional)" 
}

## Operation Requirments:
* Create: resource_data, note: resourse_id is generated automatically
* 
