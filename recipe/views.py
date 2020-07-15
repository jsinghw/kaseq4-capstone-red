from django.shortcuts import render, reverse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import Recipe
from user.models import CustomUser
from .forms import RecipeForm
from review.models import Review
from review.forms import AddReviewForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View


class RecipeView(View):
    def get(self, request, title):
        html = "recipe.html"
        recipe = Recipe.objects.get(title=title)
        reviews = Review.objects.filter(recipe=recipe)
        form = AddReviewForm(initial={'recipe': Recipe.objects.get(
            title=title), 'author': request.user})
        return render(request, html, {'recipe': recipe, 'reviews': reviews, 'form': form})

    def post(self, request, title):
        html = 'recipe.html'
        recipe = Recipe.objects.get(title=title)
        reviews = Review.objects.filter(recipe=recipe.id)
        form = AddReviewForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            Review.objects.create(
                title=data['title'],
                rating=data['rating'],
                content=data['content'],
                author=request.user,
                recipe=recipe
            )
            form = AddReviewForm(initial={'recipe': Recipe.objects.get(
                title=title), 'author': request.user})

        return render(request, html, {'recipe': recipe, 'reviews': reviews, 'form': form})

def RecipeCard(request):
    html = "recipe_card.html"
    form = RecipeForm()
    if form.is_valid():
        data = form.cleaned_data
        recipe = Recipe.objects.get(
            title = data['title'],
            recipe_picture = data['recipe_picture']
            )
        return HttpResponseRedirect(reverse('recipe', args=(recipe.title,)))
    return render(request, html, {'form': form})

def FavoriteListView(request, sort):
    html = 'favorites.html'
    print(request)
    print("sort: ", sort)
    if sort == 'title':
        recipes = request.user.favorites.order_by('title')
    elif sort == 'time_prep':
        recipes = request.user.favorites.order_by('time_prep')
    elif sort == 'date_old':
        recipes = request.user.favorites.order_by('date_created')
    else:
        recipes = request.user.favorites.order_by('-date_created')
    print(recipes)
    return render(request, html, {'recipes': recipes})


class RecipeAddView(LoginRequiredMixin, View):

    def get(self, request):
        html = "form.html"
        form = RecipeForm()
        return render(request, html, {"form": form})

    def post(self, request):
        html = "form.html"
        form = RecipeForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            recipe = Recipe.objects.create(
                author=request.user,
                title=data['title'],
                description=data['description'],
                tags=data['tags'],
                ingredients=data['ingredients'],
                instructions=data['instructions'],
                servings=data['servings'],
                time_prep=data['time_prep'],
                time_cook=data['time_cook'],
                time_additional=data['time_additional'],
            )
            return HttpResponseRedirect(reverse('recipe',
                                                args=(recipe.title,)))
        return render(request, html, {"form": form})


@login_required
def FavoriteView(request, title):
    Recipe.objects.get(title=title).favorited_by.add(request.user)
    return HttpResponseRedirect(reverse('recipe', args=(title,)))


@login_required
def UnfavoriteView(request, title):
    Recipe.objects.get(title=title).favorited_by.remove(request.user)
    return HttpResponseRedirect(reverse('recipe', args=(title,)))
