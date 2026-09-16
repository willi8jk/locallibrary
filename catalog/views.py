from django.shortcuts import render
from .models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()
    
    # Challenge: generate counts for genres and books that contain a particular word (case insensitive)
    word = "Food"
    num_genres_food = Genre.objects.filter(name__icontains=word).count()
    num_books_food = Book.objects.filter(title__icontains=word).count()

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_genres_food': num_genres_food,
        'num_books_food': num_books_food,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)