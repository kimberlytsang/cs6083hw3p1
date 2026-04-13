from flask import Flask, render_template, request
import psycopg2

app = Flask(__name__)

# pgadmin4 credentials
def get_connection():
    return psycopg2.connect(
        dbname="hw2p2",
        user="postgres",
        password="Castlepeak12",
        host="localhost",
        port="5432"
    )

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    source = request.form["source"]
    dest = request.form["dest"]
    start_date = request.form["start_date"]
    end_date = request.form["end_date"]

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT fs.flight_number,
               f.departure_date,
               fs.origin_code,
               fs.dest_code,
               fs.departure_time
        FROM FlightService fs
        JOIN Flight f
          ON fs.flight_number = f.flight_number
        WHERE fs.origin_code = %s
          AND fs.dest_code = %s
          AND f.departure_date BETWEEN %s AND %s
        ORDER BY f.departure_date, fs.departure_time, fs.flight_number;
    """

    cur.execute(query, (source, dest, start_date, end_date))
    flights = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("results.html", flights=flights)


@app.route("/flight/<flight_number>/<departure_date>")
def flight_details(flight_number, departure_date):
    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT f.flight_number,
               f.departure_date,
               a.capacity,
               a.capacity - COUNT(b.pid) AS available_seats
        FROM Flight f
        JOIN Aircraft a
          ON f.plane_type = a.plane_type
        LEFT JOIN Booking b
          ON b.flight_number = f.flight_number
         AND b.departure_date = f.departure_date
        WHERE f.flight_number = %s
          AND f.departure_date = %s
        GROUP BY f.flight_number, f.departure_date, a.capacity;
    """

    cur.execute(query, (flight_number, departure_date))
    flight = cur.fetchone()

    cur.close()
    conn.close()

    return render_template("details.html", flight=flight)


if __name__ == "__main__":
    app.run(debug=True)