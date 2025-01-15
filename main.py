import tkinter as tk
from tkinter import messagebox
from database import conn, cursor, mysql
from images import load_image
from tabulate import tabulate

# Create main window
main_window = tk.Tk()
main_window.title("Quiz App")
main_window.geometry("700x600")
main_window.config(bg="#B9D9EB")

# Global variables
current_question_index = 0
score = 0

# Load and place background image
bck_img = load_image(main_window,"page1.png",25,25)

def on_click(event):
    # Clears placeholder text in entry widgets when clicked.
    widget = event.widget
    widget.delete(0, tk.END)
    widget.config(fg="black")

def login():
    global user_id,id_entry,password_entry  # Declare user_id as a global variable

    email = id_entry.get()
    password = password_entry.get()

    # Query to check if the email and password exist for a player
    cursor.execute("SELECT user_id FROM users WHERE email = %s AND password = %s AND role = 'player'", (email, password))
    result = cursor.fetchone()

    if result:
        user_id = result[0]  # Assign the user_id from the query result
        start_quiz()
    else:
        messagebox.showerror("Login Error", "Invalid username or password.")



def signup():
    # Registers a new player in the database.
    global id_entry, password_entry, signup_window # Declare as global to use in perform_sign_up

    signup_window = tk.Tk()
    signup_window.title("Sign Up")
    signup_window.geometry("700x600")
    signup_window.config(bg="#B9D9EB")

    # Heading for signup
    heading = tk.Label(signup_window, text="Create an Account", fg="#005A9C", bg="#B9D9EB", font=("Comic Sans MS", 30, "bold underline"))
    heading.pack(pady=20)

    # Email label and entry field
    email_label = tk.Label(signup_window, text="Enter your Email", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20)
    email_label.pack(pady=10)
    
    id_entry = tk.Entry(signup_window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5, fg="gray")
    id_entry.insert(0, "Enter your email")  # Placeholder text
    id_entry.bind("<FocusIn>", on_click)
    id_entry.pack(pady=10)

    # Password label and entry field
    password_label = tk.Label(signup_window, text="Enter your Password", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20)
    password_label.pack(pady=10)
    
    password_entry = tk.Entry(signup_window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5, show="*", fg="gray")
    password_entry.insert(0, "Enter your password")  # Placeholder text
    password_entry.bind("<FocusIn>", on_click)
    password_entry.pack(pady=10)

    # Sign Up button
    signup_button = tk.Button(signup_window, text="REGISTER", fg="#B9D9EB", font=("Comic Sans MS", 20, "bold"), padx=50, pady=5, relief="groove", borderwidth=5, bg="#005A9C", command=perform_sign_up)
    signup_button.pack(pady=20)

def perform_sign_up():
    email = id_entry.get()  # Get the email from the signup window
    password = password_entry.get()  # Get the password from the signup window

    # Check if the email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()

    if result:
        messagebox.showerror("Error", "Email already exists! Please try logging in.")
    else:
        # Insert new player data into the database
        cursor.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, 'player')", (email, password))
        conn.commit()
        messagebox.showinfo("Signup Successful", "Account created successfully! Please log in.")

    # destroying the sign_up window
    signup_window.destroy()
    

# Fetch questions from the database
def get_questions():
    cursor.execute("SELECT question_id, question_text, correct_answer FROM questions;")
    return cursor.fetchall()

# Function to display the current question
def display_question():
    global current_question_index,question_label,questions
    question = questions[current_question_index]
    question_label.config(text=question[1])  # Update question label with the question text


