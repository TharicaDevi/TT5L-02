from flask import Flask, render_template, request
from database import init_db, get_all_pets, filter_pets, get_pet_by_id

app = Flask(__name__)
init_db()

@app.route('/')
def homepage():
    breed = request.args.get('breed')
    age = request.args.get('age')

    if breed or age:
        pets = filter_pets(breed=breed, age=age)
    else:
        pets = get_all_pets()

    return render_template('homepage.html', pets=pets)

@app.route('/pet/<int:pet_id>')
def pet_profile(pet_id):
    pet = get_pet_by_id(pet_id)
    if not pet:
        return "Pet not found", 404
    return render_template('pet_profile.html', pet=pet)

if __name__ == '__main__':
    app.run(debug=True)
