import os
import sqlite3

from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)
sortByDB = False

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
conn.execute('CREATE TABLE prisoners (id INTEGER PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(255), addr TEXT, city VARCHAR(255), sentence INTEGER, lifetime BOOLEAN, cell_id INTEGER, phone TEXT(20))')
conn.execute('drop table if exists cells')
conn.execute('CREATE TABLE cells (id INTEGER PRIMARY KEY, name VARCHAR(50), size integer)')
conn.execute('drop table if exists regions')
conn.execute('CREATE TABLE regions (id INTEGER PRIMARY KEY, name VARCHAR(50), prefix TEXT(20), country VARCHAR(50))')
cur = conn.cursor()
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Martin", "Novák", "Veselá 36", "Kroměříž", 5, "false", 1, "+420573323398")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Jan", "Nový", "Jána Amose Komenského 10", "Praha", 1, "false", 3,"+420234694111")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Petr", "Novák", "Křenova 6", "Brno", 2, "false", 1, "+420542173530")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Róbert", "Kaliňák", "Slovákova 28", "Bratislava", NULL, "true", 7, "+421268272200")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Demeter", "Marek", "Cejl 66", "Brno", 2, "false", 5, "")')
cur.execute('INSERT INTO prisoners (first_name, last_name, addr, city, sentence, lifetime, cell_id, phone) VALUES ("Róbert", "Fico", " Bašternáková vila 6", "Bratislava", NULL, "true", 8, "+421268272111")')
cur.execute('INSERT INTO cells (name, size) VALUES ("A1", "5")')
cur.execute('INSERT INTO cells (name, size) VALUES ("A2", "5")')
cur.execute('INSERT INTO cells (name, size) VALUES ("B1", "7")')
cur.execute('INSERT INTO cells (name, size) VALUES ("B2", "7")')
cur.execute('INSERT INTO cells (name, size) VALUES ("C1", "9")')
cur.execute('INSERT INTO cells (name, size) VALUES ("C2", "9")')
cur.execute('INSERT INTO cells (name, size) VALUES ("D1", "10")')
cur.execute('INSERT INTO cells (name, size) VALUES ("D2", "10")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Kroměříž", "+420573", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Praha", "+4202", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Brno", "+420542", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Bratislava", "+4212", "SR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Prostějov", "+420582", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Vsetín", "+420571", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Ostrava", "+420599", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Olomouc", "+420585", "ČR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Košice", "+42155", "SR")')
cur.execute('INSERT INTO regions (name, prefix, country) VALUES ("Prešov", "+42151", "SR")')
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

    sortByDB = False
    if (sortByDB):
        print("Sorted by DB")
        cur.execute("SELECT c.id, c.name as name, c.size as size, p.pocet as persons, CAST(c.size as real)/CAST(p.pocet as real) as personsize from cells c LEFT OUTER JOIN (SELECT cell_id, count(cell_id) as pocet FROM prisoners GROUP BY cell_id) p ON c.id = p.cell_id")
        cells = cur.fetchall()

    else:
        print("Sorted by App")
        cur.execute("SELECT id, name, size from cells")
        db_cells = cur.fetchall()
        cur.execute("SELECT id, cell_id, count(cell_id) as persons FROM prisoners GROUP BY cell_id ")
        prisoners = cur.fetchall()

        n = len(db_cells)
        cells = [[0] * n for i in range(n)]
        for i in range(len(db_cells)):
            cells[i][0] = db_cells[i]["id"]
            cells[i][1] = db_cells[i]["name"]
            cells[i][2] = db_cells[i]["size"]
            for j in range(len(prisoners)):
                if prisoners[j]["cell_id"] == db_cells[i]["id"]:
                    cells[i][3] = prisoners[j]["persons"]
            if cells[i][3] > 0:
               cells[i][4] = cells[i][2] / cells[i][3]
            else:
                cells[i][4] = 0

    con.close()
    return render_template("cells.html", cells=cells)

@app.route("/abccells")
def abccellsindex():
    prisoners = []
    cells = []
    con = connect_db()
    cur = con.cursor()

    sortByDB = False
    if (sortByDB):
        print("Sorted by DB")
        cur.execute("SELECT p.id, p.first_name, p.last_name, c.name FROM prisoners p JOIN cells c ON p.cell_id = c.id ORDER BY c.name" )
        prisoners = cur.fetchall()
    else:
        print("Sorted by App")
        cur.execute("select id, first_name, last_name, cell_id from prisoners")
        db_prisoners = cur.fetchall()
        cur.execute("SELECT id, name FROM cells" )
        cells = cur.fetchall()

        n = len(db_prisoners)
        prisoners = [[0] * n for i in range(n)]
        for i in range(len(db_prisoners)):
            for j in range(len(cells)):
                if db_prisoners[i]["cell_id"] == cells[j]["id"]:
                    prisoners[i][0] = db_prisoners[i]["id"]
                    prisoners[i][1] = db_prisoners[i]["first_name"]
                    prisoners[i][2] = db_prisoners[i]["last_name"]
                    prisoners[i][3] = cells[j]["name"]
        prisoners.sort(key=lambda x:(x[3], x[2], x[1]))

    con.close()
    return render_template("abccells.html", prisoners=prisoners)

