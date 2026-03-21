from django.urls import path
from . import views
from .views import SignupView, CustomLoginView, LogoutView, WriteView
from django.contrib.auth import views as auth_views
from .views import BlogDetailView
from .views import BlogListView
from .views import RecipeView
from .views import EditBlogView


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('write/', WriteView.as_view(), name='write'),
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(template_name="myapp/password_reset.html"),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="myapp/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="myapp/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="myapp/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    
    path('blog/<int:pk>/', BlogDetailView.as_view(), name='blog_detail'),
    path('blogs/', BlogListView.as_view(), name='blogs'),
    path('recipes/', RecipeView.as_view(), name='recipes'),
    path('edit/<int:pk>/', EditBlogView.as_view(), name='edit_blog'),


]