def next_question():
    global current_question_index, question_label, questions, player_window, v1, cursor, user_id

    # Check if user_id is correctly assigned (ensure it's defined in the login function)
    if 'user_id' not in globals():
        messagebox.showerror("Error", "User ID is not defined.")
        return

    # Get the player's answer and the current question
    player_answer = v1.get()  # This will be either 1 (True) or 0 (False)
    current_question = questions[current_question_index]
    
    # Determine if the answer is correct
    is_correct = player_answer == current_question[2]  # Assuming the correct answer is at index 2
    player_answer_str = 'true' if player_answer == 1 else 'false'

    # Update score if the answer is correct
    if is_correct:
        global score
        score += 1  # Increment the score
        update_score()  # Update the score button text

        try:
            # Insert the attempt into the quiz_attempts table
            cursor.execute("""
                INSERT INTO quiz_attempts (user_id, question_id, player_answer, is_correct) 
                VALUES (%s, %s, %s, %s)
            """, (user_id, current_question[0], player_answer_str, is_correct))  # Store score for each attempt as 1 if correct
            conn.commit()  # Commit the changes to the database

            # Update the total score in the users table
            cursor.execute("""
                UPDATE users SET total_score = total_score + 1 WHERE user_id = %s
            """, (user_id,))
            conn.commit()  # Commit the changes to the database
            
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error inserting data: {e}")
            return

    # Move to the next question
    if current_question_index < len(questions) - 1:
        current_question_index += 1
        display_question()
    else:
        messagebox.showinfo("Quiz Over", "Quiz is over. Thank you for playing!")
        player_window.destroy()  # Close the quiz window

def show_question(index):
    """Update the question label to show the question at the specified index."""
    question_text = questions[index][1]  # Get the question text from the list
    question_label.config(text=question_text)  # Update the label to display the question

def previous_question():
    # Go to the previous question if possible.
    global current_question_index  # Declare the variable as global

    if current_question_index > 0:  # Check if we are not at the first question
        current_question_index -= 1  # Move to the previous question
        show_question(current_question_index)  # Display the updated question
    else:
        messagebox.showinfo("Alert", "This is the first question!")  # Alert if at the first question


# Function to display the score
def show_score():
    messagebox.showinfo("Your Score", f"Your current score is: {score}")

# Function to update the score button text
def update_score():
    score_button.config(text=f"Score: {score}")  # Update the button text to show the current score

# Function to start the quiz
def start_quiz():
    global window, player_window, question_label, v1, questions, score, score_button
    window.destroy()  # Close the login window

    # Create a new window for the quiz
    player_window = tk.Tk()
    player_window.title("Quiz Window")
    player_window.geometry("700x600")
    player_window.resizable(False, False)

    bck_img = load_image(player_window, "bck_img.jpg")  # Assuming you have this function

    v1 = tk.IntVar()
    score = 0

    # Welcome label placed at the top center
    welcome_label = tk.Label(player_window, text="Welcome to the Quiz!", font=("Comic Sans MS", 30, "bold"), bg="#005A9C", fg="white", relief="sunken", borderwidth=5, padx=20, pady=10)
    welcome_label.place(x=115, y=20)

    # Display the first question label
    question_label = tk.Label(player_window, text="", font=("Comic Sans MS", 20), fg="#005A9C")
    question_label.place(x=180, y=180)



    # Styling options for the True/False buttons
    button_style = {
        "font": ("Comic Sans MS", 20, "bold"),
        "bg": "white", 
        "fg": "#005A9C", 
        "relief": "sunken",
        "borderwidth": 3,
        "padx": 30,
        "pady": 5
    }

    # True button with enhanced styling
    r1 = tk.Radiobutton(player_window, text="True", variable=v1, value=1, **button_style)
    r1.place(x=180, y=300)

    # False button with enhanced styling
    r2 = tk.Radiobutton(player_window, text="False", variable=v1, value=0, **button_style)
    r2.place(x=380, y=300)

    # Previous and Next buttons
    previous_button = tk.Button(player_window, text="<<", width=2,fg="black", font=("Comic Sans MS", 15,"bold"), padx=10, pady=4, relief="groove", borderwidth=2, bg="#B9D9EB",command=previous_question)
    previous_button.place(x=70, y=400)

    next_button = tk.Button(player_window, text=">>",width=2, fg="black", font=("Comic Sans MS", 15,"bold"), padx=10, pady=4, relief="groove", borderwidth=2, bg="#B9D9EB",command=next_question)
    next_button.place(x=570, y=400)

    score_button = tk.Button(player_window, text="Score: 0", command=show_score, font=("Comic Sans MS", 15), bg="#B9D9EB", fg="#005A9C", relief="sunken", borderwidth=3)
    score_button.place(x=10, y=10)  # Place the button at the top left corner

    # Fetch and display the first question
    questions = get_questions()
    current_question_index = 0
    display_question()

    player_window.mainloop()



