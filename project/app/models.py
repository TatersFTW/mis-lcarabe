# =============================================================================
# FILE: app/models.py
# -----------------------------------------------------------------------------
# PURPOSE:  Defines the database structure of the app. Each Python class here
#           becomes a database table, and each attribute becomes a column.
# ROLE:     This is the "M" in Django's MVT (Model-View-Template) pattern. The
#           ORM (Object-Relational Mapper) lets the rest of the code read/write
#           these objects instead of writing raw SQL.
# USED BY:  views.py and forms.py query these models; admin.py registers them in
#           the Django admin; migrations/ turn them into the database schema.
# MODELS:   CustomUser, Property, PropertyImage, Review, Partner,
#           FavoriteProperty, PropertyInquiry, Seminar, SeminarRegistration,
#           CommissionSlip.
# =============================================================================

# --- Imports -----------------------------------------------------------------
# models: base ORM classes (Model, fields like CharField/ForeignKey, validators).
from django.db import models
# AbstractUser: Django's built-in user (username, password, email, is_staff...).
# We extend it below instead of reinventing authentication from scratch.
from django.contrib.auth.models import AbstractUser
# settings: access project settings (e.g. AUTH_USER_MODEL for user relations).
from django.conf import settings
# Reusable validators: restrict file extensions and numeric ranges.
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator

class CustomUser(AbstractUser):
    """A user account, extended from Django's built-in user.

    Adds a phone number and a 'user_type' role that drives which dashboard and
    permissions a person gets. Roles: buyer, agent, broker (see USER_TYPE).
    """

    # Optional contact number (blank allowed).
    phone = models.CharField(max_length=15, blank=True, null=True)

    # The three roles used throughout the app to gate access and pick dashboards.
    USER_TYPE = (
        ('buyer', 'Buyer'),
        ('agent', 'Agent'),
        ('broker', 'Broker'),
    )

    # Stores the role code ('buyer' | 'agent' | 'broker'); defaults to 'buyer'.
    user_type = models.CharField(max_length=10, choices=USER_TYPE, default='buyer')

    # Flag the app can use to mark an account as verified (e.g. an agent confirmed
    # by a broker). Not automatically set anywhere in the code yet.
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        # Human-readable representation (used in admin lists, dropdowns, etc.).
        return self.username
    
class Property(models.Model):
    """A real-estate listing created by an agent.

    Holds descriptive details (price, location, size, status) plus a link back to
    the agent who owns the listing. 'is_deleted' enables a soft delete so listings
    disappear from the site without being erased from the database.
    """

    # Allowed categories for 'property_type' as (stored_value, display_label).
    PROPERTY_TYPE = [
        ('house_lot', 'House and Lot'),
        ('lot', 'Lot'),
        ('condominium', 'Condominium'),
        ('townhouse', 'Townhouse'),
        ('commercial', 'Commercial'),
    ]

    # Allowed listing statuses: on the market, reserved by a buyer, or sold.
    LISTING_STATUS = [
        ('sale', 'For Sale'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
    ]

    # --- Core text fields ---
    title = models.CharField(max_length=200)          # Short headline of the listing.
    description = models.TextField()                  # Long free-text description.

    # Category and current status, each restricted to the choices defined above.
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE,
        default='house_lot'
    )

    listing_status = models.CharField(
        max_length=10,
        choices=LISTING_STATUS,
        default='sale'
    )

    # Price in currency; DecimalField avoids floating-point rounding errors.
    price = models.DecimalField(max_digits=12, decimal_places=2)

    # --- Location ---
    location = models.CharField(max_length=255)       # Street / project / barangay.
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)

    # --- Rooms & areas ---
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()

    floor_area = models.DecimalField(max_digits=10, decimal_places=2)  # in sqm.
    lot_area = models.DecimalField(max_digits=10, decimal_places=2)    # in sqm.

    parking_spaces = models.IntegerField(default=0)   # Number of parking slots.
    amenities = models.TextField(blank=True)          # Free text, e.g. "pool, garden".

    # Primary/cover image uploaded to media/property_images/. Optional so a
    # listing can exist before an image is added.
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)

    # The agent who owns this listing. CASCADE means deleting the agent account
    # also deletes their property rows.
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Timestamp set automatically when the row is first created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Whether the listing is currently on the market (agents can toggle this).
    is_available = models.BooleanField(default=True)
    # Soft-delete flag: True hides the listing without removing the DB row.
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    @property
    def status_label(self):
        """A display-friendly status.

        Returns 'Sold' when the listing is explicitly sold OR simply marked
        unavailable; otherwise returns the human label for listing_status.
        A @property, so templates can use {{ property.status_label }}.
        """
        if self.listing_status == 'sold' or not self.is_available:
            return 'Sold'
        return self.get_listing_status_display()
    
class PropertyImage(models.Model):
    """An extra gallery photo belonging to a Property.

    Lets a listing carry many images. The reverse relation 'images' (see
    related_name) is used in templates, e.g. property.images.first.
    """
    # Link back to the owning listing. CASCADE: deleting the property deletes
    # its gallery images too. related_name='images' exposes property.images.all.
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    # The uploaded image file, stored under media/property_images/.
    image = models.ImageField(upload_to='property_images/')

    def __str__(self):
        return f"Image for {self.property.title}"
    
class Review(models.Model):
    """A client testimonial shown on the About page.

    Managed through the Django admin; displayed by AboutPageView in views.py.
    """
    name = models.CharField(max_length=100)                              # Reviewer's name.
    image = models.ImageField(upload_to='reviews/', blank=True, null=True)  # Optional avatar.
    rating = models.IntegerField(default=5)                              # Star rating (1-5 intended).
    comment = models.TextField()                                         # The testimonial text.
    created_at = models.DateTimeField(auto_now_add=True)                 # Set when created.

    def __str__(self):
        return self.name
    
