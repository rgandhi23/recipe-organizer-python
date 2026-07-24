# Recipe Organizer — Python + SQLite

A command-line product for saving, organizing, finding, updating, and exporting recipes. The application stores data in SQLite, so recipes remain available after the program closes.

This project began as a Jupyter notebook and was reorganized into a small Python package to make each responsibility clear, testable, and easy to explain.

## Features

- Add, update, and delete recipes
- Group recipes by category
- Search names, ingredients, and directions
- Browse results with pagination
- View recipe totals by category
- Export recipes to a text file
- Preserve data in a relational SQLite database
- Validate user input and handle missing records

## Run the product

Python 3.9 or newer is recommended. No third-party packages are required.

```bash
python3 -m recipe_organizer
```

The app creates `recipes.db` in the current directory the first time it runs.

## Run the tests

```bash
python3 -m unittest discover -v
```

The tests use temporary databases, so they do not change your real recipes.

## Design

| Component | Responsibility |
| --- | --- |
| `Category` and `Recipe` | Model the application's core data |
| `RecipeDatabase` | Own SQLite setup, queries, validation, and CRUD operations |
| `RecipeOrganizerCLI` | Collect input, display results, and control the menu |
| `tests/test_database.py` | Verify saving, searching, categories, updates, deletion, pagination, and export |

The command-line interface does not write SQL, and the database class does not ask the user questions. This separation of concerns makes the project easier to maintain and test.

## Database relationship

```text
categories
  id ───────────────┐
  name              │
                    │ one category
                    │ has many recipes
recipes             │
  id                │
  name              │
  ingredients       │
  directions        │
  category_id ──────┘
```

The `category_id` foreign key connects each recipe to one category. Parameterized SQL queries use `?` placeholders to keep user input separate from SQL commands.

## Concepts demonstrated

- Object-oriented programming
- Classes, objects, methods, and composition
- Encapsulation and separation of concerns
- CRUD operations: create, read, update, delete
- Relational database design and foreign keys
- Parameterized SQL
- Input validation
- Search and pagination
- File export
- Context managers
- Automated testing with `unittest`

## Project history

The original notebook is preserved in `notebooks/Recipe_Organizer.ipynb`. The package version keeps the original product idea while making the code easier to run, test, and discuss in an interview.

## Possible next steps

- Add recipe ratings and preparation times
- Store ingredients in their own table
- Add a graphical or web interface
- Import and export JSON
- Add continuous integration with GitHub Actions
