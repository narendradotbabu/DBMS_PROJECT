# DBMS_PROJECT
Here is a **complete, ready-to-upload README.md** for your GitHub project.

#  Pet Adoption Management System

*A Python + Tkinter + MySQL Desktop Application*

##  Overview

The Pet Adoption Management System is a GUI-based desktop application built using **Python (Tkinter)** and **MySQL**.
It allows users to manage pets, adopters, and adoption records through a clean and organized interface.
This project also demonstrates the use of **SQL Triggers, Stored Procedures, Functions, and Views**, making it a complete database-driven application.


###  Pet Management

* Add new pets
* View all pets
* Update pet name
* Delete pet (with cascading adoption record deletion)
* Search pets by name

### Adopter Management

* Add adopter details
* View all adopters

### Adoption Operations

* Adopt a pet using a Stored Procedure
* Pet status updated automatically using a Trigger
* View adopted pets report using a Database View
* Display total available pets using an SQL Function


##  Database Structure

### Tables

* Pets
* Adopters
* Adoption

### Stored Procedure

* `RegisterAdoption(p_pet_id, p_adopter_id)`

### Trigger

 `update_pet_status`
  Automatically updates pet status to Here.



### **Function**

* `GetAvailablePets()`
  Returns number of available pets.

### **View**

* `AdoptedPets`
  Displays full adoption report (pet + adopter + date).



##  Tech Stack

* **Python 3.x**
* **MySQL**
* **mysql-connector-python**
* **Tkinter (GUI framework)**



## 'project Structure


pet_adoption.py  


##  GUI Highlights

* Menu-based navigation
* Treeview tables for displaying records
* Pop-up forms for adding/updating/deleting
* Built-in validation and message alerts


##  Installation & Setup

### 1. Install Dependencies**

```bash
pip install mysql-connector-python
```

### **2. Create Database**

Open MySQL and run:

```sql
CREATE DATABASE petadoptionsystem;
```

### **3. Update Credentials**

In the code:

```python
host="localhost"
user="root"
password="your_mysql_password"
```

### **4. Run the Application**

```bash
python pet_adoption.py
```

On startup, the program will:

* Create all tables
* Create trigger, procedure, view, and function
* Launch the GUI



##  Learning Outcomes

✔ Tkinter GUI development
✔ MySQL integration with Python
✔ CRUD operations
✔ SQL advanced features (Triggers, Procedures, Views)
✔ Error handling & modular programming


##  License

This project is open-source and free to use.

