from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils.text import slugify


# ✅ Custom User
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


# ✅ Category
class Category(models.Model):
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


# ✅ Blog
class Blog(models.Model):
    LAYOUT_MAIN_THUMBNAILS = "main_thumbs"
    LAYOUT_GRID = "grid"
    LAYOUT_HERO_TEXT = "hero_text"

    LAYOUT_CHOICES = [
        (LAYOUT_MAIN_THUMBNAILS, "1 large + 3 thumbnails"),
        (LAYOUT_GRID, "2 x 2 grid"),
        (LAYOUT_HERO_TEXT, "Hero image + text"),
        ('step_by_step', 'Step by Step'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    content = models.TextField()
    ingredients = models.TextField(blank=True)
    prep_time = models.CharField(max_length=50, blank=True)
    cook_time = models.CharField(max_length=50, blank=True)
    servings = models.CharField(max_length=50, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blogs",
    )

    image = models.ImageField(upload_to='blog_steps/', null=True, blank=True)

    layout = models.CharField(
        max_length=20,
        choices=LAYOUT_CHOICES,
        default=LAYOUT_MAIN_THUMBNAILS,
    )

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    is_published = models.BooleanField(default=False)  

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# ✅ Blog Images
class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="extra_images")
    image = models.ImageField(upload_to="blogs/multi/")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


# ✅ Steps
class BlogStep(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='steps')
    image = models.ImageField(upload_to='blog_steps/')
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)


# ✅ Likes
class BlogLike(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('blog', 'user')


# ✅ Comments
class BlogComment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )

    created_at = models.DateTimeField(auto_now_add=True)



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', default='default.jpg')
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, default='Chennai, India')
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.email