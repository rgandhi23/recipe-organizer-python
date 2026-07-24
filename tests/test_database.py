"""Automated tests for the recipe data layer."""

import tempfile
import unittest
from pathlib import Path

from recipe_organizer import RecipeDatabase


class RecipeDatabaseTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "test_recipes.db"
        self.database = RecipeDatabase(database_path)

    def tearDown(self) -> None:
        self.database.close()
        self.temporary_directory.cleanup()

    def test_add_and_search_recipe(self) -> None:
        recipe = self.database.add_recipe(
            "Tomato Pasta",
            "pasta, tomatoes, garlic",
            "Boil the pasta and simmer the sauce.",
            "Dinner",
        )

        results = self.database.search_recipes("tomato")

        self.assertIsNotNone(recipe.id)
        self.assertEqual(1, len(results))
        self.assertEqual("Tomato Pasta", results[0].name)

    def test_reuses_category_ignoring_case(self) -> None:
        first = self.database.add_recipe("Pasta", "pasta", "Boil.", "Dinner")
        second = self.database.add_recipe("Soup", "vegetables", "Simmer.", "dinner")

        summaries = self.database.category_summary()

        self.assertEqual(first.category_id, second.category_id)
        self.assertEqual(1, len(summaries))
        self.assertEqual(2, summaries[0][1])

    def test_update_and_delete_recipe(self) -> None:
        recipe = self.database.add_recipe("Toast", "bread", "Toast it.", "Breakfast")

        updated = self.database.update_recipe(
            recipe.id,
            "Avocado Toast",
            "bread, avocado",
            "Toast the bread and add avocado.",
            "Breakfast",
        )
        deleted = self.database.delete_recipe(recipe.id)

        self.assertEqual("Avocado Toast", updated.name)
        self.assertTrue(deleted)
        self.assertIsNone(self.database.get_recipe(recipe.id))

    def test_pagination_and_export(self) -> None:
        for number in range(6):
            self.database.add_recipe(
                f"Recipe {number}",
                "ingredient",
                "Cook.",
                "Test",
            )

        second_page = self.database.list_recipes(page=2, page_size=5)
        export_path = Path(self.temporary_directory.name) / "recipes.txt"
        self.database.export_recipes(export_path)

        self.assertEqual(1, len(second_page))
        self.assertIn("Recipe 5", export_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()