# admin functionalities

def add_question():
    add_questions_window = tk.Toplevel()
    add_questions_window.title("Add a Question")
    add_questions_window.geometry("700x500")
    add_questions_window.configure(bg="#B9D9EB")
    add_questions_window.resizable(False, False)

    bck_img=load_image(add_questions_window,"add_ques.jpg",0,0,500,700,False)


    # Add question heading
    title_label = tk.Label(add_questions_window, text="Add a question", fg="#005A9C", bg="#1ca9c9", font=("Comic Sans MS", 25, "bold underline"))
    title_label.place(x=150, y=20)  # Position the heading near the top center

    # Question label and entry field
    question_label = tk.Label(add_questions_window, text="Enter question text", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20)
    question_label.place(x=100, y=100)  # Adjust x and y positions for the question label
    
    question_entry = tk.Entry(add_questions_window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5,fg="gray")
    question_entry.insert(0, "Enter your question")  # Placeholder text
    question_entry.bind("<FocusIn>", on_click)
    question_entry.place(x=100, y=150)  # Position the entry field below the question label

    # Answer label and entry field
    answer_label = tk.Label(add_questions_window, text="Enter correct answer", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20)
    answer_label.place(x=100, y=220)  # Position the answer label below the question entry
    
    answer_entry = tk.Entry(add_questions_window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5,fg="gray")
    answer_entry.insert(0, " 1=True / 0=False")  # Placeholder text
    answer_entry.bind("<FocusIn>", on_click)
    answer_entry.place(x=100, y=270)  # Position the answer entry below the answer label

    def perform_add():
        
        question = question_entry.get()
        answer = answer_entry.get()

        if question and answer:
            try:
                cursor.execute("""insert into questions (question_text,correct_answer) values
                           (%s,%s)""", (question,answer))
                conn.commit()
                messagebox.showinfo("Success","Question added successfully!")

            except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
        else:
            messagebox.showwarning("Warning","Please fill the entries to add a question")

    add_question_button = tk.Button(add_questions_window, text="ADD", fg="#B9D9EB", font=("Comic Sans MS", 20, "bold"), padx=50, pady=2, relief="raised", borderwidth=5, bg="#005A9C",command=perform_add)
    add_question_button.place(x=270,y=390)
    

def delete_question():
    delete_question_window = tk.Toplevel()
    delete_question_window.title("Users")
    delete_question_window.geometry("700x600")
    delete_question_window.configure(bg="#005A9C")
    delete_question_window.resizable(False,False)

    # Heading for the window
    tk.Label(delete_question_window, text="Delete a question", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 25, "bold underline")).pack(pady=10)
    

    # Fetch all users except admins
    cursor.execute("SELECT question_id, question_text FROM questions;")
    questions = cursor.fetchall()

    # Check if there are any users to delete
    if not questions:
        no_users_label = tk.Label(delete_question_window, text="No questions available to delete.", fg="#005A9C", bg="#B9D9EB", font=("Comic Sans MS", 15))
        no_users_label.pack(pady=20)
        return

    # Listbox to display users
    question_listbox = tk.Listbox(delete_question_window, font=("Courier", 12), width=40, height=15,bg="#B9D9EB")
    question_listbox.pack(pady=20)

    # Insert users into the listbox
    for question in questions:
        question_listbox.insert(tk.END, f"ID: {question[0]} - QUESTION TEXT: {question[1]}")

    def confirm_delete():

        selected_indices = question_listbox.curselection()

        if selected_indices:
            selected_index = selected_indices[0]
            question_info = question_listbox.get(selected_index)
            question_id = int(question_info.split(" - ")[0].split(": ")[1])

            confirm = messagebox.askyesno("Confirm Deletion",f"Are you sure you want to delete the question?")

            if confirm:
                try:
                    # Deleting related records from the quiz_attempts table
                    cursor.execute("DELETE FROM quiz_attempts WHERE question_id = %s", (question_id,))
                    cursor.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))
                    conn.commit()
                    messagebox.showinfo("Success", f"Question ID {question_id} has been deleted.")
                    question_listbox.delete(selected_index)  # Remove question from listbox
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
        else:
            messagebox.showwarning("Selection Error", "Please select a question to delete.")

    delete_user_button = tk.Button(delete_question_window,text="Delete",padx=160,pady=5,fg="#FAFAFA", bg="red", font=("Comic Sans MS", 15),command=confirm_delete)
    delete_user_button.pack(pady=40)

