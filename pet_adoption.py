import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date

#connect host

try:
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="narendra",
        database="petadoptionsystem"
    )
    cursor = con.cursor()
except mysql.connector.Error as err:
   
    print(f"Database Connection Error: {err}")
    con, cursor = None, None

def execute_sql(sql_query, params=None, fetch=False):
    """Helper function to safely execute SQL and handle errors/transactions."""
    if con is None:
        messagebox.showerror("Connection Error", "Database connection is not available.")
        return None
    try:
        if fetch:
            cursor.execute(sql_query, params)
            return cursor.fetchall()
        else:
            cursor.execute(sql_query, params)
            con.commit()
            return cursor.rowcount
    except mysql.connector.Error as err:
        con.rollback()
        messagebox.showerror("Database Error", f"SQL execution failed: {err}")
        return None
    except Exception as e:
        con.rollback()
        messagebox.showerror("System Error", f"An unexpected error occurred: {e}")
        return None

def setup_database():
    """Sets up the necessary tables (Pets, Adopters, Adoption)."""
    if con is None: return
    
    # Drop tables safely
    execute_sql("DROP TABLE IF EXISTS Adoption")
    execute_sql("DROP TABLE IF EXISTS Pets")
    execute_sql("DROP TABLE IF EXISTS Adopters")

    # 1. Create Pets Table
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Pets (
        Pet_ID INT PRIMARY KEY AUTO_INCREMENT,
        Pet_Name VARCHAR(50),
        Breed VARCHAR(50),
        Age INT,
        Gender VARCHAR(10),
        Status VARCHAR(20) DEFAULT 'Available'
    )
    """)

    # 2. Create Adopters Table
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Adopters (
        Adopter_ID INT PRIMARY KEY AUTO_INCREMENT,
        Adopter_Name VARCHAR(50),
        Phone VARCHAR(15), 
        City VARCHAR(50)
    )
    """)

    # 3. Create Adoption Table
    execute_sql("""
    CREATE TABLE IF NOT EXISTS Adoption (
        Adoption_ID INT PRIMARY KEY AUTO_INCREMENT,
        Pet_ID INT,
        Adopter_ID INT,
        Adoption_Date DATE,
        FOREIGN KEY (Pet_ID) REFERENCES Pets(Pet_ID),
        FOREIGN KEY (Adopter_ID) REFERENCES Adopters(Adopter_ID)
    )
    """)
    print("Tables created successfully!")


def setup_features():
    """Sets up the database features: Trigger, Stored Procedure, Function, and View."""
    if con is None: return
    
    # Drop features before recreation to prevent errors
    execute_sql("DROP TRIGGER IF EXISTS update_pet_status")
    execute_sql("DROP PROCEDURE IF EXISTS RegisterAdoption")
    execute_sql("DROP FUNCTION IF EXISTS GetAvailablePets")
    execute_sql("DROP VIEW IF EXISTS AdoptedPets")

    # Trigger: Updates pet status to 'Adopted'
    execute_sql("""
    CREATE TRIGGER update_pet_status
    AFTER INSERT ON Adoption
    FOR EACH ROW
    UPDATE Pets SET Status='Adopted' WHERE Pet_ID = NEW.Pet_ID
    """)

    # Stored Procedure: Handles adoption registration
    execute_sql("""
    CREATE PROCEDURE RegisterAdoption(IN p_pet_id INT, IN p_adopter_id INT)
    BEGIN
        INSERT INTO Adoption (Pet_ID, Adopter_ID, Adoption_Date)
        VALUES (p_pet_id, p_adopter_id, CURDATE());
    END
    """)

    # Function: Returns the count of available pets
    execute_sql("""
    CREATE FUNCTION GetAvailablePets()
    RETURNS INT
    DETERMINISTIC
    BEGIN
        DECLARE available_count INT;
        SELECT COUNT(*) INTO available_count FROM Pets WHERE Status='Available';
        RETURN available_count;
    END
    """)

    # View: Report of adopted pets and adopters
    execute_sql("""
    CREATE VIEW AdoptedPets AS
    SELECT p.Pet_Name, p.Breed, a.Adopter_Name, a.City, ad.Adoption_Date
    FROM Pets p
    JOIN Adoption ad ON p.Pet_ID = ad.Pet_ID
    JOIN Adopters a ON ad.Adopter_ID = a.Adopter_ID
    """)
    print("Trigger, Procedure, Function, and View created successfully...")

