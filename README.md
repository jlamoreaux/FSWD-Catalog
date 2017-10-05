# Sports Product Catalog

Sports Product Catalog is a website which was built using Flask framework in Python. The items in the catalog are accessed using SQLAlchemy. Users log in using Google or Facebook OAuth. Once logged in users can create, edit and delete categories and items.

## Requirements
- Python 2.7.12
- SQLAlchemy 1.1.12
- Flask 0.9
- OAuth2Client 4.1.2

## Setup
The file [catalog.zip](#) can be found in this repository. To initialize the database, open the shell and navigate to the folder which contains _catalog.zip_ and run the following commands:<br>

`unzip catalog.zip` _This unzips the folder containing all needed files_<br>
`python itemSetup.py` _This initializes the database and populates the tables with the contents of the catalog_

## Running the Program
To run the program, you must run `python views.py`.

The server will begin to run locally. You may now open a web browser and enter `localhost:8000` into the address bar. You are now able to navigate the site.

## API
API requests will return JSON objects from the following urls:
`localhost:8000/catalog/JSON` _This returns all the categories in the catalog._
`localhost:8000/catalog/<category_name>/JSON` _This returns all items in a catalog._
`localhost:8000/catalog/<category_name/<item_id>/JSON` _This returns the data for a specific item._

_**NOTE: <category_name> and <item_id> are variables that must be known to get results. (E.g. "localhost:8000/catalog/football/1/JSON")**_
