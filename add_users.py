import logging
from db import init_db, add_user
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

init_db()

users = [
    {"username": "12345678", "password": "password123"},
    {"username": "87654321", "password": "pass456"},
    {"username": "344", "password": "mypassword"},
    # add more users here
]

def export_users_to_csv(users, filename='user_logins_backup.csv'):
    import csv
    from werkzeug.security import generate_password_hash
    try:
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['username', 'password_hash']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for user in users:
                writer.writerow({
                    'username': user['username'],
                    'password_hash': generate_password_hash(user['password'], method='pbkdf2:sha256')
                })
        logging.info(f'User login info exported to {filename}')
    except Exception as e:
        logging.error(f'Failed to export users to CSV: {e}')

added_count = 0
exists_count = 0

for user in users:
    try:
        if add_user(user["username"], user["password"]):
            logging.info(f'User {user["username"]} added.')
            added_count += 1
        else:
            logging.warning(f'User {user["username"]} already exists.')
            exists_count += 1
    except Exception as e:
        logging.error(f'Error adding user {user["username"]}: {e}')

logging.info(f'Total users processed: {len(users)}')
logging.info(f'Users added: {added_count}')
logging.info(f'Users already existed: {exists_count}')

export_users_to_csv(users)

# Debug script: Print all forms in the exception_forms table
with sqlite3.connect('forms.db', timeout=10) as conn:
    c = conn.cursor()
    c.execute('SELECT * FROM exception_forms')
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description]
    print(f"Found {len(rows)} forms in exception_forms table:")
    for row in rows:
        form = dict(zip(columns, row))
        print(form)