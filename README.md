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

### Log In:

- Username: admin
- Password: admin


### Input Data:

Fill in the form with the required information. The form is divided into three sections:
- Date and Time (required)
- Telescope Status (required and the default value is 'Not Ready')
- Cancellations 
  - Not required if there's no cancellation
  - If there is a cancellation, the user can input the time and reason for the cancellation and click the 'Add' button to add the cancellation to the list. 
  - The user can also remove a cancellation by selecting the cancellations and clicking the 'Remove' button. 
  - You can add and remove multiply cancellations

### Save Data:
If the operator wants to save the data and continue logging, click the 'Save' button. The data will be saved for the current session and be retrieved when the user logs in and selects 'Edit existing log' again.
### Submit Data:

Click the 'Submit' button. The data will first be validated. If validation is successful, the data will be saved to the database.
### View and download Log:

- Click the 'Log' button in the navbar and select 'Log History' to display the data stored in the database. 
- Select the 'Download Log' button to download the data stored in the database as a CSV file.