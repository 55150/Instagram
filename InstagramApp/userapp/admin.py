from django.contrib import admin
from .models import ( 
    Photo,
    Tag,
    Comment,
    Like,
    Follow,
    UserProfile,
    PhotoTag
    )

# Register your models here.
# admin.site.register(User)
admin.site.register(Photo)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(UserProfile)
admin.site.register(PhotoTag)
