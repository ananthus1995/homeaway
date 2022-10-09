from django.db import models

import uuid

import math
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class Users(AbstractUser):
    gender_opt= (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other')
    )
    gender = models.CharField(choices=gender_opt, max_length=50)
    phone = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(_('email address'), unique=True)


class Profile(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE,related_name='users')
    bio = models.TextField(blank=True)
    dob = models.DateField(null=True, auto_now=False, auto_now_add=False)
    location = models.CharField(max_length=150, null=True)
    website = models.CharField(max_length=350, null=True)
    organisation = models.CharField(max_length=350, null= True)
    banner_img=models.ImageField(upload_to='user_banners', null=True)




class UserImages(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='userimg')
    user_img = models.ImageField(upload_to='user_images', null=True)

    def delete(self, *args, **kwargs):
        self.user_img.delete()
        return super(UserImages, self).delete(*args, **kwargs)


class UserSocialLinks(models.Model):
    user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name='user_links')
    fb_link = models.CharField(max_length=300, null=True,blank=True)
    insta_link = models.CharField(max_length=350, null=True, blank=True)
    youtube_link = models.CharField(max_length=350, null=True, blank=True)
    git_link = models.CharField(max_length=350, null=True, blank=True)




class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='user')
    image = models.ImageField(upload_to='post_images', null=True)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    liked = models.ManyToManyField(Users, blank=True, related_name='likes')
    updated = models.DateTimeField(auto_now=True)
    # no_of_likes = models.IntegerField(default=0)

    def num_likes(self):
        return self.liked.all().count()

    # def __str__(self):
    #     return self.user
    def get_date(self):

        now = timezone.now()

        diff = now - self.created_at

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:

            seconds = diff.seconds

            if seconds == 1:
                return str(seconds) + "second ago"

            else:
                return str(seconds) + " seconds ago"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            if minutes == 1:
                return str(minutes) + " minute ago"

            else:
                return str(minutes) + " minutes ago"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            if hours == 1:
                return str(hours) + " hour ago"

            else:
                return str(hours) + " hours ago"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 30:
            days = diff.days

            if days == 1:
                return str(days) + " day ago"

            else:
                return str(days) + " days ago"

        if diff.days >= 30 and diff.days < 365:
            months = math.floor(diff.days / 30)

            if months == 1:
                return str(months) + " month ago"

            else:
                return str(months) + " months ago"

        if diff.days >= 365:
            years = math.floor(diff.days / 365)

            if years == 1:
                return str(years) + " year ago"

            else:
                return str(years) + " years ago"




LIKE_CHOICES = (
    ('Like', 'Like'),
    ('Unlike', 'Unlike')
)

class Like(models.Model):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    value = models.CharField(choices=LIKE_CHOICES, max_length=20)
    # created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.value}"


class FollowersCount(models.Model):
    follower = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='followed_by')
    user = models.ForeignKey(Users, on_delete=models.CASCADE,related_name='followingto')
    status=models.CharField(max_length=50, default='pending')

    # def __str__(self):
    #     return self.user

class Comments(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE,related_name='posts')
    comments=models.TextField(blank=True)
    comment_by=models.ForeignKey(Users,on_delete=models.CASCADE,related_name='commented_user')

class Replies(models.Model):
    comment=models.ForeignKey(Comments,on_delete=models.CASCADE,related_name='post_comments')
    replie=models.TextField(blank=True)
    replied_by= models.ForeignKey(Users, on_delete=models.CASCADE ,related_name='replied_user')




