#this code allows users to input a query to search for specific recipes,
#i.e. input = "wings", output may be a recipe for "buffalo wings"

import json
import sqlite3

conn = sqlite3.connect('mealdb.sqlite')
cur = conn.cursor()

cur.executescript('''
DROP TABLE IF EXISTS Recipes;
DROP TABLE IF EXISTS Ingredient;
DROP TABLE IF EXISTS recipe_ingredients;
                  
CREATE TABLE Recipes (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name   TEXT UNIQUE,
    instructions_link TEXT,
    calories INTEGER, 
    protein INTEGER, 
    carbs INTEGER, 
    fat INTEGER
);

CREATE TABLE Ingredient (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT UNIQUE
);

CREATE TABLE recipe_ingredients (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id   INTEGER,
    ingredient_id   INTEGER
);
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


search_term = input("Enter part of a recipe name: ").strip()

conn = sqlite3.connect('mealdb.sqlite')
cur = conn.cursor()

cur.execute('''
    SELECT 
        R.name,
        R.instructions_link,
        GROUP_CONCAT(I.name, ', ')
    FROM Recipes R
    JOIN recipe_ingredients RI ON R.id = RI.recipe_id
    JOIN Ingredient I ON RI.ingredient_id = I.id
    WHERE R.name LIKE '%' || ? || '%'
    GROUP BY R.id
''', (search_term,))

rows = cur.fetchall()
conn.close()

if rows:
    for r in rows:
        name, link, ingredients = r
        print(f"\n{name}\nInstructions: {link}\nIngredients: {ingredients}")
else:
    print("No recipes found matching that search.")