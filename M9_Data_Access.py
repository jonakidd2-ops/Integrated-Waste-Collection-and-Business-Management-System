import sqlite3
from contextlib import contextmanager
#this creates the table needed for the system to work; its SQL commands; #SCHEMA was Generated using AI
SCHEMA = """ 
CREATE TABLE IF NOT EXISTS trucks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, full_name TEXT NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL, truck_id INTEGER REFERENCES trucks(id));
CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, contact TEXT);
CREATE TABLE IF NOT EXISTS parts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, part_type TEXT NOT NULL,
  unit_cost REAL NOT NULL, supplier_id INTEGER REFERENCES suppliers(id));
CREATE TABLE IF NOT EXISTS parts_orders (
  id INTEGER PRIMARY KEY AUTOINCREMENT, order_date TEXT NOT NULL, status TEXT NOT NULL,
  total REAL NOT NULL, supplier_id INTEGER REFERENCES suppliers(id), created_by INTEGER REFERENCES users(id));
CREATE TABLE IF NOT EXISTS order_lines (
  id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL REFERENCES parts_orders(id) ON DELETE CASCADE,
  part_id INTEGER NOT NULL REFERENCES parts(id), quantity INTEGER NOT NULL, unit_cost REAL NOT NULL);
CREATE TABLE IF NOT EXISTS documents (
  id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, doc_type TEXT NOT NULL, description TEXT,
  filename TEXT NOT NULL, content BLOB NOT NULL, uploaded_by INTEGER REFERENCES users(id), uploaded_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL UNIQUE, contact TEXT);
CREATE TABLE IF NOT EXISTS collections (
  id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL REFERENCES customers(id),
  address TEXT NOT NULL, date TEXT NOT NULL, start_time TEXT NOT NULL, end_time TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'Scheduled', truck_id INTEGER REFERENCES trucks(id));
CREATE TABLE IF NOT EXISTS contracts (
  id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL REFERENCES customers(id),
  details TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  document_id INTEGER REFERENCES documents(id) ON DELETE SET NULL);
"""

TABLES = {"users", "trucks", "suppliers", "parts", "parts_orders", "order_lines",
          "documents", "customers", "collections", "contracts"} #these are all the tables in the database
                                                                #database operartion can only access these

class Database: #class with all the function to interact with database; other modules should use this
    def __init__(self, path=":memory:"): #activates when a database objecct is created, database is stored temp in memory
        self.path = path
        # autocommit mode; transactions are explicit (see transaction())
        self.conn= sqlite3.connect(path, isolation_level=None) #establishes the connection with the database
        self.conn.row_factory= sqlite3.Row #allows for db results to be access with coloumn names as well ie.row["username"] or row[1]
        self.conn.execute("PRAGMA foreign_keys = ON")#makes sure relationship between tables are maintained
        self.conn.executescript(SCHEMA)#this just executes the SQL commands in the SCHEMA
        self._columns={t: [r["name"] for r in self.conn.execute(f"PRAGMA table_info({t})")] for t in TABLES}#retrieves and stores the coloumn name for each table

    #generic operations(use these according to your needs when writing: find, save, remove, store_file, get_file....)
    def _check(self, table, names=()):#validation to make sure table and colomn exist before acting
        if table not in TABLES:      #ie.  self._check("users", ["username"]); checks if the user table and cloumn exists.
            raise ValueError(f"unknown table {table}")
        for n in names:
            if n not in self._columns[table]:
                raise ValueError(f"unknown column {n} in {table}")

    def find(self, table, **criteria): #searches for a record in a table; **criteria is used so we can use different search condition
        self._check(table, criteria)   #ie. db.find("users", username="admin"); this looks in the user table to find a username "admin"
        where= " AND ".join(f"{k} = ?" for k in criteria)
        sql= f"SELECT * FROM {table}"+(f" WHERE {where}" if where else "")+ " ORDER BY id"
        return [dict(r) for r in self.conn.execute(sql, tuple(criteria.values()))]

    def get(self, table, row_id): #retirves a singular record using it's ID
        rows=self.find(table, id=row_id) #ie. db.get("users", 1); gets the users ID is 1
        return rows[0] if rows else None

    def save(self, table, record): #insert new records or upadtes ones that already exist
        self._check(table, record)
        record= dict(record) #copies a record into a dic
        row_id= record.pop("id", None) #rmoves id from dic and stores it in row_id
        if row_id is None:#if id doesn't exists, treats it as a new record and gens an ID
            cols= ", ".join(record)
            marks= ", ".join("?" for _ in record)
            cur=self.conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({marks})", tuple(record.values()))
            return cur.lastrowid
        sets= ", ".join(f"{k} = ?" for k in record)#if id exists upadtes the record with the supllied info
        self.conn.execute(f"UPDATE {table} SET {sets} WHERE id = ?", tuple(record.values()) + (row_id,))
        return row_id

    def remove(self, table, row_id):#use to delete a record form a specific table using its ID
        self._check(table)          #ie. db.remove("users", 3); deletes the user who's ID is 3
        self.conn.execute(f"DELETE FROM {table} WHERE id = ?", (row_id,))

    def store_file(self, content: bytes, details: dict): #stores uplaoded documents in the database
        """Store an uploaded file in the database next to its details (one backup covers both)."""
        return self.save("documents", {**details, "content": content}) #combine document detail with 

    def get_file(self, doc_id): #search for a document using its ID returns the filename and contents; else None
        row = self.conn.execute("SELECT filename, content FROM documents WHERE id = ?", (doc_id,)).fetchone()
        return (row["filename"], bytes(row["content"])) if row else None

    #queries with joins
    def query(self, sql, params=()): #allows other modules to execute custom SQL SELECT queries
        return [dict(r) for r in self.conn.execute(sql, params)] #ie. db.query("SELECT * FROM users") allows complicated queries like JOIN operations

    def execute(self, sql, params=()):#carries out a custom SQL statement then return the last inserted row id
        return self.conn.execute(sql, params).lastrowid   #db.execute("INSERT INTO trucks (name) VALUES (?)", ("Truck 1",))          

    
    #this function transaction() was written with the assitance of AI
    @contextmanager
    def transaction(self):
        """All-or-nothing block; BEGIN IMMEDIATE stops two users saving conflicting changes at once."""  #
        self.conn.execute("BEGIN IMMEDIATE")                                                             #
        try:                                                                                             #
            yield self
        except BaseException:
            self.conn.execute("ROLLBACK")
            raise
        else:
            self.conn.execute("COMMIT")

    def close(self): #this is just closing the database connection
        self.conn.close()
