import mysql.connector

# Database connection
try:
    conn = mysql.connector.connect(host="localhost", user="root")
    cursor = conn.cursor()

    # Switch to quiz_app database
    cursor.execute("USE quiz_app;")
    
    # Fetch and print questions
    # cursor.execute("drop table users;")
    # print(cursor.fetchall())

    # Uncomment if you need to create tables or insert values
    # cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    #                user_id INT PRIMARY KEY AUTO_INCREMENT,
    #                email VARCHAR(50) UNIQUE NOT NULL,
    #                password VARCHAR(30) NOT NULL,
    #                role ENUM('admin', 'player') NOT NULL);""")

    # cursor.execute("ALTER TABLE users ADD COLUMN total_score INT DEFAULT 0;")

    # cursor.execute("""CREATE TABLE IF NOT EXISTS questions(
    #                question_id INT PRIMARY KEY AUTO_INCREMENT,
    #                question_text VARCHAR(50) NOT NULL,
    #                correct_answer BOOLEAN NOT NULL);""")

    # cursor.execute("""CREATE TABLE IF NOT EXISTS quiz_attempts (
    #                     id INT PRIMARY KEY AUTO_INCREMENT,
    #                     user_id INT,
    #                     question_id INT,
    #                     player_answer ENUM('true', 'false'),
    #                     is_correct BOOLEAN,
    #                     attempt_time_and_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    #                     FOREIGN KEY (user_id) REFERENCES users(user_id),
    #                     FOREIGN KEY (question_id) REFERENCES questions(question_id)
    #                 );""")

    # cursor.execute("""INSERT INTO users(email, password, role) 
    #                 VALUES ('simran@gmail.com', 'simran123', 'admin');""")

    # cursor.execute("""INSERT INTO questions (question_text, correct_answer) 
    # VALUES 
    #               ('Lightning never strikes the same place.', FALSE),
    #               ('Humans have five basic senses.', TRUE),
    #               ('Tomatoes are considered a vegetable.', FALSE),
    #               ('Saturn has the most moons.', TRUE),
    #               ('Penguins can fly in the sky.', FALSE),
    #               ('Spiders have eight legs only.', TRUE),
    #               ('The moon is a planet.', FALSE),
    #               ('Water freezes at zero degrees.', TRUE),
    #               ('A dolphin is a type of fish.', FALSE),
    #               ('Honey never spoils over time.', TRUE);
    #               """)

    conn.commit()

except mysql.connector.Error as err:
    print(f"Error: {err}")


