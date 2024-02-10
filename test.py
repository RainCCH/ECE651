from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
import re

app = Flask(__name__)
CORS(app)

email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'rainchoi228'
app.config['MYSQL_DB'] = 'OnlineTutor'

mysql = MySQL(app)

# Route for adding a new student
@app.route('/add_student', methods=['POST'])
def add_student():
    # Get data from request
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    # Hash the password for security
    hashed_password = generate_password_hash(password)
    # Create a cursor
    cur = mysql.connection.cursor()
    try:
        # Check for duplicate username or email
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        cur.execute("SELECT * FROM Students WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            # Found a duplicate
            return jsonify({'error': 'Username or email already exists.'}), 409

        # No duplicates found, proceed to insert
        cur.execute("INSERT INTO Students(username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        
        # Commit to DB
        mysql.connection.commit()
        return jsonify({'message': 'Student added successfully!'}), 201
    except Exception as e:
        # In case of any exception, rollback the transaction
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close connection
        cur.close()

# Route for adding a new tutor
@app.route('/add_teacher', methods=['POST'])
def add_teacher():
    # Get data from request
    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    # Hash the password for security
    hashed_password = generate_password_hash(password)
    # Create a cursor
    cur = mysql.connection.cursor()
    try:
        # Check for duplicate username or email
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        cur.execute("SELECT * FROM Teachers WHERE username = %s OR email = %s", (username, email))
        if cur.fetchone():
            # Found a duplicate
            return jsonify({'error': 'Username or email already exists.'}), 409

        # No duplicates found, proceed to insert
        cur.execute("INSERT INTO Teachers(username, password, email) VALUES (%s, %s, %s)", (username, password, email))
        
        # Commit to DB
        mysql.connection.commit()
        return jsonify({'message': 'Teacher added successfully!'}), 201
    except Exception as e:
        # In case of any exception, rollback the transaction
        mysql.connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        # Close connection
        cur.close()

@app.route('/delete_account', methods=['POST'])
def delete_account(id='Students'):
    # Extracting username or email from request data
    account_identifier = request.json.get('identifier')  # Could be either username or email

    cur = mysql.connection.cursor()

    # Assuming 'username' and 'email' are in the same table and unique
    sql = ""
    if id == 'Students':
        sql = "DELETE FROM Students WHERE username = %s OR email = %s"
    elif id == 'Teachers':
        sql = "DELETE FROM Teachers WHERE username = %s OR email = %s"
    else:
        return jsonify({'error': 'Invalid account type'}), 400
    # sql = "DELETE FROM Students WHERE username = %s OR email = %s"
    affected_count = cur.execute(sql, (account_identifier, account_identifier))
    mysql.connection.commit()
    cur.close()

    if affected_count:
        return jsonify({'message': 'Account with username/email:{} deleted successfully'.format(account_identifier)}), 200
    else:
        return jsonify({'error': 'Account not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)