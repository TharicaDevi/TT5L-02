from flask import Flask, render_template, request, redirect, url_for
from petsdatabase import init_db, get_all_pets, get_pet_by_id, filter_pets

app = Flask(__name__)
init_db()

@app.route('/')
def home():
    pets = get_all_pets()
    return render_template("homepage.html", pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_profile(pet_id):
    pet = get_pet_by_id(pet_id)
    return render_template("pet_profile.html", pet=pet)

@app.route('/filter', methods=['POST'])
def filter():
    breed = request.form.get("breed")
    age = request.form.get("age")
    pets = filter_pets(breed, age)
    return render_template("homepage.html", pets=pets)

if __name__ == '__main__':
    app.run(debug=True)