def delete_user():
    # Create a new top-level window for deleting users
    delete_user_window = tk.Toplevel()
    delete_user_window.title("Delete User")
    delete_user_window.geometry("500x500")
    delete_user_window.configure(bg="#B9D9EB")  # Set background color
    delete_user_window.resizable(False, False)  # Disable window resizing

    # Add a heading label for the window
    heading = tk.Label(delete_user_window, text="Delete a User", fg="#005A9C", bg="#B9D9EB", 
                       font=("Comic Sans MS", 20, "bold underline"))
    heading.pack(pady=10)

    # Query the database to retrieve all users with the 'player' role
    cursor.execute("SELECT user_id, email FROM users WHERE role = 'player';")
    users = cursor.fetchall()

    # If there are no users available for deletion, display a message and return
    if not users:
        no_users_label = tk.Label(delete_user_window, text="No users available to delete.", 
                                  fg="#005A9C", bg="#B9D9EB", font=("Comic Sans MS", 15))
        no_users_label.pack(pady=20)
        return

    # Create a listbox to display users
    user_listbox = tk.Listbox(delete_user_window, font=("Helvetica", 12), width=40, height=15)
    user_listbox.pack(pady=20)

    # Populate the listbox with user IDs and emails
    for user in users:
        user_listbox.insert(tk.END, f"ID: {user[0]} - Email: {user[1]}")

    # Function to confirm and delete the selected user
    def confirm_delete():
        selected_indices = user_listbox.curselection()  # Get the selected index from the listbox
        if selected_indices:
            selected_index = selected_indices[0]
            user_info = user_listbox.get(selected_index)  # Get the selected user's information
            user_id = int(user_info.split(" - ")[0].split(": ")[1])  # Extract the user ID

            # Ask the user for confirmation before deletion
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete User ID {user_id}?")
            if confirm:
                try:
                    # Delete the user from the database
                    cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
                    conn.commit()  # Commit the changes to the database
                    messagebox.showinfo("Success", f"User ID {user_id} has been deleted.")
                    user_listbox.delete(selected_index)  # Remove the deleted user from the listbox
                except mysql.connector.Error as err:
                    messagebox.showerror("Error", f"An error occurred: {err}")
        else:
            # Display a warning if no user is selected
            messagebox.showwarning("Selection Error", "Please select a user to delete.")

    # Button to trigger the deletion process
    delete_button = tk.Button(delete_user_window, text="Delete Selected User", fg="#FAFAFA", bg="#005A9C", 
                              font=("Comic Sans MS", 12), command=confirm_delete)
    delete_button.pack(pady=10)



def view_data(text, window_title, query, tablefmt="grid"):
    # Create a new top-level window to display the data
    view_window = tk.Toplevel()
    view_window.title(window_title)  # Set the window title
    view_window.geometry("700x600")  # Set the window size
    view_window.configure(bg="#B9D9EB")  # Set background color
    view_window.resizable(False, False)  # Disable window resizing

    # Add a heading label to the window
    tk.Label(view_window, text=text, fg="#005A9C", bg="#B9D9EB", 
             font=("Comic Sans MS", 30, "bold underline")).pack(pady=10)

    # Execute the provided SQL query
    cursor.execute(query)
    data = cursor.fetchall()  # Fetch all the data from the query result

    # Extract column names from the cursor description
    column_names = [description[0] for description in cursor.description]

    # Use the tabulate library to format the data into a table with headers
    table = tabulate(data, headers=column_names, tablefmt=tablefmt)

    # Create a text widget to display the table
    text_widget = tk.Text(view_window, wrap="none", bg="#FFF", fg="#000", font=("Courier", 10))
    text_widget.insert(tk.END, table)  # Insert the table into the text widget
    text_widget.config(state=tk.DISABLED)  # Make the text widget read-only
    text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)  # Pack the widget with padding

    # Add a vertical scrollbar to the text widget
    scrollbar_y = tk.Scrollbar(view_window, orient=tk.VERTICAL, command=text_widget.yview)
    text_widget.config(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)

    # Add a horizontal scrollbar to the text widget
    scrollbar_x = tk.Scrollbar(view_window, orient=tk.HORIZONTAL, command=text_widget.xview)
    text_widget.config(xscrollcommand=scrollbar_x.set)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

