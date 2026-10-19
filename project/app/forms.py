# =============================================================================
# FILE: app/forms.py
# -----------------------------------------------------------------------------
# PURPOSE:  Defines the Django forms used across the site. A form declares which
#           model fields to show, how to render/validate them, and any extra
#           clean-up logic. Django handles rendering, validation, and saving.
# ROLE:     Sits between the HTML templates and the models: views instantiate
#           these forms, templates render them, and the forms write to models.py.
# USED BY:  views.py (imports every form here); templates render the forms.
# DEPENDS:  app/models.py for the CustomUser, Property, PropertyInquiry, Seminar
#           and CommissionSlip models.
# FORMS:    apply_form_control (helper), CustomUserCreationForm,
#           CustomAuthenticationForm, PropertyForm, PropertyInquiryForm,
#           SeminarForm, CommissionSlipForm.
# =============================================================================

# --- Imports -----------------------------------------------------------------
from django import forms
# Built-in form base classes for creating a user and for the login screen.
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import (
    CommissionSlip,
    CustomUser,
    Property,
    PropertyInquiry,
    Seminar,
)


# Field types that should get the shared 'box' CSS class applied (see below).
FORM_CONTROL_FIELDS = (forms.CharField, forms.EmailField, forms.DecimalField, forms.IntegerField, forms.URLField)


def apply_form_control(field):
    """Add the shared 'box' CSS class to a form field's widget.

    Applied to text-like inputs so every field is styled consistently. Checkboxes
    are skipped (they use their own styling). Any class already set on the widget
    is preserved and 'box' is appended. Modifies the field in place; returns None.
    """
    css_class = 'box'
    if isinstance(field.widget, forms.CheckboxInput):
        return
    existing = field.widget.attrs.get('class', '')
    field.widget.attrs['class'] = f"{existing} {css_class}".strip()

class CustomUserCreationForm(UserCreationForm):
    """Registration form for new accounts.

    Extends Django's UserCreationForm. Collects a full name, email, phone and
    the two password fields. Public sign-ups are always buyers; administrators
    can assign agent or broker roles from Django admin. On save it uses the email
    as the username so people log in with their email address.
    """
    # Extra field not on the base form: the person's full name.
    name = forms.CharField(max_length=150, label='Full name')

    class Meta:
        model = CustomUser
        # Do not expose user_type on public registration. Role assignment is an
        # administrator-only action in Django admin.
        fields = ['name', 'email', 'phone', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        # Apply the shared styling to each sign-up field.
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            apply_form_control(field)

    def clean_email(self):
        """Validate the email: normalise to lowercase and ensure it's unused.

        Rejects the submission if any existing user has the same email OR the
        same username (because usernames are set to the email on save).
        Returns the lowercased email, or raises ValidationError.
        """
        email = self.cleaned_data['email'].lower()
        if CustomUser.objects.filter(email__iexact=email).exists() or CustomUser.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError('Email already registered.')
        return email

    def save(self, commit=True):
        """Create the user, mapping form values onto model fields.

        Sets username and email to the (validated) email and first_name to the
        entered full name. If commit is True the user is written to the database.
        Returns the (unsaved or saved) CustomUser instance.
        """
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['name']
        # Enforce the public sign-up role even if a forged POST includes
        # user_type=agent or user_type=broker.
        user.user_type = 'buyer'
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Login form that accepts an email address instead of a username.

    Extends Django's AuthenticationForm. The visible field is labelled 'Email';
    behind the scenes it is translated to the matching account's username so
    Django's standard authentication still works.
    """
    # Relabel the inherited 'username' field as "Email" and type it as an email.
    username = forms.EmailField(label="Email")

    def __init__(self, request=None, *args, **kwargs):
        # Apply the shared 'box' styling to every field.
        super().__init__(request, *args, **kwargs)
        for field in self.fields.values():
            apply_form_control(field)

    def clean_username(self):
        """Turn the entered email into the username Django authenticates against.

        Looks up the account whose email matches (case-insensitive) and returns
        its username. If no account matches, the raw (lowercased) input is
        returned so authentication fails with the usual "invalid login" message
        rather than leaking whether the email exists.
        """
        email = self.cleaned_data['username'].lower()
        try:
            return CustomUser.objects.get(email__iexact=email).username
        except CustomUser.DoesNotExist:
            return email

class PropertyForm(forms.ModelForm):
    """Form agents use to create and edit a property listing.

    A ModelForm bound to Property. The owning 'agent' is set by the view, not the
    form, so it is not included in the field list. Extra gallery images are
    handled separately in the view (via the 'images' file input).
    """
    class Meta:
        model = Property
        # Editable listing fields. 'agent', 'created_at', 'is_deleted' are set by
        # the app, not the user, so they are intentionally left out.
        fields = [
            "title", "description", "property_type", "listing_status",
            "price", "location", "city", "province",
            "bedrooms", "bathrooms",
            "floor_area", "lot_area",
            "parking_spaces", "amenities", "image", "is_available"
        ]
        # Render the two long-text fields as multi-line boxes with helpful sizing.
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'amenities': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Pool, garden, balcony, security, etc.'}),
        }

    def __init__(self, *args, **kwargs):
        # Apply the shared 'box' styling to every field.
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            apply_form_control(field)

    def clean_image(self):
        """Validate the uploaded cover image size.

        Rejects images larger than 5 MB (5 * 1024 * 1024 bytes). Returns the
        image unchanged when valid, or raises ValidationError.
        """
        image = self.cleaned_data.get('image')
        if image and image.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Image must be 5MB or smaller.')
        return image


class PropertyInquiryForm(forms.ModelForm):
    """The "Contact Agent" form on a property's detail page.

    Collects the sender's name, email, optional phone, and message. The property
    and buyer are attached by the view, not the form.
    """
    class Meta:
        model = PropertyInquiry
        # Only the sender-provided fields; property/buyer are set in the view.
        fields = ['name', 'email', 'phone', 'message']
        widgets = {'message': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        # Apply the shared 'box' styling to every field.
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            apply_form_control(field)


class SeminarForm(forms.ModelForm):
    """Form brokers use to create and edit seminars.

    A ModelForm bound to Seminar. Uses native HTML date/time pickers for the date
    and time fields. The creating broker is set by the view, not the form.
    """
    class Meta:
        model = Seminar
        # Editable seminar fields; 'created_by' and timestamps are set by the app.
        fields = ['title', 'description', 'date', 'time', 'venue_or_link', 'speaker', 'attachment', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),      # Native date picker.
            'time': forms.TimeInput(attrs={'type': 'time'}),      # Native time picker.
            'description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        # Apply the shared 'box' styling to every field.
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            apply_form_control(field)


class CommissionSlipForm(forms.ModelForm):
    """Form brokers use to create and edit a commission slip.

    A ModelForm bound to CommissionSlip. The 'agent' dropdown is limited to users
    whose role is 'agent'. The commission amount itself is NOT editable here; it
    is calculated automatically by CommissionSlip.save().
    """
    class Meta:
        model = CommissionSlip
        # Editable fields. 'commission_amount' is auto-calculated, so it is omitted.
        fields = ['agent', 'property', 'client', 'sale_amount', 'commission_percentage', 'date_released', 'status']
        widgets = {'date_released': forms.DateInput(attrs={'type': 'date'})}  # Native date picker.

    def __init__(self, *args, **kwargs):
        # Restrict the agent choices to actual agents, then apply shared styling.
        super().__init__(*args, **kwargs)
        self.fields['agent'].queryset = CustomUser.objects.filter(user_type='agent')
        for field in self.fields.values():
            apply_form_control(field)
