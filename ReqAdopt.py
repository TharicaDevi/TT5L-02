from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
from petsdatabase import init_db, add_adoption_request, get_all_pets

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize DB
init_db()

@app.route('/')
def adoption_form():
    return render_template('request.html')

@app.route('/submit-request', methods=['POST'])
def submit_request():
    # Dummy user_id and pet_id for demonstration (replace with actual login system + selected pet)
    user_id = 1
    pet_id = 1

    # Extract form data
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    pet_type = request.form.get('pet-type')
    reason = request.form.get('reason')
    living = request.form.get('living')
    agree = request.form.get('agree')

    if not all([fullname, email, phone, address, pet_type, reason, living, agree]):
        flash("Please fill out all required fields.")
        return redirect(url_for('request'))

    message = f"Full Name: {fullname}\nEmail: {email}\nPhone: {phone}\nAddress: {address}\n" \
              f"Pet Type: {pet_type}\nReason: {reason}\nLiving Situation: {living}"

    add_adoption_request(user_id=user_id, pet_id=pet_id, message=message)
    flash("Your adoption request has been submitted successfully!")
    return redirect(url_for('request'))

if __name__ == '__main__':
    app.run(debug=True)