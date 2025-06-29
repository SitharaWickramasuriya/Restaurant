from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["yum_yard"]
reservations = db["reservations"]

@app.route("/reserve", methods=["POST"])
def reserve():
    data = request.json
    reservations.insert_one(data)
    return jsonify({"status": "success", "message": "Reservation saved"})

@app.route("/delete", methods=["POST"])
def delete_reservation():
    phone = request.json.get("phone")
    reservations.delete_one({"phone": phone})
    return jsonify({"status": "success", "message": "Reservation deleted"})

@app.route("/admin")
def view_reservations():
    all_reservations = list(reservations.find({}, {"_id": 0}))
    html_template = """
    <html>
    <head>
        <title>Admin - Reservations</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f7f7f7; }
            h1 { color: #444; }
            table { border-collapse: collapse; width: 100%; background: white; }
            th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
            th { background-color: #f0f0f0; }
            button { background-color: #ff4444; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 5px; }
            button:hover { background-color: #dd2222; }
        </style>
        <script>
          async function deleteReservation(phone) {
              if (!confirm("Are you sure you want to delete this reservation?")) return;

              const res = await fetch("/delete", {
                  method: "POST",
                  headers: {
                      "Content-Type": "application/json"
                  },
                  body: JSON.stringify({ phone: phone })
              });

              const result = await res.json();
              alert(result.message);
              location.reload();
          }
        </script>
    </head>
    <body>
        <h1>All Reservations</h1>
        <table>
            <tr>
                <th>Name</th>
                <th>Phone</th>
                <th>People</th>
                <th>Date</th>
                <th>Time</th>
                <th>Message</th>
                <th>Action</th>
            </tr>
            {% for r in reservations %}
            <tr>
                <td>{{ r.name }}</td>
                <td>{{ r.phone }}</td>
                <td>{{ r.person }}</td>
                <td>{{ r.date }}</td>
                <td>{{ r.time }}</td>
                <td>{{ r.message }}</td>
                <td><button onclick="deleteReservation('{{ r.phone }}')">Delete</button></td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    return render_template_string(html_template, reservations=all_reservations)

if __name__ == "__main__":
    app.run(debug=True)
