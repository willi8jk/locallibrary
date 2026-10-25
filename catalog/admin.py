from django.contrib import admin

from .models import Author, BookAuthor, Genre, Book, BookInstance, Language

# consider adding save_as to more easily add instance that have similar values
# you could do this for any or all of the below, e.g.
# admin.site.register(Book, save_as=True)
# except mayeb not bookinstance tho

# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)
admin.site.register(Language)
# admin.site.register(BookAuthor)


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('book', 'author', 'author_order')
    fields = ['book', 'author', 'author_order']


class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 0

# Define the admin class

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',
                    'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BookAuthorInline]
    # optionally enable "save as new", by uncommenting line below
    # save_as = True
    

# Register the admin class with the associated model
# admin.site.register(Author, AuthorAdmin)

# Challenge 2
# class AuthorBooksInline(admin.TabularInline):
#     model = Book
#     extra = 0

# End Challenge 2


class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0

# Register the Admin classes for Book using the decorator


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'display_genre')
    inlines = [BooksInstanceInline, BookAuthorInline]

# Register the Admin classes for BookInstance using the decorator


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):

    # Challenge 1
    list_display = ('book', 'status', 'due_back', 'id')
    # End Challenge 1

    list_filter = ('status', 'due_back')
    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Availability', {
            'fields': ('status', 'due_back')
        }),
    )
