"""Interactive command-line interface for Recipe Organizer."""

from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import Type

from .database import RecipeDatabase
from .models import Recipe


class RecipeOrganizerCLI:
    """Collects user input and delegates data work to RecipeDatabase."""

    def __init__(self, database_path: str | Path = "recipes.db") -> None:
        self.database = RecipeDatabase(database_path)

    @staticmethod
    def _display_recipe(recipe: Recipe) -> None:
        print(f"\n[{recipe.id}] {recipe.name}")
        print(f"Ingredients: {recipe.ingredients}")
        print(f"Directions: {recipe.directions}")

    @staticmethod
    def _read_recipe_id(prompt: str) -> int | None:
        try:
            return int(input(prompt).strip())
        except ValueError:
            print("Please enter a numeric recipe ID.")
            return None

    def add_recipe(self) -> None:
        try:
            recipe = self.database.add_recipe(
                input("Recipe name: "),
                input("Ingredients (separated by commas): "),
                input("Directions: "),
                input("Category: "),
            )
        except ValueError as error:
            print(f"Error: {error}")
            return

        print(f'Recipe "{recipe.name}" added with ID {recipe.id}.')

    def update_recipe(self) -> None:
        recipe_id = self._read_recipe_id("Recipe ID to update: ")
        if recipe_id is None:
            return

        try:
            recipe = self.database.update_recipe(
                recipe_id,
                input("New recipe name: "),
                input("New ingredients: "),
                input("New directions: "),
                input("New category: "),
            )
        except ValueError as error:
            print(f"Error: {error}")
            return

        if recipe is None:
            print("Recipe not found.")
        else:
            print("Recipe updated.")
            self._display_recipe(recipe)

    def delete_recipe(self) -> None:
        recipe_id = self._read_recipe_id("Recipe ID to delete: ")
        if recipe_id is None:
            return

        message = "Recipe deleted." if self.database.delete_recipe(recipe_id) else "Recipe not found."
        print(message)

    def view_all_recipes(self) -> None:
        page = 1
        while True:
            recipes = self.database.list_recipes(page=page)
            if not recipes:
                print("No recipes found." if page == 1 else "No more recipes.")
                return

            print(f"\nRecipes — page {page}")
            for recipe in recipes:
                self._display_recipe(recipe)

            choice = input("\n[n]ext, [p]revious, or Enter to return: ").lower().strip()
            if choice == "n":
                page += 1
            elif choice == "p" and page > 1:
                page -= 1
            else:
                return

    def view_recipes_by_category(self) -> None:
        summaries = self.database.category_summary()
        if not summaries:
            print("No categories found.")
            return

        print("\nCategories")
        for category, count in summaries:
            print(f"[{category.id}] {category.name} ({count} recipes)")

        category_id = self._read_recipe_id("Category ID: ")
        if category_id is None:
            return
        recipes = self.database.list_recipes_by_category(category_id)
        for recipe in recipes:
            self._display_recipe(recipe)
        if not recipes:
            print("No recipes found for that category.")

    def search_recipes(self) -> None:
        try:
            recipes = self.database.search_recipes(input("Search keyword: "))
        except ValueError as error:
            print(f"Error: {error}")
            return

        for recipe in recipes:
            self._display_recipe(recipe)
        if not recipes:
            print("No matching recipes found.")

    def view_categories(self) -> None:
        summaries = self.database.category_summary()
        for category, count in summaries:
            print(f"{category.name}: {count} recipes")
        if not summaries:
            print("No categories found.")

    def export_recipes(self) -> None:
        output_path = self.database.export_recipes("recipes_export.txt")
        print(f"Recipes exported to {output_path}.")

    def display_menu(self) -> None:
        actions = {
            "1": self.add_recipe,
            "2": self.update_recipe,
            "3": self.delete_recipe,
            "4": self.view_all_recipes,
            "5": self.view_recipes_by_category,
            "6": self.search_recipes,
            "7": self.view_categories,
            "8": self.export_recipes,
        }

        while True:
            print(
                "\n=== RECIPE ORGANIZER ===\n"
                "1. Add recipe\n"
                "2. Update recipe\n"
                "3. Delete recipe\n"
                "4. View all recipes\n"
                "5. View recipes by category\n"
                "6. Search recipes\n"
                "7. View category totals\n"
                "8. Export recipes\n"
                "9. Exit"
            )
            choice = input("Choose an option: ").strip()
            if choice == "9":
                print("Goodbye!")
                return

            action = actions.get(choice)
            if action is None:
                print("Please choose a number from 1 to 9.")
            else:
                action()

    def close(self) -> None:
        self.database.close()

    def __enter__(self) -> RecipeOrganizerCLI:
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.close()