# Function to view questions by calling view_data with appropriate parameters
def view_questions():
    view_data("List of Questions", "Questions", "SELECT * FROM questions;")

# Function to view users by calling view_data with appropriate parameters
def view_user():
    view_data("List of Users", "Users", "SELECT * FROM users;")

# Function to view quiz attempts by calling view_data with appropriate parameters
def view_quiz_attempt():
    view_data("Quiz Attempts", "Quiz Attempts", "SELECT * FROM quiz_attempts;")



def admin_login():

    # Prepares the interface for admin login by changing labels and fields.
    heading.config(text="Admin Login")

    bck_img=load_image(window,"admin_login.png",0,0,600,900,False)
    
    id_label.config(text="Enter Admin ID")
    id_entry.delete(0, tk.END)
    id_entry.insert(0, "admin@example.com")
    
    password_label.config(text="Enter Admin Password")
    password_entry.delete(0, tk.END)
    password_entry.insert(0, "password")

    # Change the login button functionality to handle admin login
    player_login_button.config(text="ADMIN LOG IN", command=perform_admin_login)
    
    # Hide the 'Login as admin' option to prevent confusion
    heading2.grid_forget()
    signup_button.grid_forget()
    heading3.grid_forget()
    admin_login_button.grid_forget()

def perform_admin_login():
    # Validates the admin login credentials and opens the admin window.
    if id_entry.get().lower() == "simran@gmail.com" and password_entry.get() == "simran123":
        admin_window()
    elif id_entry.get().lower() == "s" and password_entry.get() == "s":
        admin_window()
    else:
        messagebox.showerror("Error", "Invalid password or id")


def admin_window():
    # Opens the admin window after successful login.
    admin_window = tk.Toplevel()  # Creates a new window on top of the current one
    admin_window.title("Admin Window")
    admin_window.geometry("750x500")
    admin_window.configure(bg="#B9D9EB")
    admin_window.resizable(False, False)

    bck_img=load_image(admin_window,"admin_img.png",0,0,500,750,False)

    # Heading for the admin window
    admin_heading = tk.Label(admin_window, text="Admin Dashboard", fg="#005A9C", bg="white", font=("Comic Sans MS", 30, "bold underline"))
    admin_heading.place(x=170, y=20)

    # Label for managing questions
    manage_questions_label = tk.Label(admin_window, text="Manage Questions", fg="#005A9C", bg="white", font=("Comic Sans MS", 20))
    manage_questions_label.place(x=70, y=100)

    # Button to add a new question
    add_question_button = tk.Button(admin_window, text="Add Question", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15),command=add_question)
    add_question_button.place(x=70, y=150, width=200, height=40)

    # Button to view all questions
    view_questions_button = tk.Button(admin_window, text="View Questions", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15),command=view_questions)
    view_questions_button.place(x=70, y=200, width=200, height=40)

    # Button to delete a question
    delete_question_button = tk.Button(admin_window, text="Delete Question", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15),command=delete_question)
    delete_question_button.place(x=70, y=250, width=200, height=40)

    # Label for managing users
    manage_users_label = tk.Label(admin_window, text="Manage Users", fg="#005A9C", bg="white", font=("Comic Sans MS", 20))
    manage_users_label.place(x=420, y=100)

    # Button to view all users
    view_users_button = tk.Button(admin_window, text="View Users", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15),command=view_user )
    view_users_button.place(x=420, y=150, width=200, height=40)

    # Button to delete a user
    delete_user_button = tk.Button(admin_window, text="Delete User", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15), command=delete_user)
    delete_user_button.place(x=420, y=200, width=200, height=40)


    view_quiz_attempt_button = tk.Button(admin_window, text="View Quiz Attempt", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 15),command=view_quiz_attempt )
    view_quiz_attempt_button.place(x=420, y=250, width=200, height=40)

    # Button to log out
    logout_button = tk.Button(admin_window, text="Log Out", fg="black", bg="red", font=("Comic Sans MS", 15), command=admin_window.destroy)
    logout_button.place(x=245, y=350, width=200, height=60)

    admin_window.mainloop()




