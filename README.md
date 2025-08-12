#Doctor Appointment Scheduler

Doctor Appointment Scheduler is a Python-based application developed using Tkinter for the GUI and MongoDB as the backend database.
It allows users to manage doctor appointments efficiently by providing complete CRUD (Create, Read, Update, Delete) functionality in a simple, intuitive interface.

#Features
1. Add Appointments: Schedule new appointments with patient details, date, and time.
2. View Appointments: Display all appointments in a tabular format for easy review.
3. Update Appointments: Edit existing appointment details with ease.
4. Delete Appointments: Remove unwanted appointments instantly.
5. Persistent Storage: All data is stored securely in MongoDB, ensuring information is retained even after the application is closed.

#Technology Stack
1. Programming Language: Python
2. GUI Framework: Tkinter
3. Database: MongoDB
4. Database Connector: PyMongo

#Installation & Setup
Install MongoDB
Make sure MongoDB is installed and running on your system.

#Install Python Dependencies
Open a terminal and run:
pip install pymongo tkcalendar

#Run the Application
Navigate to the project folder and run:
python appsch.py

#How It Works
1. The application connects to a MongoDB collection.
2. User inputs are collected via Tkinter forms.
3. The system performs insert, read, update, and delete operations directly on the MongoDB database.

#Project Structure

doctor-appointment-scheduler/
│
├── main.py              # Main application script
├── requirements.txt     # Dependencies list
└── README.md            # Project documentation
