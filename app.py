import os
import sqlite3

from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'prison.db')
))

def connect_db():
    """Connects to the specific database."""
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


conn = sqlite3.connect(app.config['DATABASE'])
print("Opened database successfully");
conn.execute('drop table if exists prisoners')
conn.execute('CREATE TABLE prisoners (id INTEGER PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(255), addr TEXT, city VARCHAR(255))')
cur = conn.cursor()
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city) VALUES ("Martin", "Novák", "Veselá 36", "Kroměříž")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city) VALUES ("Jan", "Nový", "Jána Amose Komenského 10", "Praha")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city) VALUES ("Petr", "Novák", "Křenova 6", "Brno")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city) VALUES ("Dezider", "Čonka", "Slovákova 28", "Námestovo")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city) VALUES ("Demeter", "Marek", "Cejl 66", "Brno")')
conn.commit()
print("Table created successfully");
conn.close()


@app.route("/")
def index():
    prisoners = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("select * from prisoners")

    prisoners = cur.fetchall()
    con.close()
    return render_template("index.html", prisoners=prisoners)



@app.route("/prisoners/new")
def new():
    return render_template("form.html")


@app.route("/prisoner/<prisoner_id>")
def detail(prisoner_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("select * from prisoners where id = ?", (prisoner_id))

    prisoners = cur.fetchall()
    prisoner = prisoners[0]
    con.close()
    return render_template("detail.html", prisoner=prisoner)


@app.route("/search", methods=["POST"])
def search():
    if  request.method == 'POST':
        search = request.form['search']
        query = "SELECT * FROM prisoners WHERE last_name LIKE '%%%s%%'" % (search)

        con = connect_db()
        cur = con.cursor()
        cur.execute(query)

        prisoners = cur.fetchall()
        con.close()

    return render_template("index.html", prisoners=prisoners)

@app.route("/prisoner/<prisoner_id>/edit")
def edit(prisoner_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("select * from prisoners where id = ?", (prisoner_id))

    prisoners = cur.fetchall()
    prisoner = prisoners[0]
    con.close()
    return render_template("form.html", prisoner=prisoner)


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == 'POST':
        try:
            fn = request.form['first_name']
            ln = request.form['last_name']
            city = request.form['city']
            addr = request.form['addr']

            with connect_db() as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO prisoners (first_name, last_name, city, addr) VALUES (?,?,?,?)",
                    (fn, ln, city, addr))

                con.commit()
                msg = "Record successfully added"
        except Exception as ex:
            print(ex)
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("form.html", msg = msg)
            con.close()


@app.route("/prisoner/<prisoner_id>/update", methods=['POST'])
def update(prisoner_id):
    if request.method == 'POST':
        try:
            fn = request.form['first_name']
            ln = request.form['last_name']
            city = request.form['city']
            addr = request.form['addr']

            with connect_db() as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE prisoners SET first_name = ?, last_name = ?, city = ?, addr = ? WHERE id = ?",
                    (fn, ln, city, addr, prisoner_id))

                con.commit()
                msg = "Record successfully updated"
        except Exception as ex:
            print(ex)
            con.rollback()
            msg = "error in update operation"

        finally:
            return render_template("form.html", msg = msg)
            con.close()


@app.route("/prisoner/<prisoner_id>/delete")
def delete(prisoner_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM prisoners where id = ?", (prisoner_id))
    con.commit()
    con.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run()
