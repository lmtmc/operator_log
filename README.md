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

### Arriving:

- Click the "Arrive" button and the arrival time will be recorded in the database.



### Facility Instruments Ready:

- Click all the ready instrument and the submit button, then the instrument status will be recorded in the database.

### Report A Problem:

- Click the "Report A Problem" button and fill the information and click the 'report' button, the problem will be recorded in the database.
- After the problem is resolved, click the "Fixed" button and the problem will be marked as resolved in the database.
- If another problem arises, repeat the above steps. 

### Leaving:

- Click the "Leave" button and the leave time will be recorded in the database.

