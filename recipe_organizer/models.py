"""Domain objects used by the recipe organizer."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Category:
    """A group used to organize related recipes."""

    name: str
    id: int | None = None


@dataclass(frozen=True)
class Recipe:
    """A recipe stored by the application."""

    name: str
    ingredients: str
    directions: str
    category_id: int
    id: int | None = None
