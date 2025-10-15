import json
import sqlite3

conn = sqlite3.connect('mealdb.sqlite')
cur = conn.cursor()

# Do some setup
cur.executescript('''
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS recipe_ingredients;
                  
CREATE TABLE Recipes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT UNIQUE,
    instructions_link TEXT,
    calories REAL,
    protein REAL,
    carbs REAL,
    fat REAL
);

CREATE TABLE Ingredient (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE
);

CREATE TABLE recipe_ingredients (
    recipe_id   INTEGER,
    ingredient_id   INTEGER,
    PRIMARY KEY (recipe_id, ingredient_id)              
)
''')

fname = 'recipes.json'
str_data= open(fname).read()
json_data = json.loads(str_data)

for entry in json_data["Recipes"]:
    name = entry["name"]
    link = entry["instructions link"]
    calories = entry["macros"]["calories"]
    protein = entry["macros"]["protein"]
    carbs = entry["macros"]["carbs"]
    fat = entry["macros"]["fat"]
    ingredients = entry["ingredients"]

    cur.execute('''INSERT OR IGNORE INTO Recipes (name, instructions_link, calories, protein, carbs, fat)
        VALUES ( ?, ?, ?, ?, ?, ? )''', 
        (name, link, calories, protein, carbs, fat) )
    cur.execute('SELECT id FROM Recipes WHERE name = ? ', (name, ))
    recipe_id = cur.fetchone()[0]

    for ing in ingredients:
        cur.execute('INSERT OR IGNORE INTO Ingredient (name) VALUES (?)', (ing,))
        cur.execute('SELECT id FROM Ingredient WHERE name = ?', (ing,))
        ingredient_id = cur.fetchone()[0]

        cur.execute('''INSERT OR IGNORE INTO Recipe_Ingredients
            (recipe_id, ingredient_id) VALUES (?, ?)''',
            (recipe_id, ingredient_id)
        )
    conn.commit()

conn.close()

def get_user_pantry():
    print("When inputting your pantry items, separate each with a comma.")
    print("Common household items (salt, oil, spices) are automatically included.\n")

    proteins = input("What protein sources do you have? (e.g. chicken, beef, eggs): ").lower().split(",")
    veggies = input("What vegetables do you have? (e.g. broccoli, peppers, spinach): ").lower().split(",")
    carbs = input("What carbs do you have? (e.g. rice, pasta, bread): ").lower().split(",")
    sauces = input("What sauces or extras do you have? (e.g. soy sauce, mayonnaise): ").lower().split(",")
    salad = input("What salad items do you have? (e.g. lettuce, tomato): ").lower().split(",")

    # Merge, clean, and add defaults
    pantry = {i.strip() for i in proteins + veggies + carbs + sauces + salad if i.strip()}
    #print("you have:", pantry)
    print(f"\nYou have: {', '.join(sorted(pantry))}\n")
    return pantry

if __name__ == "__main__":
    pantry = get_user_pantry()

    def find_recipes(pantry):
        conn= sqlite3.connect('mealdb.sqlite')
        cur = conn.cursor()

        pantry_tuple = tuple(pantry)
        
        cur.execute(f'''
            SELECT R.name, R.calories, R.protein, R.carbs, R.fat
            FROM Recipes R
            JOIN Recipe_Ingredients RI ON R.id = RI.recipe_id
            JOIN Ingredient I ON RI.ingredient_id = I.id
            WHERE I.name IN ({','.join('?' for _ in pantry_tuple)})
            GROUP BY R.id
        ''', pantry_tuple)

        recipes = cur.fetchall()
        conn.close()
        return recipes

    results = find_recipes(pantry)

    if results:
        print("Recipes you can make:")
        for r in results:
            name, cal, protein, carbs, fat = r
            print(f"{name} - Calories: {cal}, Protein: {protein}, Carbs: {carbs}, Fat: {fat}")
    else:
        print("No matching recipes found.")