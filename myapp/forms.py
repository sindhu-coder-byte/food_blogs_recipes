from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
import re

from .models import Blog, BlogImage, Category, CustomUser


class SignupForm(UserCreationForm):
    username= forms.CharField(
        widget=forms.TextInput(attrs={
            "placeholder": "Enter Username", "class": "form-control"
            })
        )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Id"}),
        
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter Password",
            "class": "form-control"
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
            "class": "form-control"
        })
    )

    
    

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = (self.cleaned_data.get('email') or "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")

        # Basic, user-friendly validation (format + allowed TLDs)
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.(com|in|org)$', email):
            raise forms.ValidationError("Enter a valid email (example: name@gmail.com).")

        User = get_user_model()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered. Please login.")

        return email

    def clean_username(self):
        username = (self.cleaned_data.get('username') or "").strip()
        if not username:
            raise forms.ValidationError("Username is required.")

        if len(username) < 4:
            raise forms.ValidationError("Username must be at least 4 characters")

        return username

    def clean_password1(self):
        password = self.cleaned_data.get('password1') or ""

        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters")

        return password
    
    


class EmailAuthenticationForm(AuthenticationForm):
    """
    Login form that validates email format before calling authenticate().
    Django will still pass this value as the 'username' parameter internally.
    Since CustomUser.USERNAME_FIELD = 'email', authentication will work.
    """

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter Email Id"}),
        required=True,
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Enter Password"}),
        required=True,
    )

    def clean_username(self):
        email = (self.cleaned_data.get("username") or "").strip().lower()
        if not re.match(r'^[\w\.-]+@[\w\.-]+\.(com|in|org)$', email):
            raise ValidationError("Enter a valid email (example: name@gmail.com).")
        return email


class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ["title", "category", "description", "content", "image", "layout"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Recipe title"}),
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Short description (shown on card)"}
            ),
            "content": forms.Textarea(
                attrs={"rows": 10, "placeholder": "Full recipe / blog content"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        base = {
            "style": "width:100%; padding:10px 12px; border:1px solid #E5E7EB; border-radius:10px; outline:none; font-family:Lato, system-ui, -apple-system, Segoe UI, sans-serif;",
        }

        # Ensure dropdown shows admin-created categories with a placeholder.
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "Select category"

        for name, field in self.fields.items():
            if name in {"image", "layout"}:
                field.widget.attrs.update({"style": "width:100%;"})
                continue
            field.widget.attrs.update(base)


class BlogImageForm(forms.ModelForm):
    class Meta:
        model = BlogImage
        fields = ["image", "order"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"class": "file-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get("image")

        if not image:
            return cleaned

        return cleaned