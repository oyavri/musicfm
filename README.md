# Initialization

If you have a data set, you can put them into a folder called "data" in order for database to load them. The expected file format is CSV. The columns of CSV file can be found by inspecting the script for importing data to the database. Otherwise, the project will start with initializing the tables for the project without the data. 

# Running the project

To run the project, you need to have docker installed to run the project. The server and the database are configured to run in containers. 

The `docker-compose.yaml` file handles all of the running configurations. Thus, the only command to run the project is indicated below. The flag "-d" is for running the task in the background.
```sh
docker-compose up -d 
```

If it does not work, try the following before running `docker-compose up -d`
```sh
docker-compose build app
```
