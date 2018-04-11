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
conn.execute('CREATE TABLE prisoners (id INTEGER PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(255), addr TEXT, city VARCHAR(255), sentence INTEGER, lifetime BOOLEAN, cell_id INTEGER)')
conn.execute('drop table if exists cells')
conn.execute('CREATE TABLE cells (id INTEGER PRIMARY KEY, name VARCHAR(50), size integer)')
cur = conn.cursor()
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Martin", "Novák", "Veselá 36", "Kroměříž", 5, "false", 1 )')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Jan", "Nový", "Jána Amose Komenského 10", "Praha", 1, "false", 3)')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Petr", "Novák", "Křenova 6", "Brno", 2, "false", 1)')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Róbert", "Kaliňák", "Slovákova 28", "Bratislava", NULL, "true", 7)')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Demeter", "Marek", "Cejl 66", "Brno", 2, "false", 5)')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id) VALUES ("Róbert", "Fico", " Bašternáková vila 6", "Bratislava", NULL, "true", 8)')
cur.execute('INSERT INTO cells (name, size) VALUES ("A1", "5")')
cur.execute('INSERT INTO cells (name, size) VALUES ("A2", "5")')
cur.execute('INSERT INTO cells (name, size) VALUES ("B1", "7")')
cur.execute('INSERT INTO cells (name, size) VALUES ("B2", "7")')
cur.execute('INSERT INTO cells (name, size) VALUES ("C1", "9")')
cur.execute('INSERT INTO cells (name, size) VALUES ("C2", "9")')
cur.execute('INSERT INTO cells (name, size) VALUES ("D1", "10")')
cur.execute('INSERT INTO cells (name, size) VALUES ("D2", "10")')
conn.commit()
print("Table created successfully");
conn.close()


@app.route("/")
def index():
    prisoners = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("select * from prisoners p JOIN cells c ON p.cell_id = c.id")

    prisoners = cur.fetchall()
    con.close()
    return render_template("index.html", prisoners=prisoners)

@app.route("/cells")
def cellindex():
    cells = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT c.id, c.name as name, c.size as size, p.pocet as persons, CAST(c.size as real)/CAST(p.pocet as real) as personsize from cells c LEFT OUTER JOIN (SELECT cell_id, count(cell_id) as pocet FROM prisoners GROUP BY cell_id) p ON c.id = p.cell_id")

    cells = cur.fetchall()
    con.close()
    return render_template("cells.html", cells=cells)

@app.route("/abccells")
def abccellsindex():
    prisoners = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM prisoners p JOIN cells c ON p.cell_id = c.id ORDER BY c.name" )

    prisoners = cur.fetchall()
    con.close()
    return render_template("abccells.html", prisoners=prisoners)

@app.route("/abcprisoners")
def abcprisonersindex():
    prisoners = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM prisoners p JOIN cells c ON p.cell_id = c.id ORDER BY p.last_name, p.first_name" )

    prisoners = cur.fetchall()
    con.close()
    return render_template("abcprisoners.html", prisoners=prisoners)

@app.route("/cell/<cell_id>")
def cell_detail(cell_id):
    con = connect_db()
    msg = None
    cur = con.cursor()
    cur.execute(("select * from cells where id = ?;"), cell_id)
    cells = cur.fetchall()
    cell = cells[0]
    cur.execute(("select first_name, last_name from prisoners where cell_id = ?;"), (cell_id))

    prisoners = cur.fetchall()
    con.close()

    if not len(prisoners):
        msg = "Cela nie je obsadená."
    return render_template("cell_detail.html", prisoners=prisoners, cell=cell, msg=msg)


@app.route("/prisoners/new")
def new():
    return render_template("form.html")


@app.route("/prisoner/<prisoner_id>")
def detail(prisoner_id):
    con = connect_db()
    msg = None
    cur = con.cursor()
    cur.execute("select * from prisoners p JOIN cells c ON p.cell_id = c.id where p.id = ?;", (prisoner_id))
    prisoners = cur.fetchall()
    prisoner = prisoners[0]
    cell_name = prisoner["name"]
    cell_id = str(prisoner["cell_id"])

    cur.execute("select first_name, last_name from prisoners where cell_id = ? AND id != ? ;", (cell_id, prisoner_id))

    roommates = cur.fetchall()
    con.close()

    if not len(roommates):
        msg = "Väzeň je na cele sám."
    return render_template("detail.html", prisoner=prisoner, cell_name=cell_name, roommates=roommates, msg=msg)


@app.route("/search", methods=["POST"])
def search():
    if  request.method == 'POST':
        search = request.form['search']
        query = "SELECT * FROM prisoners p JOIN cells c ON p.cell_id = c.id WHERE p.first_name LIKE '%%%s%%' OR p.last_name  LIKE '%%%s%%' OR c.name LIKE '%%%s%%'" % (search, search, search)

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
            sentence = request.form['sentence']
            lifetime = request.form.getlist('lifetime')
            cell_id = request.form['cell_id']



            if lifetime:
                print("Lifetime: " + lifetime[0])
                if lifetime[0] == "on":
                    lifetime[0] = "true"
            else:
                lifetime = ["false"]

            with connect_db() as con:
                cur = con.cursor()
                cur.execute(
                    "INSERT INTO prisoners (first_name, last_name, city, addr, sentence, lifetime, cell_id) VALUES (?,?,?,?,?,?,?)",
                    (fn, ln, city, addr, sentence, lifetime[0], cell_id))

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
            sentence = request.form['sentence']
            lifetime = request.form.getlist('lifetime')
            cell_id = request.form['cell_id']

            with connect_db() as con:
                cur = con.cursor()

                lifetime_mates = 0
                if lifetime:
                    if lifetime[0] == "on":
                        lifetime[0] = "true"
                    cur.execute("SELECT * FROM prisoners WHERE cell_id = ? AND lifetime = 'true' AND id != ?;", (cell_id, prisoner_id))
                    lifetime_mates = len(cur.fetchall())
                else:
                    lifetime = ["false"]


                if lifetime_mates == 0:
                    cur.execute(
                        "UPDATE prisoners SET first_name = ?, last_name = ?, city = ?, addr = ?, sentence = ?, lifetime = ?, cell_id = ? WHERE id = ?",
                        (fn, ln, city, addr, sentence, lifetime[0], cell_id, prisoner_id))
                    con.commit()
                    msg = "Record successfully updated"
                else:
                    msg = "Do tejto cely nie je možné priradiť ďalšieho väzňa na doživotie!!!"



        except Exception as ex:
            print(ex)
            con.rollback()
            msg = "error in update operation"

        finally:
            #return render_template("form.html", msg = msg)
            cur.execute("select * from prisoners where id = ?", (prisoner_id))
            prisoners = cur.fetchall()
            prisoner = prisoners[0]
            return render_template("form.html", prisoner=prisoner, msg=msg)
            #return redirect(url_for("edit"))
            con.close()


@app.route("/prisoner/<prisoner_id>/delete")
def delete(prisoner_id):
    con = connect_db()
    cur = con.cursor()
    cur.execute("DELETE FROM prisoners where id = ?", (prisoner_id))
    con.commit()
    con.close()
    return redirect(url_for("index"))

@app.route("/statistics")
def statisticsindex():
    statistics = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("select a.persons as persons, b.cells as cells, b.allsize as allsize, CAST(b.allsize as real)/CAST(a.persons as real) as personsize from (select count(*) as persons from prisoners) a, (select count(*) as cells, sum(size) as allsize from cells) b")

    statistics = cur.fetchall()
    con.close()
    return render_template("statistics.html", statistics=statistics)

if __name__ == "__main__":
    app.run()
