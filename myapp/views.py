from django.shortcuts import render
from django.views.generic import TemplateView


def home(request):
    from .models import Blog

    blogs = Blog.objects.all().order_by("-created_at")
    return render(request, "myapp/index.html", {"blogs": blogs})


from django.views.generic import CreateView
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django.forms import modelformset_factory

from .forms import (
    BlogForm,
    BlogImageForm,
    EmailAuthenticationForm,
    SignupForm,
)
from .models import Blog, BlogImage, BlogStep, Category


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'myapp/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login after successful signup
        login(self.request, self.object)
        return response


class CustomLoginView(LoginView):
    template_name = 'myapp/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(RedirectView):
    pattern_name = "home"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)
    

# views.py
from django.contrib.auth.decorators import login_required
from .models import Blog, Profile

@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        # Image upload
        if request.FILES.get("profile_image"):
            profile.image = request.FILES["profile_image"]

        # Bio update (safe)
        profile.bio = request.POST.get("bio", "")  

        profile.save()

    blogs = Blog.objects.filter(author=request.user, is_published=True)
    drafts = Blog.objects.filter(author=request.user, is_published=False)

    context = {
        'profile': profile,
        'blogs': blogs,
        'drafts': drafts,
        'blog_count': blogs.count(),
        'draft_count': drafts.count(),
    }

    return render(request, 'myapp/profile.html', context)

from django.db.models import Count
from django.shortcuts import redirect

class WriteView(LoginRequiredMixin, CreateView):
    model = Blog
    form_class = BlogForm
    template_name = "myapp/write.html"
    success_url = reverse_lazy("blogs")
    login_url = reverse_lazy("login")

    def _get_image_formset_class(self):
        return modelformset_factory(
            BlogImage,
            form=BlogImageForm,
            extra=4,
            max_num=4,
            can_delete=True,
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["core_categories"] = Category.objects.annotate(
            post_count=Count("blogs")
        )

        ImageFormSet = self._get_image_formset_class()

        if self.request.method == "POST":
            ctx["image_formset"] = ImageFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=BlogImage.objects.none(),
                prefix="images",
            )
        else:
            ctx["image_formset"] = ImageFormSet(
                queryset=BlogImage.objects.none(),
                prefix="images",
            )

        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        image_formset = context["image_formset"]

        if not image_formset.is_valid():
            return self.form_invalid(form)

        # ✅ AUTHOR AUTO
        form.instance.author = self.request.user
        form.instance.ingredients = self.request.POST.get("ingredients")
        form.instance.prep_time = self.request.POST.get("prep_time")
        form.instance.cook_time = self.request.POST.get("cook_time")
        form.instance.servings = self.request.POST.get("servings")


        action = self.request.POST.get("action")

        if action == "publish":
          form.instance.is_published = True
        else:
          form.instance.is_published = False  

        if not form.cleaned_data.get("layout"):
           form.instance.layout = "main_thumbs"

        self.object = form.save() 

        # =========================
        # ✅ STEP-BY-STEP SAVE FIXED
        # =========================

        if self.object.layout == "step_by_step":
          i = 1

          while True:
           img = self.request.FILES.get(f"step_image_{i}")
           desc = self.request.POST.get(f"step_desc_{i}")

           if not img and not desc:
            break

           if desc:
               BlogStep.objects.create(
                 blog=self.object,
                 image=img,   # can be None
                 description=desc,
                 order=i
             )

           i += 1
        # =========================
        # ✅ IMAGE FORMSET SAVE
        # =========================
        images_saved = 0

        for img_form in image_formset.forms:
            if not img_form.cleaned_data:
                continue

            if img_form.cleaned_data.get("DELETE"):
                continue

            image = img_form.cleaned_data.get("image")

            if image:
                BlogImage.objects.create(
                    blog=self.object,
                    image=image,
                    order=images_saved
                )
                images_saved += 1

            if images_saved >= 4:
                break

        return redirect("profile")
    
