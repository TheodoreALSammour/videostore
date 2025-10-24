from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class Video(models.Model):
    GENRE_CHOICES = [
        ("Comedy", "Comedy"),
        ("Romance", "Romance"),
        ("Action", "Action"),
        ("Drama", "Drama"),
        ("Horror", "Horror"),
        ("Sci-Fi", "Sci-Fi"),
        ("Thriller", "Thriller"),
        ("Animation", "Animation"),
        ("Family", "Family"),
    ]

    MovieID = models.IntegerField(primary_key=True)
    MovieTitle = models.CharField(max_length=200)
    Actor1Name = models.CharField(max_length=120, blank=True)
    Actor2Name = models.CharField(max_length=120, blank=True)
    DirectorName = models.CharField(max_length=120, blank=True)
    MovieGenre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    ReleaseYear = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2100)]
    )

    def __str__(self):
        return f"{self.MovieTitle} ({self.ReleaseYear})"