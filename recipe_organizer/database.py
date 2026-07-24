"""SQLite persistence for recipes and categories."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Category, Recipe


class RecipeDatabase:
    """Owns database setup and all recipe data operations."""

    def __init__(self, database_path: str | Path = "recipes.db") -> None:
        self.database_path = str(database_path)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_tables()

    def create_tables(self) -> None:
        """Create the application tables when they do not already exist."""
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE
            );

            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                ingredients TEXT NOT NULL,
                directions TEXT NOT NULL,
                category_id INTEGER NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            );
            """
        )
        self.connection.commit()

    @staticmethod
    def _require_text(value: str, field_name: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError(f"{field_name} is required.")
        return cleaned

    def get_or_create_category(self, name: str) -> Category:
        """Return an existing category or create it if needed."""
        cleaned_name = self._require_text(name, "Category name")
        row = self.connection.execute(
            "SELECT id, name FROM categories WHERE name = ?",
            (cleaned_name,),
        ).fetchone()

        if row is None:
            cursor = self.connection.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (cleaned_name,),
            )
            self.connection.commit()
            return Category(id=cursor.lastrowid, name=cleaned_name)

        return Category(id=row["id"], name=row["name"])

    def add_recipe(
        self,
        name: str,
        ingredients: str,
        directions: str,
        category_name: str,
    ) -> Recipe:
        """Validate and save a new recipe."""
        cleaned_name = self._require_text(name, "Recipe name")
        cleaned_ingredients = self._require_text(ingredients, "Ingredients")
        cleaned_directions = self._require_text(directions, "Directions")
        category = self.get_or_create_category(category_name)

        cursor = self.connection.execute(
            """
            INSERT INTO recipes (name, ingredients, directions, category_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                cleaned_name,
                cleaned_ingredients,
                cleaned_directions,
                category.id,
            ),
        )
        self.connection.commit()
        return Recipe(
            id=cursor.lastrowid,
            name=cleaned_name,
            ingredients=cleaned_ingredients,
            directions=cleaned_directions,
            category_id=category.id,
        )

    def get_recipe(self, recipe_id: int) -> Recipe | None:
        """Find one recipe by its database ID."""
        row = self.connection.execute(
            """
            SELECT id, name, ingredients, directions, category_id
            FROM recipes
            WHERE id = ?
            """,
            (recipe_id,),
        ).fetchone()
        return self._row_to_recipe(row) if row else None

    def update_recipe(
        self,
        recipe_id: int,
        name: str,
        ingredients: str,
        directions: str,
        category_name: str,
    ) -> Recipe | None:
        """Update a recipe and return it, or return None when it is missing."""
        if self.get_recipe(recipe_id) is None:
            return None

        cleaned_name = self._require_text(name, "Recipe name")
        cleaned_ingredients = self._require_text(ingredients, "Ingredients")
        cleaned_directions = self._require_text(directions, "Directions")
        category = self.get_or_create_category(category_name)

        self.connection.execute(
            """
            UPDATE recipes
            SET name = ?, ingredients = ?, directions = ?, category_id = ?
            WHERE id = ?
            """,
            (
                cleaned_name,
                cleaned_ingredients,
                cleaned_directions,
                category.id,
                recipe_id,
            ),
        )
        self.connection.commit()
        return self.get_recipe(recipe_id)

    def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe and report whether a row was removed."""
        cursor = self.connection.execute(
            "DELETE FROM recipes WHERE id = ?",
            (recipe_id,),
        )
        self.connection.commit()
        return cursor.rowcount > 0

    def list_recipes(self, page: int = 1, page_size: int = 5) -> list[Recipe]:
        """Return one page of recipes."""
        if page < 1:
            raise ValueError("Page must be at least 1.")
        if page_size < 1:
            raise ValueError("Page size must be at least 1.")

        rows = self.connection.execute(
            """
            SELECT id, name, ingredients, directions, category_id
            FROM recipes
            ORDER BY id
            LIMIT ? OFFSET ?
            """,
            (page_size, (page - 1) * page_size),
        ).fetchall()
        return [self._row_to_recipe(row) for row in rows]

    def list_recipes_by_category(self, category_id: int) -> list[Recipe]:
        """Return every recipe in a category."""
        rows = self.connection.execute(
            """
            SELECT id, name, ingredients, directions, category_id
            FROM recipes
            WHERE category_id = ?
            ORDER BY name
            """,
            (category_id,),
        ).fetchall()
        return [self._row_to_recipe(row) for row in rows]

    def search_recipes(self, keyword: str) -> list[Recipe]:
        """Search recipe names, ingredients, and directions."""
        cleaned_keyword = self._require_text(keyword, "Search keyword")
        pattern = f"%{cleaned_keyword}%"
        rows = self.connection.execute(
            """
            SELECT id, name, ingredients, directions, category_id
            FROM recipes
            WHERE name LIKE ? OR ingredients LIKE ? OR directions LIKE ?
            ORDER BY name
            """,
            (pattern, pattern, pattern),
        ).fetchall()
        return [self._row_to_recipe(row) for row in rows]

    def category_summary(self) -> list[tuple[Category, int]]:
        """Return each category with its recipe count."""
        rows = self.connection.execute(
            """
            SELECT categories.id, categories.name, COUNT(recipes.id) AS recipe_count
            FROM categories
            LEFT JOIN recipes ON categories.id = recipes.category_id
            GROUP BY categories.id, categories.name
            ORDER BY categories.name
            """
        ).fetchall()
        return [
            (Category(id=row["id"], name=row["name"]), row["recipe_count"])
            for row in rows
        ]

    def export_recipes(self, destination: str | Path) -> Path:
        """Write all recipes to a readable text file."""
        output_path = Path(destination)
        recipes = self.list_recipes(page=1, page_size=self.recipe_count() or 1)
        sections = [
            (
                f"Name: {recipe.name}\n"
                f"Ingredients: {recipe.ingredients}\n"
                f"Directions: {recipe.directions}\n"
            )
            for recipe in recipes
        ]
        output_path.write_text("\n".join(sections), encoding="utf-8")
        return output_path

    def recipe_count(self) -> int:
        """Return the total number of saved recipes."""
        row = self.connection.execute(
            "SELECT COUNT(*) AS total FROM recipes"
        ).fetchone()
        return row["total"]

    @staticmethod
    def _row_to_recipe(row: sqlite3.Row) -> Recipe:
        return Recipe(
            id=row["id"],
            name=row["name"],
            ingredients=row["ingredients"],
            directions=row["directions"],
            category_id=row["category_id"],
        )

    def close(self) -> None:
        """Close the SQLite connection."""
        self.connection.close()

    def __enter__(self) -> RecipeDatabase:
        return self

    def __exit__(self, *_: Iterable[object]) -> None:
        self.close()

