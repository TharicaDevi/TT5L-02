import database

def seed_pets():
    database.insert_pet("Milo", "dog1.jpeg", "Dog", "Golden", "Golden Retriever", 1, "available")
    database.insert_pet("Snowy", "cat1.jpeg", "Cat", "White", "Persian", 2, "available")
    database.insert_pet("Hammy", "hamster1.jpeg", "Hamster", "Brown", "Roborovski Dwarf", 2, "available")
    database.insert_pet("Oyen", "cat2.jpeg", "Cat", "Orange", "Persian", 4, "available")
    database.insert_pet("Xixi", "cat3.jpeg", "Cat", "Grey", "Persian", 1, "available")
    database.insert_pet("Spike", "dog2.jpeg", "Dog", "Calico", "Chihuahua", 3, "available")
    database.insert_pet("Tabby", "cat4.jpeg", "Cat", "Seal point", "Siamese", 1, "available")
    database.insert_pet("Sam", "hamster2.jpeg", "Hamster", "Orange", "Syrian hamster", 1, "available")

if __name__ == "__main__":
    seed_pets()