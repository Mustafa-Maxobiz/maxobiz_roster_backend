# users/admin.py
from django.contrib import admin
from users.models.invites import Invitation

# ✅ Unregister if already registered to avoid AlreadyRegistered errors
try:
    admin.site.unregister(Invitation)
except admin.sites.NotRegistered:
    pass

@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """
    Admin for custom Invitation model.
    Uses only fields that definitely exist on the model.
    """
    # Fields to display - using __str__ which safely displays email and role
    list_display = ('id', '__str__', 'role')
    
    # Make id clickable
    list_display_links = ('id',)

    # Filters - only role which we know exists
    list_filter = ('role',)

    # Searchable fields - only role which we know exists
    search_fields = ('role',)