#  Tkinter Application Class 

class PetAdoptionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(" Pet Adoption System")
        self.geometry("800x800")
        
        if con is None:
            messagebox.showerror("Connection Error", "Could not connect to the database. Application closing.")
            self.destroy()
            return
            
        try:
            setup_database()
            setup_features()
        except Exception as e:
            messagebox.showerror("Setup Error", f"Failed to set up database: {e}")
            self.destroy()
            return

        self.create_main_menu()

    def create_main_menu(self):
        # Clear existing content if called multiple times 
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = tk.Frame(self, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="PET ADOPTION SYSTEM", font=("Arial", 18, "bold"), fg="#007acc").pack(pady=10)
        
        # Helper function 
        def create_button(text, command):
            tk.Button(main_frame, text=text, command=command, width=35, height=1, bg="#e0e0e0").pack(pady=4)

        # Pet Management
        tk.Label(main_frame, text="               Pet Management                ", font=("Arial", 14)).pack(pady=5)
        create_button("1. Add New Pet", self.show_add_pet_form)
        create_button("2. View All Pets", self.view_pets_gui)
        create_button("3. Update Pet Name", self.show_update_pet_name_form)
        create_button("4. Delete Pet", self.show_delete_pet_form)
        create_button("5. Search Pet by Name", self.show_search_pet_form)

        # Adopter Management
        tk.Label(main_frame, text="               Adopter Management                ", font=("Arial", 14)).pack(pady=5)
        create_button("6. Add Adopter", self.show_add_adopter_form)
        create_button("7. View All Adopters", self.view_adopters_gui)

        # Adoption Operations
        tk.Label(main_frame, text="             Adoption Operations                  ", font=("Arial", 14)).pack(pady=5)
        create_button("8. Adopt a Pet", self.show_adopt_pet_form)
        create_button("9. View Adopted Pets Report", self.view_adopted_pets_gui)
        create_button("10. Show Available Pets Count", self.show_available_pets_count_gui)

        tk.Label(main_frame, text=" _____________-_____________", font=("Arial", 12)).pack(pady=5)
        create_button("11. Exit", self.on_exit)

    # --- Utility Functions for Display ---
    def create_table_window(self, title, columns, data):
        """Creates a Toplevel window to display data in a Treeview table."""
        view_window = tk.Toplevel(self)
        view_window.title(title)
        view_window.geometry("750x300")
        
        tree = ttk.Treeview(view_window, columns=columns, show='headings')
        
        for col in columns:
            tree.heading(col, text=col.replace("_", " "))
            tree.column(col, width=100, anchor='center')

        if data:
            for row in data:
                tree.insert("", tk.END, values=row)
        else:
            tree.insert("", tk.END, values=("(No records found)",) * len(columns))

        scrollbar = ttk.Scrollbar(view_window, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")

    def create_input_form(self, title, fields, button_text, command):
        """Creates a Toplevel window with input fields."""
        form_window = tk.Toplevel(self)
        form_window.title(title)
        form_window.grid_columnconfigure(1, weight=1)
        
        entries = {}
        for i, field in enumerate(fields):
            tk.Label(form_window, text=f"{field}:").grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(form_window, width=40)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            entries[field] = entry

        tk.Button(form_window, text=button_text, command=lambda: command(entries, form_window), width=20).grid(row=len(fields), column=0, columnspan=2, pady=15)
        return entries, form_window

    # --- Option 1: Add New Pet ---
    def show_add_pet_form(self):
        fields = ["Pet Name", "Breed", "Age (INT)", "Gender"]
        self.create_input_form("Add New Pet", fields, "Add Pet", self.add_pet_gui)

    def add_pet_gui(self, entries, window):
        name, breed, age_str, gender = [entries[f].get() for f in ["Pet Name", "Breed", "Age (INT)", "Gender"]]
        try:
            age = int(age_str)
        except ValueError:
            messagebox.showerror("Input Error", "Age must be an integer.")
            return

        rowcount = execute_sql("INSERT INTO Pets (Pet_Name, Breed, Age, Gender) VALUES (%s, %s, %s, %s)",
                               (name, breed, age, gender))
        if rowcount is not None and rowcount > 0:
            messagebox.showinfo("Success", "Pet added successfully!")
            window.destroy()

    # --- Option 2: View All Pets ---
    def view_pets_gui(self):
        pets = execute_sql("SELECT Pet_ID, Pet_Name, Breed, Age, Gender, Status FROM Pets", fetch=True)
        self.create_table_window("All Pets", ["Pet_ID", "Pet_Name", "Breed", "Age", "Gender", "Status"], pets)
    
    # --- Option 3: Update Pet Name ---
    def show_update_pet_name_form(self):
        fields = ["Pet ID (INT)", "New Name"]
        self.create_input_form("Update Pet Name", fields, "Update Name", self.update_pet_name_gui)

    def update_pet_name_gui(self, entries, window):
        pet_id_str, new_name = [entries[f].get() for f in ["Pet ID (INT)", "New Name"]]
        try:
            pet_id = int(pet_id_str)
        except ValueError:
            messagebox.showerror("Input Error", "Pet ID must be an integer.")
            return
        
        rowcount = execute_sql("UPDATE Pets SET Pet_Name = %s WHERE Pet_ID = %s", (new_name, pet_id))
        if rowcount is not None:
            if rowcount > 0:
                messagebox.showinfo("Success", f"Pet ID {pet_id} name updated to '{new_name}' successfully!")
                window.destroy()
            else:
                messagebox.showerror("Update Failed", f"No pet found with ID {pet_id}.")
    
    # --- Option 4: Delete Pet ---
    def show_delete_pet_form(self):
        fields = ["Pet ID (INT)"]
        self.create_input_form("Delete Pet", fields, "Delete Pet", self.delete_pet_gui)

    def delete_pet_gui(self, entries, window):
        pet_id_str = entries["Pet ID (INT)"].get()
        try:
            pet_id = int(pet_id_str)
        except ValueError:
            messagebox.showerror("Input Error", "Pet ID must be an integer.")
            return

        if not messagebox.askyesno("Confirmation", f"Are you sure you want to delete Pet ID {pet_id} and all related adoption records?"):
            return

        # Delete dependent records first, then the pet
        execute_sql("DELETE FROM Adoption WHERE Pet_ID = %s", (pet_id,))
        rowcount = execute_sql("DELETE FROM Pets WHERE Pet_ID = %s", (pet_id,))
        
        if rowcount is not None:
            if rowcount > 0:
                messagebox.showinfo("Success", f"Pet ID {pet_id} deleted successfully!")
                window.destroy()
            else:
                messagebox.showerror("Delete Failed", f"No pet found with ID {pet_id}.")

    # --- Option 5: Search Pet by Name ---
    def show_search_pet_form(self):
        fields = ["Pet Name (Partial)"]
        self.create_input_form("Search Pet", fields, "Search", self.search_pet_by_name_gui)

    def search_pet_by_name_gui(self, entries, window):
        name = entries["Pet Name (Partial)"].get()
        if not name:
            messagebox.showerror("Input Error", "Please enter a pet name.")
            return
            
        pets = execute_sql("SELECT Pet_ID, Pet_Name, Breed, Age, Gender, Status FROM Pets WHERE Pet_Name LIKE %s", 
                           ('%' + name + '%',), fetch=True)
        
        if pets:
            self.create_table_window(f"Search Results for '{name}'", ["Pet_ID", "Pet_Name", "Breed", "Age", "Gender", "Status"], pets)
        else:
            messagebox.showinfo("No Results", f"No pets found with names matching '{name}'.")

        window.destroy()

    # --- Option 6: Add Adopter ---
    def show_add_adopter_form(self):
        fields = ["Adopter Name", "Phone", "City"]
        self.create_input_form("Add New Adopter", fields, "Add Adopter", self.add_adopter_gui)

    def add_adopter_gui(self, entries, window):
        name, phone, city = [entries[f].get() for f in ["Adopter Name", "Phone", "City"]]
        
        rowcount = execute_sql("INSERT INTO Adopters (Adopter_Name, Phone, City) VALUES (%s, %s, %s)",
                               (name, phone, city))
        if rowcount is not None and rowcount > 0:
            messagebox.showinfo("Success", "Adopter added successfully!")
            window.destroy()

    # --- Option 7: View All Adopters ---
    def view_adopters_gui(self):
        adopters = execute_sql("SELECT Adopter_ID, Adopter_Name, Phone, City FROM Adopters", fetch=True)
        self.create_table_window("All Adopters", ["Adopter_ID", "Adopter_Name", "Phone", "City"], adopters)

    # --- Option 8: Adopt a Pet (Uses Stored Procedure and Trigger) ---
    def show_adopt_pet_form(self):
        fields = ["Pet ID (INT)", "Adopter ID (INT)"]
        self.create_input_form("Adopt a Pet", fields, "Register Adoption", self.adopt_pet_gui)

    def adopt_pet_gui(self, entries, window):
        pet_id_str, adopter_id_str = [entries[f].get() for f in ["Pet ID (INT)", "Adopter ID (INT)"]]
        
        try:
            pet_id = int(pet_id_str)
            adopter_id = int(adopter_id_str)
        except ValueError:
            messagebox.showerror("Input Error", "IDs must be integers.")
            return

        # 1. Check if pet is available
        status_result = execute_sql("SELECT Status FROM Pets WHERE Pet_ID = %s", (pet_id,), fetch=True)
        if status_result is None or not status_result:
            messagebox.showerror("Adoption Failed", f"Pet ID {pet_id} not found.")
            return
        
        pet_status = status_result[0][0]
        if pet_status == 'Adopted':
            messagebox.showerror("Adoption Failed", f"Pet ID {pet_id} is already adopted.")
            return

        # 2. Execute Stored Procedure
        try:
            cursor.callproc("RegisterAdoption", (pet_id, adopter_id))
            con.commit()
            messagebox.showinfo("Success", "Pet adopted successfully! Status updated via Trigger.")
            window.destroy()
        except mysql.connector.Error as err:
            con.rollback()
            messagebox.showerror("Database Error", f"Error during adoption: {err}\nEnsure both IDs are valid.")

    # --- Option 9: View Adopted Pets Report (Uses View) ---
    def view_adopted_pets_gui(self):
        adopted = execute_sql("SELECT Pet_Name, Breed, Adopter_Name, City, Adoption_Date FROM AdoptedPets", fetch=True)
        self.create_table_window("Adopted Pets Report", ["Pet_Name", "Breed", "Adopter_Name", "City", "Adoption_Date"], adopted)

    # --- Option 10: Show Available Pets Count (Uses Function) ---
    def show_available_pets_count_gui(self):
        count_result = execute_sql("SELECT GetAvailablePets()", fetch=True)
        if count_result is not None:
            count = count_result[0][0]
            messagebox.showinfo("Available Pets", f"Total Available Pets: {count}")

    # --- Option 11: Exit ---
    def on_exit(self):
        """Cleanly close the database connection and exit."""
        if con and con.is_connected():
            con.close()
        self.destroy()

# Run Program
if __name__ == "__main__":
    if con is not None:
        app = PetAdoptionApp()
        # Bind the exit handler to the window close button
        app.protocol("WM_DELETE_WINDOW", app.on_exit) 
        app.mainloop()