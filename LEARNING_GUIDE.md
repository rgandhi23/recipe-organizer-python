# Recipe Organizer Learning Guide

Use this guide to understand the project well enough to explain it in your own words.

## The product in one sentence

The command-line interface collects a user's choices, `RecipeDatabase` saves and retrieves the data, and `Recipe` and `Category` objects represent the results.

```text
User → RecipeOrganizerCLI → RecipeDatabase → SQLite
                                  ↓
                         Recipe / Category
```

## 1. Classes and objects

A **class** is a blueprint. An **object** is one specific value created from that blueprint.

```python
recipe = Recipe(
    name="Tomato Pasta",
    ingredients="pasta, tomatoes",
    directions="Boil and combine.",
    category_id=1,
)
```

`Recipe` is the class. `recipe` is one object.

## 2. Separation of concerns

Each class has one main responsibility:

- `RecipeOrganizerCLI` communicates with the user.
- `RecipeDatabase` communicates with SQLite.
- `Recipe` and `Category` hold application data.

This means the database can be tested without pretending to type into the menu.

## 3. CRUD

CRUD describes the four basic data operations:

- **Create:** `add_recipe`
- **Read:** `get_recipe`, `list_recipes`, and `search_recipes`
- **Update:** `update_recipe`
- **Delete:** `delete_recipe`

Most business applications use these same four operations.

## 4. Relational databases

The project has two tables: `categories` and `recipes`.

One category can contain many recipes. Each recipe stores a `category_id` foreign key that points to its category.

This avoids repeating the full category information inside every recipe.

## 5. Parameterized SQL

The project uses placeholders:

```python
self.connection.execute(
    "SELECT * FROM recipes WHERE id = ?",
    (recipe_id,),
)
```

The database receives the SQL command and the value separately. This is safer and clearer than building SQL by joining strings.

## 6. Validation

`_require_text` removes extra spaces and rejects blank values before they reach the database. The database also marks important columns as `NOT NULL`.

This is defense in depth: both the Python code and database protect data quality.

## 7. Automated tests

Every test creates a temporary SQLite database. The test can add, change, or delete data without touching a real user's recipes.

The tests check:

- Adding and searching
- Reusing a category
- Updating and deleting
- Pagination and exporting

## Interview-ready explanation

> I built a Python recipe organizer that persists data in SQLite. I separated the user interface, database operations, and domain models into different classes. It supports full CRUD, category relationships, search, pagination, export, validation, and automated tests. I originally prototyped it in Jupyter, then refactored it into a testable package.

## Questions you should be able to answer

1. Why are the menu and database code in different classes?
2. What is the difference between the `Recipe` class and one recipe object?
3. What do CRUD operations mean?
4. Why does a recipe store `category_id`?
5. Why do SQL queries use `?` placeholders?
6. How do the tests avoid changing the real database?
7. What happens when the user enters a blank recipe name?
8. What would you build next?

