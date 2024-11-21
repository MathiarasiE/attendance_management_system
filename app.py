from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'mathi'  # Make sure to change this key for security purposes

# Database configuration
app.config['MYSQL_HOST'] = '127.0.0.1'  # Your MySQL host
app.config['MYSQL_USER'] = 'root'  # Your MySQL username
app.config['MYSQL_PASSWORD'] = '1234'  # Your MySQL password
app.config['MYSQL_DB'] = 'attendance_db'  # Your MySQL database name

mysql = MySQL(app)

# Route for the home page (root URL)
@app.route('/')
def home():
    return redirect(url_for('login'))  # Redirect to login page

# Route to handle login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple validation logic for login (you can improve this)
        if username == 'admin' and password == 'admin':
            session['logged_in'] = True  # Store the session to track user login
            return redirect(url_for('attendance'))  # Redirect to attendance after successful login
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    if 'logged_in' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login page

    if request.method == 'POST':
        student_id = request.form['student_id']
        student_name = request.form['student_name']
        date = request.form['date']
        status = request.form['status'].lower()

        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO attendance_records(student_id, student_name, date, status) VALUES(%s, %s, %s, %s)",
                        (student_id, student_name, date, status))
            mysql.connection.commit()  # Commit changes
            cur.close()
            flash('Attendance added successfully!', 'success')
        except Exception as e:
            print(f"Error: {e}")
            flash('An error occurred while saving attendance.', 'danger')

    # For testing, insert a record directly
    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO attendance_records(student_id, student_name, date, status) VALUES(%s, %s, %s, %s)",
                    ('S003', 'Test Student', '2024-11-20', 'present'))
        mysql.connection.commit()  # Commit changes
        cur.close()
    except Exception as e:
        print(f"Error inserting test record: {e}")

    # Fetch all attendance records
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM attendance_records")
    attendance_records = cur.fetchall()
    cur.close()

    return render_template('attendance.html', attendance_records=attendance_records)


# Route to handle attendance search
@app.route('/search_attendance', methods=['POST'])
def search_attendance():
    if 'logged_in' not in session:
        return redirect(url_for('login'))  # If not logged in, redirect to login page

    student_id_or_name = request.form['student_id']  # Get the search input
    cur = mysql.connection.cursor()

    # Query to search attendance records by student ID or name
    cur.execute("SELECT * FROM attendance_records WHERE student_id LIKE %s OR student_name LIKE %s",
                (f'%{student_id_or_name}%', f'%{student_id_or_name}%'))
    attendance_records = cur.fetchall()
    cur.close()

    return render_template('attendance.html', attendance_records=attendance_records)

# Route to update attendance
@app.route('/update_attendance/<string:student_id>', methods=['GET', 'POST'])
def update_attendance(student_id):
    if 'logged_in' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # If not, redirect to login page

    cur = mysql.connection.cursor()
    
    # Fetch the existing record for the student to update
    cur.execute("SELECT * FROM attendance_records WHERE student_id = %s", [student_id])
    record = cur.fetchone()

    if request.method == 'POST':
        student_name = request.form['student_name']
        date = request.form['date']
        status = request.form['status'].lower()  # Convert status to lowercase to match ENUM values
        
        # Validate status
        if status not in ['present', 'absent', 'on_duty']:
            flash('Invalid status value. Please select a valid status.', 'danger')
            return redirect(url_for('attendance'))

        # Update the record in the database
        cur.execute("UPDATE attendance_records SET student_name = %s, date = %s, status = %s WHERE student_id = %s",
                    (student_name, date, status, student_id))
        mysql.connection.commit()
        cur.close()

        flash('Attendance record updated successfully!', 'success')
        return redirect(url_for('attendance'))

    return render_template('update_attendance.html', record=record)

# Route to delete attendance
@app.route('/delete_attendance/<string:student_id>', methods=['GET'])
def delete_attendance(student_id):
    if 'logged_in' not in session:  # Check if user is logged in
        return redirect(url_for('login'))  # Redirect to login page if not logged in

    try:
        cur = mysql.connection.cursor()

        # Check if the record exists before attempting to delete it
        cur.execute("SELECT * FROM attendance_records WHERE student_id = %s", [student_id])
        record = cur.fetchone()

        if not record:
            flash('Record not found. Unable to delete.', 'danger')
            return redirect(url_for('attendance'))

        # Delete the attendance record
        cur.execute("DELETE FROM attendance_records WHERE student_id = %s", [student_id])
        mysql.connection.commit()
        cur.close()

        flash('Attendance record deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting record: {e}")
        flash('An error occurred while deleting the record.', 'danger')

    return redirect(url_for('attendance'))

# Route to log out the user
@app.route('/logout')
def logout():
    session.pop('logged_in', None)  # Remove logged-in session
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))  # Redirect to login page after logout

if __name__ == '__main__':
    app.run(debug=True)