@app.route("/abcprisoners")
def abcprisonersindex():
    prisoners = []
    cells = []
    con = connect_db()
    cur = con.cursor()

    if (sortByDB):
        print("Sorted by DB")
        cur.execute("SELECT p.id, p.first_name, p.last_name, c.name FROM prisoners p JOIN cells c ON p.cell_id = c.id ORDER BY p.last_name, p.first_name" )
        prisoners = cur.fetchall()
    else:
        print("Sorted by App")
        cur.execute("select id, first_name, last_name, cell_id from prisoners")
        db_prisoners = cur.fetchall()
        cur.execute("SELECT id, name FROM cells" )
        cells = cur.fetchall()

        n = len(db_prisoners)
        prisoners = [[0] * n for i in range(n)]
        for i in range(len(db_prisoners)):
            for j in range(len(cells)):
                if db_prisoners[i]["cell_id"] == cells[j]["id"]:
                    prisoners[i][0] = db_prisoners[i]["id"]
                    prisoners[i][1] = db_prisoners[i]["first_name"]
                    prisoners[i][2] = db_prisoners[i]["last_name"]
                    prisoners[i][3] = cells[j]["name"]
        prisoners.sort(key=lambda x:(x[2], x[1]))

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
            phone = request.form['phone']
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
                    "INSERT INTO prisoners (first_name, last_name, city, addr, sentence, lifetime, cell_id, phone) VALUES (?,?,?,?,?,?,?,?)",
                    (fn, ln, city, addr, sentence, lifetime[0], cell_id, phone))

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
            phone = request.form['phone']
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
                        "UPDATE prisoners SET first_name = ?, last_name = ?, city = ?, addr = ?, phone = ?, sentence = ?, lifetime = ?, cell_id = ? WHERE id = ?",
                        (fn, ln, city, addr, phone, sentence, lifetime[0], cell_id, prisoner_id))
                    con.commit()
                    msg = "Record successfully updated"
                else:
                    msg = "Do tejto cely nie je možné priradiť ďalšieho väzňa na doživotie!!!"

        except Exception as ex:
            print(ex)
            con.rollback()
            msg = "error in update operation"

        finally:

            cur.execute("select * from prisoners where id = ?", (prisoner_id))
            prisoners = cur.fetchall()
            prisoner = prisoners[0]
            return render_template("form.html", prisoner=prisoner, msg=msg)
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

    if(sortByDB):
        cur.execute("select a.persons as persons, b.cells as cells, b.allsize as allsize, CAST(b.allsize as real)/CAST(a.persons as real) as personsize from (select count(*) as persons from prisoners) a, (select count(*) as cells, sum(size) as allsize from cells) b")
        statistics = cur.fetchall()
    else:
        print("Sorted by App")
        cur.execute("select id, first_name, last_name, cell_id from prisoners")
        prisoners = cur.fetchall()
        cur.execute("SELECT id, name, size FROM cells" )
        cells = cur.fetchall()

        persons = len(prisoners)
        statistics = [[0] * persons for i in range(1)]
        statistics[0][0] = persons
        statistics[0][1] = len(cells)
        sum = 0
        for i in range(len(cells)):
            sum += cells[i]["size"]
        statistics[0][2] = sum
        statistics[0][3] = sum / persons

    con.close()
    return render_template("statistics.html", statistics=statistics)

@app.route("/call_prefix")
def call_prefix():
    prisoners = []
    regions = []
    call_prefix = []
    con = connect_db()
    cur = con.cursor()
    cur.execute("select * from regions")
    regions = cur.fetchall()
    cur.execute("select phone from prisoners")
    prisoners = cur.fetchall()

    for i in range(len(regions)):
        for j in range(len(prisoners)):
            phone = prisoners[j]["phone"]
            if regions[i]["prefix"] in phone:
                row = [0,2]
                row[0] = regions[i]["name"]
                row[1] =  regions[i]["prefix"]
#                print(row[0])
#                print(row[1])
                call_prefix.append(row)
                break

    con.close()
    return render_template("call_prefix.html", call_prefix=call_prefix)

if __name__ == "__main__":
    app.run()
