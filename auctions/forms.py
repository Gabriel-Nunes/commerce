from django import forms
from .models import AuctionListing


class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = [
            'product',
            'photo',
            'description',
            'starting_bid',
            # 'current_price',
        ]