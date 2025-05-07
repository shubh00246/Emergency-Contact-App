from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from firebase_config import contacts_ref
from twilio.rest import Client

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = "replace-with-a-secure-random-key"

# Twilio credentials
TWILIO_SID   = "ACe98f77389f77f88c8761a08663a2d4e7"
TWILIO_TOKEN = "e36d6d5df21e4d3d225c4124ff39af3f"
TWILIO_FROM  = "+14787778389"
client = Client(TWILIO_SID, TWILIO_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        relation = request.form.get("relation", "").strip()
        if not (name and phone and relation):
            flash("All fields are required", "danger")
            return redirect(url_for("add"))
        contacts_ref.push({"name": name, "phone": phone, "relation": relation})
        flash("Contact added!", "success")
        return redirect(url_for("contacts"))
    return render_template("add.html")

@app.route("/contacts")
def contacts():
    data = contacts_ref.get() or {}
    return render_template("contacts.html", contacts=data)

@app.route("/edit/<contact_id>", methods=["GET", "POST"])
def edit(contact_id):
    contact = contacts_ref.child(contact_id).get()
    if not contact:
        flash("Contact not found.", "danger")
        return redirect(url_for("contacts"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        relation = request.form.get("relation", "").strip()

        if not (name and phone and relation):
            flash("All fields are required.", "danger")
            return redirect(url_for("edit", contact_id=contact_id))

        contacts_ref.child(contact_id).update({
            "name": name,
            "phone": phone,
            "relation": relation
        })
        flash("Contact updated!", "success")
        return redirect(url_for("contacts"))

    return render_template("edit.html", contact=contact, contact_id=contact_id)

@app.route("/alert", methods=["POST"])
def alert():
    contacts = contacts_ref.get()
    if not contacts:
        return jsonify({"status": "error", "message": "No contacts to alert!"}), 400

    data = request.get_json()
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if not latitude or not longitude:
        return jsonify({"status": "error", "message": "Location not provided"}), 400

    location_link = f"https://maps.google.com/?q={latitude},{longitude}"

    for contact_id, contact in contacts.items():
        to_number = contact.get("phone")
        name = contact.get("name")
        relation = contact.get("relation")
        if to_number:
            client.messages.create(
                body=f"Emergency! {name} ({relation}) needs help. Location: {location_link}",
                from_=TWILIO_FROM,
                to=to_number
            )

    return jsonify({"status": "success", "message": "Alert messages sent successfully!"})

if __name__ == "__main__":
    app.run(debug=True)
