# Operator Log App
## Introduction
The Operator Log App is a web-based interface designed for logging telescope statuses. It offers a streamlined and user-friendly platform for operators to input and manage data efficiently. Below are detailed instructions for setting up and running the application.

## Setup
### Environment and Dependencies
To set up your environment and install the required dependencies, follow these steps:

#### Create a Virtual Environment:

```
python3 -m venv env
```
#### Activate the Virtual Environment:

```angular2html
source env/bin/activate
```
#### Install Dependencies:

```angular2html
pip3 install -r requirements.txt
```
## Start the Application:

```angular2html
python3 app.py
```
The application will then be accessible at http://127.0.0.1:8050.

### Arrival:

- Input operator's name and arrival time then click the "SAVE" button to save the data in the database.



### Facility Instruments Ready:

- Check all the ready instrument and then click the "SAVE" button to save the data in the database.

### Report A Problem:

- Input the problem fields and then click the "SAVE" button to save the data in the database.
### Restart:

- Input the restart time and then click the "SAVE" button to save the data in the database.
### Shutdown:
- Input the shutdown time and then click the "SAVE" button to save the data in the database.

