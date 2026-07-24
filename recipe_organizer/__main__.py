from .cli import RecipeOrganizerCLI


def main() -> None:
    """Start the interactive recipe organizer."""
    with RecipeOrganizerCLI() as organizer:
        organizer.display_menu()


if __name__ == "__main__":
    main()