class Partner(models.Model):
    """A partner/affiliate company whose logo is shown on the site.

    Managed through the Django admin; listed on the home and partnerships pages.
    """
    name = models.CharField(max_length=200)          # Company name.
    logo = models.ImageField(upload_to='partners/')  # Logo image in media/partners/.
    website = models.URLField()                      # Link opened when the logo is clicked.

    def __str__(self):
        return self.name


class FavoriteProperty(models.Model):
    """A property a buyer has saved to their favorites.

    Acts as a join table between a buyer and a property. The unique_together
    constraint below stops the same buyer saving the same property twice.
    """
    # The buyer who saved it. CASCADE: favorites vanish if the account is deleted.
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_properties')
    # The saved property. related_name='favorites' exposes property.favorites.
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)   # When it was saved.

    class Meta:
        # One buyer may save a given property only once.
        unique_together = ('buyer', 'property')
        # Newest favorites first when listing a buyer's saved properties.
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.buyer} saved {self.property}"


class PropertyInquiry(models.Model):
    """A message a visitor sends to a property's agent ("contact agent" form).

    Created by property_detail in views.py; surfaced to the agent on their
    dashboard under "recent inquiries".
    """
    # The property being asked about. CASCADE: inquiry removed if property is.
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    # Optional link to the logged-in buyer who sent it. SET_NULL keeps the
    # inquiry if the account is later deleted; blank/null so guests can inquire.
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name='property_inquiries')
    name = models.CharField(max_length=150)          # Sender's name (free text).
    email = models.EmailField()                      # Sender's email for replies.
    phone = models.CharField(max_length=30, blank=True)  # Optional contact number.
    message = models.TextField()                     # The inquiry message body.
    created_at = models.DateTimeField(auto_now_add=True) # When it was sent.

    class Meta:
        # Newest inquiries first.
        ordering = ['-created_at']

    def __str__(self):
        return f"Inquiry for {self.property.title} by {self.name}"


class Seminar(models.Model):
    """A training seminar/webinar created by a broker for agents.

    Only 'published' seminars are visible to agents (see SeminarListView); the
    broker dashboard also lists upcoming published ones. Managed in views.py by
    the Seminar*View classes.
    """
    # Publication state: a 'draft' is hidden from agents until 'published'.
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]

    title = models.CharField(max_length=200)          # Seminar title.
    description = models.TextField()                  # What the seminar covers.
    date = models.DateField()                         # Calendar date it happens.
    time = models.TimeField()                         # Start time.
    venue_or_link = models.CharField(max_length=255)  # Physical venue or online URL.
    speaker = models.CharField(max_length=150)        # Presenter's name.
    # Optional downloadable material. FileExtensionValidator restricts uploads
    # to common document/presentation types (no images, executables, etc.).
    attachment = models.FileField(
        upload_to='seminar_attachments/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xlsx', 'xls'])]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # draft|published.
    # Broker who created it. SET_NULL keeps the seminar if that user is deleted.
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Set on creation.
    updated_at = models.DateTimeField(auto_now=True)      # Auto-updated on every save.

    class Meta:
        # Listed chronologically by date then time.
        ordering = ['date', 'time']

    def __str__(self):
        return self.title


class SeminarRegistration(models.Model):
    """Records that an agent signed up for a seminar.

    Acts as a join table between an agent and a seminar. unique_together
    prevents the same agent registering for the same seminar more than once.
    """
    # The seminar being attended. CASCADE: registration removed if seminar is.
    seminar = models.ForeignKey(Seminar, on_delete=models.CASCADE, related_name='registrations')
    # The agent who registered. related_name exposes agent.seminar_registrations.
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seminar_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)  # When they signed up.

    class Meta:
        # One registration per (seminar, agent) pair.
        unique_together = ('seminar', 'agent')
        # Most recent sign-ups first.
        ordering = ['-registered_at']

    def __str__(self):
        return f"{self.agent} registered for {self.seminar}"


class CommissionSlip(models.Model):
    """A record of an agent's commission on a completed sale.

    Created/managed by brokers (see the CommissionSlip*View classes in views.py).
    Agents can view only their own slips and export them to Excel. The commission
    amount is computed automatically in save() from sale_amount and percentage.
    """
    # Workflow state of the slip.
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('released', 'Released'),
        ('paid', 'Paid'),
    ]

    # The agent earning the commission. related_name exposes agent.commission_slips.
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commission_slips')
    # The property that was sold. CASCADE: slip removed if the property is deleted.
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='commission_slips')
    client = models.CharField(max_length=150)  # Name of the buyer/client.
    # Monetary figures use DecimalField for exact currency math; 0 is the minimum.
    sale_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    # Percentage rate (0-100) applied to the sale amount.
    commission_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    # The resulting payout; recalculated automatically in save() below.
    commission_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    date_released = models.DateField(blank=True, null=True)  # When the commission was released.
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # draft|released|paid.
    created_at = models.DateTimeField(auto_now_add=True)  # Set on creation.
    updated_at = models.DateTimeField(auto_now=True)      # Auto-updated on every save.

    class Meta:
        # Most recently released (then most recently created) first.
        ordering = ['-date_released', '-created_at']

    def save(self, *args, **kwargs):
        """Recalculate commission_amount before writing to the database.

        Runs on every save (create or update). If both the sale amount and the
        percentage are present, commission_amount = sale_amount * percentage / 100,
        so the payout always matches the other two fields. Then it calls the
        normal Model.save() to actually persist the row.
        """
        if self.sale_amount is not None and self.commission_percentage is not None:
            self.commission_amount = (self.sale_amount * self.commission_percentage) / 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.agent} - {self.property} commission"
