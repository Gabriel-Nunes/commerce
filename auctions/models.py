from django.contrib.auth.models import AbstractUser, User
from django.db import models
from datetime import datetime


# class User(AbstractUser):
#     username = models.CharField(max_length=150, unique=True)
#     watchlist = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name='watchlist')
    

class AuctionListing(models.Model):
    categories_choices = (
        ('Fashion', 'Fashion'),
        ('Toys', 'Toys'),
        ('Electronics', 'Electronics'),
        ('Home', 'Home'),
        ('Books', 'Books'),
        ('Other', 'Other')
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auction_listings")
    product = models.CharField(max_length=200)
    photo = models.ImageField(blank=True,  null=True, upload_to='uploads/')
    description = models.TextField(max_length=500)
    starting_bid = models.FloatField(default=0.01)
    current_price = models.FloatField()
    current_winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="current_winner", blank=True, null=True)
    active = models.BooleanField(default=True)
    categorie = models.CharField(max_length=15, choices=categories_choices, blank=True, null=True, default='Other')

    def __str__(self):
        return f"{self.product}: $ {self.current_price}"


class Watchlist(models.Model):
    auction_listings = models.ManyToManyField(AuctionListing)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist', primary_key=True)



class Bid(models.Model):
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    value = models.FloatField()


class Comment(models.Model):
    date = models.DateField(auto_created=True, default=datetime.now())
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    auction_listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField(max_length=500)
