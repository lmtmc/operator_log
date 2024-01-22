# Operator Log App
## Introduction
The Operator Logging App is a web-based interface designed for logging telescope statuses. It offers a streamlined and user-friendly platform for operators to input and manage data efficiently. Below are detailed instructions for setting up and running the application.

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

### Log In:

- Username: admin
- Password: admin
### Input Data:

Fill in all fields marked with a red asterisk ("*").
### Submit Data:

Click the 'Submit' button. The data will first be validated. If validation is successful, the data will be saved to the database.
### View Logs:

Click the 'Log' button to display the data stored in the database.

### Download Logs:
Click the 'Download' button to download the data stored in the database as a CSV file.