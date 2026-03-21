from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from myapp.models import Blog, Category


class Command(BaseCommand):
    help = "Seed default categories and a few starter blog/recipe posts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Create seed posts even if some Blog posts already exist.",
        )

    def handle(self, *args, **options):
        force = bool(options.get("force"))

        if Blog.objects.exists() and not force:
            self.stdout.write(self.style.WARNING("Blogs already exist. Skipping seed."))
            self.stdout.write("Run with --force to add seed posts anyway.")
            return

        categories = [
            "Desserts",
            "Quick Meals",
            "Vegetarian",
            "Non-Veg",
            "Drinks",
        ]
        category_map = {}
        for idx, name in enumerate(categories):
            cat, _ = Category.objects.get_or_create(
                name=name, defaults={"sort_order": idx}
            )
            category_map[name] = cat

        User = get_user_model()
        author, _ = User.objects.get_or_create(
            email="seed@example.com", defaults={"username": "SeedChef"}
        )
        if not author.has_usable_password():
            author.set_password("seed12345")
            author.save(update_fields=["password"])

        seeds = [
            {
                "title": "Creamy Spinach & Mushroom Pasta",
                "category": "Vegetarian",
                "description": "A comforting vegetarian pasta dish loaded with fresh spinach, mushrooms, and creamy sauce.",
                "content": (
                    "Ingredients:\n"
                    "- Pasta\n- Mushrooms\n- Spinach\n- Garlic\n- Cream\n\n"
                    "Steps:\n"
                    "1. Cook pasta.\n"
                    "2. Sauté garlic and mushrooms.\n"
                    "3. Add spinach, then cream.\n"
                    "4. Toss with pasta and serve."
                ),
            },
            {
                "title": "Refreshing Summer Mango Smoothie",
                "category": "Drinks",
                "description": "A cool and tropical mango smoothie recipe that's perfect for hot summer afternoons.",
                "content": (
                    "Ingredients:\n"
                    "- Mango\n- Yogurt\n- Honey\n- Ice\n\n"
                    "Steps:\n"
                    "1. Blend everything until smooth.\n"
                    "2. Taste and adjust sweetness.\n"
                    "3. Serve chilled."
                ),
            },
            {
                "title": "Easy Homemade Chocolate Brownies",
                "category": "Desserts",
                "description": "Soft, fudgy, and rich brownies made with simple ingredients.",
                "content": (
                    "Ingredients:\n"
                    "- Cocoa powder\n- Butter\n- Sugar\n- Eggs\n- Flour\n\n"
                    "Steps:\n"
                    "1. Mix wet ingredients.\n"
                    "2. Fold in dry ingredients.\n"
                    "3. Bake at 180°C for ~22 minutes."
                ),
            },
        ]

        created = 0
        for s in seeds:
            blog, was_created = Blog.objects.get_or_create(
                title=s["title"],
                defaults={
                    "category": category_map.get(s["category"]),
                    "description": s["description"],
                    "content": s["content"],
                    "author": author,
                },
            )
            if was_created:
                created += 1

        self.stdout.write(self.style.SUCCESS(f"Seed complete. Created {created} posts."))

