"""Contains all models used in the app."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from . import fileUtils
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.core.validators import RegexValidator

class User(AbstractUser):
    """User model - inherited from Django implementation"""
    pass




class Auction(models.Model):
    """Contains info about one auction:
        * auction's title
        * auction's description
        * who is selling
        * auction's current price
        * when auction was publicated
        * what is auction's category
        * auction's image URL
        * is auction closed?
    """

    # Categories - choices
    AI = "AI"
    OTHER = "OTH"
    WEB_DEV = "WEB"
    MOBILE_DEV = "MOB"
    DATA_SCIENCE = "DAT"
    CLOUD_COMPUTING = "CLD"
    CYBERSECURITY = "SEC"
    DEVOPS = "DEV"
    GAME_DEV = "GAM"
    IOT = "IOT"
    BLOCKCHAIN = "BLC"

    CATEGORY = [
        (OTHER, "Other"),
        (AI, "Artificial Intelligence"),
        (WEB_DEV, "Web Development"),
        (MOBILE_DEV, "Mobile Development"),
        (DATA_SCIENCE, "Data Science & Analytics"),
        (CLOUD_COMPUTING, "Cloud Computing"),
        (CYBERSECURITY, "Cybersecurity"),
        (DEVOPS, "DevOps & Infrastructure"),
        (GAME_DEV, "Game Development"),
        (IOT, "Internet of Things"),
        (BLOCKCHAIN, "Blockchain & Cryptocurrency"),
    ]

    # Model fields
    # auto: auction_id
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(blank=True)
    current_price = models.DecimalField(max_digits=11, decimal_places=2, default=0.0)
    category = models.CharField(max_length=3, choices=CATEGORY, default=OTHER)
    image_url = models.URLField(blank=True)
    publication_date = models.DateTimeField(auto_now_add=True)
    closed = models.BooleanField(default=False)
    supporting_link = models.URLField(blank=True, verbose_name="SupportingLink")
    supporting_link_description = models.CharField(max_length=100, blank=True, verbose_name="SupportingLinkDescription")
    images = models.ManyToManyField('AuctionImage',related_name='auctions', blank=True)
    videos = models.ManyToManyField('AuctionVideo', related_name='auctions', blank=True)

    class Meta:
        verbose_name = "auction"
        verbose_name_plural = "auctions"

    def __str__(self):
        return f"Auction id: {self.id}, title: {self.title}, seller: {self.seller}, supporting link: {self.supporting_link}"
    
    def delete(self, *args, **kwargs):
        # Delete related images
        for image in self.images.all():
            image.delete()
        
        # Delete related videos
        for video in self.videos.all():
            video.delete()
        
        # Call the "real" delete() method
        super().delete(*args, **kwargs)

class AuctionImage(models.Model):
    image = models.ImageField(
        upload_to='auction_images/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
            fileUtils.validate_file_size
        ]
    )
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Image for {self.auctions.first()}"

class AuctionVideo(models.Model):
    video = models.FileField(
        upload_to='auction_videos/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mov']),
            fileUtils.validate_file_size
        ]
    )
    caption = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Video for {self.auctions.first()}"

@receiver(pre_delete, sender=Auction)
def delete_auction_files(sender, instance, **kwargs):
    # Delete related images
    for image in instance.images.all():
        image.image.delete(save=False)
        image.delete()
    
    # Delete related videos
    for video in instance.videos.all():
        video.video.delete(save=False)
        video.delete()

class Bid(models.Model):
    """Contains all info about single bid:
        * price
        * who bid
        * when
        * on what auction
    """

    # Model fields
    # auto: bid_id
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_date = models.DateTimeField(auto_now_add=True)
    bid_price = models.DecimalField(max_digits=11, decimal_places=2)

    class Meta:
        verbose_name = "bid"
        verbose_name_plural = "bids"

    def __str__(self):
        return f"{self.user} bid {self.bid_price} $ on {self.auction}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=1000, blank=True)
    listings = models.ManyToManyField(Auction, related_name="user_profiles", blank=True)
    
    # New fields for contact information
    contact_email = models.EmailField(blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    contact_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    social_media = models.URLField(blank=True)

    def __str__(self):
        return f"Profile for {self.user}"

class Comment(models.Model):
    """Contains all info about single comment
        * content
        * who posted
        * when
        * on what auction
    """

    # Model fields
    # auto: comment_id
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(blank=False)
    comment_date = models.DateTimeField(auto_now_add=True, null=True)
    class Meta:
        verbose_name = "comment"
        verbose_name_plural = "comments"

    def __str__(self):
        return f"Comment {self.id} on auction {self.auction} made by {self.user}"

class Watchlist(models.Model):
    """Contains info about object on watchlist
        * which auction is on watchlist
        * on whose watchlist this auction is
    """
    # Model field
    # auto: watchlist_id
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")

    class Meta:
        verbose_name = "watchlist"
        verbose_name_plural = "watchlists"
        # Forces to not have auction duplicates for one user
        unique_together = ["auction", "user"]

    def __str__(self):
        return f"{self.auction} on user {self.user} watchlist"

from django.db.models.signals import pre_delete
pre_delete.connect(delete_auction_files, sender=Auction)