def get_started():
    # Switches from the main window to the login page.
    main_window.destroy()
    global window, heading, id_label, id_entry, password_label, password_entry, player_login_button, heading2, admin_login_button, signup_button, heading3
    
    # Create login window
    window = tk.Tk()
    window.title("Log In Page")
    window.geometry("900x600")
    window.resizable(False, False)
    window.config(bg="#B9D9EB")

    # Centering the window
    window.grid_columnconfigure(0, weight=1)
    window.grid_columnconfigure(1, weight=1)

    # Heading for player login
    heading = tk.Label(window, text="Player Login", fg="#005A9C", bg="#B9D9EB", font=("Comic Sans MS", 30, "bold underline"))
    heading.grid(row=0, column=0, columnspan=2, pady=10)

    # ID/Username label and entry field
    id_label = tk.Label(window, text="Enter your ID/Username", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20, pady=5)
    id_label.grid(row=1, column=0, padx=10, pady=10)
    
    id_entry = tk.Entry(window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5, fg="gray")
    id_entry.insert(0, "Enter your email")  # Placeholder text
    id_entry.bind("<FocusIn>", on_click)  # Clears placeholder on click
    id_entry.grid(row=1, column=1, padx=10, pady=10)

    # Password label and entry field
    password_label = tk.Label(window, text="Enter your password", fg="#B9D9EB", bg="#005A9C", font=("Comic Sans MS", 20), width=20, pady=5)
    password_label.grid(row=2, column=0, padx=10, pady=10)
    
    password_entry = tk.Entry(window, font=("Comic Sans MS", 20), width=20, relief="groove", borderwidth=5, show="*", fg="gray")
    password_entry.insert(0, "Enter your password")  # Placeholder text
    password_entry.bind("<FocusIn>", on_click)  # Clears placeholder on click
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    # Player login button (validates player login)
    player_login_button = tk.Button(window, text="PLAYER LOG IN", fg="#B9D9EB", font=("Comic Sans MS", 20, "bold"), padx=50, pady=5, relief="groove", borderwidth=5, bg="#005A9C", command=login)
    player_login_button.grid(row=3, column=0, columnspan=2, pady=20)

    # Sign-Up section
    heading2 = tk.Label(window, text="Don't have an account? SIGN UP :- ", fg="#005A9C", bg="#B9D9EB", font=("Braggadocio", 20))
    heading2.grid(row=4, column=0, pady=10)
    
    signup_button = tk.Button(window, text="SIGN UP", fg="#B9D9EB", font=("Comic Sans MS", 15), padx=4, pady=1, relief="groove", borderwidth=5, bg="#005A9C", command=signup)
    signup_button.grid(row=4, column=1, pady=10)

    # Admin login option
    heading3 = tk.Label(window, text="Login as admin:- ", fg="#005A9C", bg="#B9D9EB", font=("Braggadocio", 20))
    heading3.grid(row=5, column=0, pady=10)

    admin_login_button = tk.Button(window, text="ADMIN LOG IN", fg="#B9D9EB", font=("Comic Sans MS", 15), padx=4, pady=1, relief="groove", borderwidth=5, bg="#005A9C", command=admin_login)
    admin_login_button.grid(row=5, column=1, pady=10)

# Get started button on the main window (redirects to login page)
get_started_button = tk.Button(main_window, text="GET STARTED", fg="#B9D9EB", font=("Comic Sans MS", 20, "bold"), relief="raised", borderwidth=5, bg="#005A9C", command=get_started)
get_started_button.place(x=140, y=450, width=400, height=100)



# Main loop to keep the application running
main_window.mainloop()


# Close the cursor and connection after the main loop ends
cursor.close()
conn.close()          