from django.views.generic import DetailView, ListView
from django.conf import settings
from .models import Blog, BlogComment, BlogLike
class BlogDetailView(DetailView):
    model = Blog
    template_name = "myapp/blog_detail.html"
    context_object_name = "blog"

    # ✅ CONTEXT DATA (INSIDE CLASS)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.object

        # ✅ INGREDIENT LIST (clean)
        if blog.ingredients:
            context["ingredients_list"] = [
                i.strip() for i in blog.ingredients.splitlines() if i.strip()
            ]
        else:
            context["ingredients_list"] = []

        # ✅ LIKE STATUS
        if self.request.user.is_authenticated:
            context['liked'] = BlogLike.objects.filter(
                blog=blog,
                user=self.request.user
            ).exists()
        else:
            context['liked'] = False

        context['like_count'] = blog.likes.count()

        # ✅ COMMENTS
        context['comments'] = blog.comments.filter(
            parent__isnull=True
        ).order_by('-created_at')

        # ✅ TRENDING (latest blogs except current)
        context['trending_blogs'] = Blog.objects.exclude(
            id=blog.id
        ).order_by('-created_at')[:5]

        # ✅ RELATED (same category)
        if blog.category:
            context['related_blogs'] = Blog.objects.filter(
                category=blog.category
            ).exclude(id=blog.id)[:4]
        else:
            context['related_blogs'] = Blog.objects.none()

        return context

    # ✅ POST HANDLER (LIKE + COMMENT + REPLY)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        blog = self.object

        # ===== LIKE =====
        if "like" in request.POST:
            if request.user.is_authenticated:
                liked = BlogLike.objects.filter(
                    blog=blog,
                    user=request.user
                ).exists()

                if liked:
                    BlogLike.objects.filter(
                        blog=blog,
                        user=request.user
                    ).delete()
                else:
                    BlogLike.objects.create(
                        blog=blog,
                        user=request.user
                    )

            return redirect('blog_detail', pk=blog.pk)

        # ===== COMMENT / REPLY =====
        if request.user.is_authenticated:
            comment_text = request.POST.get("comment")
            parent_id = request.POST.get("parent_id")

            if comment_text:
                parent = None
                if parent_id:
                    parent = BlogComment.objects.get(id=parent_id)

                BlogComment.objects.create(
                    blog=blog,
                    user=request.user,
                    comment=comment_text,
                    parent=parent
                )

        return redirect('blog_detail', pk=blog.pk)

from django.db.models import Q

class BlogListView(ListView):
    model = Blog
    template_name = "myapp/blogs.html"
    context_object_name = "blogs"
    paginate_by = 5 

    def get_queryset(self):
        qs = Blog.objects.all().select_related(
            "author", "category"
        ).prefetch_related(
            "extra_images"
        ).order_by("-created_at")
        
        
            # 🔍 SEARCH
        query = (self.request.GET.get("q") or "").strip()

        if query:
          qs = qs.filter(
               Q(title__icontains=query) |
               Q(description__icontains=query) |
               Q(ingredients__icontains=query)
         )

        
        category_slug = (self.request.GET.get("category") or "").strip()
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        return qs

    def get_context_data(self, **kwargs):
        from django.db.models import Count

        ctx = super().get_context_data(**kwargs)
        categories_qs = Category.objects.annotate(post_count=Count("blogs"))
        ctx["categories"] = categories_qs
        # Show categories in a preferred order (if present), then the rest.
        preferred_slugs = ["desserts", "vegetarian", "non-veg"]
        by_slug = {c.slug: c for c in categories_qs}
        ordered = [by_slug[s] for s in by_slug if s in preferred_slugs]
        extras = [c for c in categories_qs if c.slug not in set(preferred_slugs)]
        ctx["ordered_categories"] = ordered
        ctx["extra_categories"] = extras
        ctx["ordered_categories_count"] = len(ordered)
        ctx["active_category"] = (self.request.GET.get("category") or "").strip()
        return ctx
    
    
from django.views.generic import UpdateView

class EditBlogView(LoginRequiredMixin, UpdateView):
    model = Blog
    form_class = BlogForm
    template_name = "myapp/write.html"
    success_url = reverse_lazy("blogs")

    def _get_image_formset_class(self):
        return modelformset_factory(
            BlogImage,
            form=BlogImageForm,
            extra=2,
            can_delete=True
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ImageFormSet = self._get_image_formset_class()

        if self.request.method == "POST":
            ctx["image_formset"] = ImageFormSet(
                self.request.POST,
                self.request.FILES,
                queryset=self.object.extra_images.all(),
                prefix="images",
            )
        else:
            ctx["image_formset"] = ImageFormSet(
                queryset=self.object.extra_images.all(),
                prefix="images",
            )

        ctx["core_categories"] = Category.objects.all()

        return ctx

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context["image_formset"]

        if not formset.is_valid():
            return self.form_invalid(form)

        self.object = form.save()

        for f in formset:
            if not f.cleaned_data:
                continue

            # ✅ DELETE OLD IMAGE
            if f.cleaned_data.get("DELETE"):
                if f.instance.pk:
                    f.instance.delete()
                continue

            # ✅ UPDATE / ADD IMAGE
            if f.cleaned_data.get("image"):
                img = f.save(commit=False)
                img.blog = self.object
                img.save()

        return redirect(self.success_url)
    

class RecipeView(TemplateView):
    template_name = "myapp/recipes.html"
    

from django.shortcuts import get_object_or_404, redirect

@login_required
def publish_blog(request, id):
    blog = get_object_or_404(Blog, id=id, author=request.user)

    blog.is_published = True  
    blog.save()

    return redirect('profile') 


@login_required
def unpublish_blog(request, id):
    blog = get_object_or_404(Blog, id=id, author=request.user)

    blog.is_published = False  
    blog.save()

    return redirect("profile") 

