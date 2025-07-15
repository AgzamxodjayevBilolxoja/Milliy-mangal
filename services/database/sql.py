create_table_user = """
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id INTEGER UNIQUE NOT NULL,
lang VARCHAR NOT NULL,
phone VARCAHR(20) NOT NULL,
name VARCHAR(32) NOT NULL
)
"""

create_user = """
INSERT INTO users(chat_id, lang, phone, name)
VALUES(?, ?, ?, ?)
"""

check_user = """
SELECT * FROM users WHERE chat_id=?
"""

change_name = """
UPDATE users SET name=? WHERE chat_id=? 
"""

change_phone = """
UPDATE users SET phone=? WHERE chat_id=? 
"""

change_lang = """
UPDATE users SET lang=? WHERE chat_id=? 
"""

create_table_rating = """
CREATE TABLE IF NOT EXISTS ratings(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
rating VARCHAR NOT NULL,
comment VARCHAR
)
"""

create_rating = """
INSERT INTO ratings(user_id, rating, comment)
VALUES (?, ?, ?)
"""

create_table_branhes = """
CREATE TABLE IF NOT EXISTS branches(
id INTEGER PRIMARY KEY AUTOINCREMENT,
latitude FLOAT NOT NULL UNIQUE,
longitude FLOAT NOT NULL UNIQUE,
name VARCHAR NOT NULL UNIQUE,
opening_time VARCHAR NOT NULL
)
"""

create_branch = """
INSERT INTO branches(latitude, longitude, name)
VALUES(?, ?, ?)
"""

get_branches = """
SELECT * FROM branches
"""

create_table_staff = """
CREATE TABLE IF NOT EXISTS staff(
id INTEGER PRIMARY KEY AUTOINCREMENT,
chat_id INTEGER UNIQUE,
role VARCHAR NOT NULL,
password VARCHAR NOT NULL UNIQUE
)
"""

create_staff = """
INSERT INTO staff(role, password)
VALUES(?, ?)
"""

check_staff = """
SELECT * FROM staff WHERE role=? AND password=?
"""

update_staff = """
UPDATE staff SET chat_id=? WHERE role=? AND password=?
"""

check_staff_by_chat_id = """
SELECT * FROM staff WHERE chat_id=?
"""

get_staffs = """
SELECT chat_id FROM staff WHERE role=?
"""

add_branch = """
INSERT INTO branches(latitude, longitude, name, opening_time)
VALUES(?, ?, ?, ?)
"""

get_branches = """
SELECT name FROM branches
"""

get_branch_by_name = """
SELECT * FROM branches WHERE name=?
"""

update_location_branch = """
UPDATE branches SET latitude=? AND longitude=? WHERE id=?
"""

update_name_branch = """
UPDATE branches SET name=? WHERE id=?
"""

update_time_branch = """
UPDATE branches SET opening_time=? WHERE id=?
"""

delete_branch = """
DELETE FROM branches WHERE id=?
"""