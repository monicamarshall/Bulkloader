# Bulkloader

Python django project that bulkloads json data retrieved via Python requests library from the Conference Speaker service. See CRUDGenerics project to view the Speaker service.

The project uses Python 3.6, Django 2.2.10, and djangorestframework 3.9.2

This project includes a bulkload service that reads Speaker data retrieved in json format from the Speaker service and bulkloads it into a Postgres database.  

Two Methods are available to bulkload the database:

Postgres native copy_from, which loads over 20,000 records in about 80 milliseconds.

Django ORM bulk_create which loads over 20,000 records in about 2 seconds.

Clearly, the Postgres native copy_from utility is lightning fast and outperforms every other bulkloading methods.

Both bulkloading capabilities read json data from the Speader service, store the json data in csv files, then read the values in the cvs files to bulkload it in the database.

The speaker.csv files created from reading the json output and written to a csv file in comma-separated rows of values are stored in the web server file system.

After the bulkload has finished, all records are deleted from the database.  

To preserve all records in the database comment out line 95 in bulkload/views.py:  models.Speaker.objects.all().delete()

Access the Speaker service at: http://localhost:8089/bulkload/ (The port is decided at the time the server is started)


