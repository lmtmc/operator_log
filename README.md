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
The application will then be accessible at http://127.0.0.1:8050/observer_log.

### Arrival:

- Select observers' names and input other observers
- Input the arrival time 
- Check the ready instruments
- click the "SAVE" button to save the data in the database.



### Pause or Cancellation:

- Input the cancellation time
- Enter reasons
- Click the "SAVE" button to save the data in the database.

### Resume:

- Input the resume time
- Input comment
- Click the "SAVE" button to save the data in the database.
### User Note:
- Input ObsNums
- Input keywords
- Input Entry
- Click the "SAVE" button to save the data in the database.

### Shutdown:
- Input the shutdown time 
- Click the "SAVE" button to save the data in the database.

### View Log History:
- Click the "View Log History" button to view the 10 most recent log history.

### Download Log:
- Click the "Download Log" button to download the log history in CSV format.