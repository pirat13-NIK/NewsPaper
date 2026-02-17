from django.db import models
from django.contrib.auth.models import User


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def update_rating(self):
        posts_rating = sum(post.rating for post in self.post_set.all()) * 3

        comments_rating = sum(comment.rating for comment in self.user.comment_set.all())

        posts_comments_rating = 0
        for post in self.post_set.all():
            posts_comments_rating += sum(comment.rating for comment in post.comment_set.all())

        self.rating = posts_rating + comments_rating + posts_comments_rating
        self.save()

    def __str__(self):
        return f"{self.user.username} (рейтинг: {self.rating})"


