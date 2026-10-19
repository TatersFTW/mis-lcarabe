# =============================================================================
# FILE: app/views.py
# -----------------------------------------------------------------------------
# PURPOSE:  The controller layer. Each function/class here handles one or more
#           URLs: it reads the request, talks to the database via the models,
#           and returns a rendered template or a redirect.
# ROLE:     This is the "V" in Django's MVT pattern. URLs in app/urls.py point to
#           the views defined here. Most pages are function-based views; several
#           list/form pages use Django's class-based views (ListView, etc.).
# USES:     app/forms.py for validation and app/models.py for data.
# FLOW:     URL -> view -> models (DB) -> template -> HTML response.
# ACCESS:   Role-based. Brokers manage agents/seminars/commissions; agents manage
#           their own properties and see commissions; buyers browse, favorite and
#           inquire. Access is enforced by RoleRequiredMixin / role_required.
# =============================================================================

# --- Imports -----------------------------------------------------------------
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Count, Q and Sum power the dashboard statistics and search filters.
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import DeleteView, ListView, TemplateView, UpdateView

from .forms import (
    CommissionSlipForm,
    CustomAuthenticationForm,
    CustomUserCreationForm,
    PropertyForm,
    PropertyInquiryForm,
    SeminarForm,
)
from .models import (
    CommissionSlip,
    CustomUser,
    FavoriteProperty,
    Partner,
    Property,
    PropertyImage,
    PropertyInquiry,
    Review,
    Seminar,
    SeminarRegistration,
)


# --- Role helpers ------------------------------------------------------------
def role_dashboard_name(user):
    """Return the dashboard URL name that matches a user's role.

    Maps 'broker' -> 'broker_dashboard', 'agent' -> 'agent_dashboard', and
    everything else (including 'buyer') -> 'buyer_dashboard'. Used to send users
    to the right home page after login or when access is denied.
    """
    if user.user_type == 'broker':
        return 'broker_dashboard'
    if user.user_type == 'agent':
        return 'agent_dashboard'
    return 'buyer_dashboard'


class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin for class-based views that restricts access to certain roles.

    Set allowed_roles to a tuple of role codes. If the current user's role is not
    in that tuple, access is denied: anonymous users are sent to the login page,
    and logged-in users get an error message and are redirected to their own
    dashboard. test_func decides whether access is allowed.
    """
    allowed_roles = ()

    def test_func(self):
        # Allowed only if logged in AND the user's role is one of allowed_roles.
        return self.request.user.is_authenticated and self.request.user.user_type in self.allowed_roles

    def handle_no_permission(self):
        # Called when test_func returns False.
        if not self.request.user.is_authenticated:
            return redirect('login')
        messages.error(self.request, 'You do not have permission to access that page.')
        return redirect(role_dashboard_name(self.request.user))


def role_required(*roles):
    """Decorator for function-based views that restricts access to given roles.

    Usage: @role_required('agent'). Wraps the view so it first requires login
    (@login_required); if the user's role is not among *roles, it shows an error
    and redirects them to their own dashboard instead of running the view.
    """
    def decorator(view_func):
        @login_required
        def wrapped(request, *args, **kwargs):
            if request.user.user_type not in roles:
                messages.error(request, 'You do not have permission to access that page.')
                return redirect(role_dashboard_name(request.user))
            return view_func(request, *args, **kwargs)
        return wrapped
    return decorator


def dashboard_redirect(request):
    """Send a logged-in user to their role's dashboard; others to the login page."""
    if request.user.is_authenticated:
        return redirect(role_dashboard_name(request.user))
    return redirect('login')


def login_view(request):
    """Show and process the login form.

    GET  -> render the login page.
    POST -> validate credentials with CustomAuthenticationForm; on success log the
            user in, set an 8-hour session expiry, show a welcome message, and
            redirect to their role dashboard. Already-logged-in users are sent
            straight to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect(role_dashboard_name(request.user))

    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        request.session.set_expiry(60 * 60 * 8)  # 8-hour session.
        messages.success(request, f"Welcome back, {user.first_name or user.username} ({user.get_user_type_display()}).")
        return redirect(role_dashboard_name(user))
    return render(request, 'login.html', {'form': form})


def register_view(request):
    """Show and process the account sign-up form.

    GET  -> render the registration page.
    POST -> validate with CustomUserCreationForm; on success create the account,
            show a message, and redirect to the login page (the user must then log
            in). Already-logged-in users are redirected to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect(role_dashboard_name(request.user))

    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('login')
    return render(request, 'register.html', {'form': form})


def home(request):
    """Render the public home page.

    Shows the 6 most recent available listings, all partner logos, and the list of
    property types (for the search box). Open to everyone (no login required).
    """
    properties = Property.objects.filter(is_deleted=False).order_by('-created_at')[:6]
    partners = Partner.objects.all()
    return render(request, 'home.html', {
        'properties': properties,
        'partners': partners,
        'property_types': Property.PROPERTY_TYPE,
    })


class AboutPageView(TemplateView):
    """Public 'About Us' page.

    A simple TemplateView that also loads all client reviews (newest first) into
    the context so they can be displayed.
    """
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        # Add every Review, newest first, to the template context.
        context = super().get_context_data(**kwargs)
        context['reviews'] = Review.objects.order_by('-created_at')
        return context


class ListingsPageView(ListView):
    """Public page listing all currently-available properties.

    Uses Django's ListView: it queries the model and renders 'agent/listings.html'
    with the results under the context name 'properties'.
    """
    template_name = 'agent/listings.html'
    context_object_name = 'properties'

    def get_queryset(self):
        # Only show listings that are not soft-deleted and are marked available.
        return Property.objects.filter(is_deleted=False, is_available=True).order_by('-created_at')


class BrokerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """The broker's dashboard (broker role only).

    Aggregates high-level statistics (counts of agents, buyers, properties, active
    vs sold listings, total sales), plus lists of recent activity, recent
    commission slips, upcoming seminars, and per-agent performance.
    """
    allowed_roles = ('broker',)
    template_name = 'broker_dashboard.html'

    def get_context_data(self, **kwargs):
        # Gather the data the dashboard template needs.
        context = super().get_context_data(**kwargs)
        agents = CustomUser.objects.filter(user_type='agent')
        properties = Property.objects.filter(is_deleted=False).select_related('agent')
        # Total sales across all commission slips (sum of sale_amount); 0 if none.
        commission_total = CommissionSlip.objects.aggregate(total=Sum('sale_amount'))['total'] or 0
        context.update({
            'total_agents': agents.count(),
            'total_buyers': CustomUser.objects.filter(user_type='buyer').count(),
            'total_properties': properties.count(),
            # Available and not explicitly sold.
            'active_listings': properties.filter(is_available=True).exclude(listing_status='sold').count(),
            # Either flagged unavailable or explicitly marked sold.
            'sold_listings': properties.filter(Q(is_available=False) | Q(listing_status='sold')).count(),
            'monthly_sales': commission_total,
            'recent_properties': properties.order_by('-created_at')[:6],
            'recent_commissions': CommissionSlip.objects.select_related('agent', 'property')[:5],
            # Published seminars happening today or later.
            'upcoming_seminars': Seminar.objects.filter(status='published', date__gte=timezone.localdate())[:5],
            # Annotate each agent with how many properties and how much they sold.
            'agents': agents.annotate(property_count=Count('property'), sales_total=Sum('commission_slips__sale_amount'))[:8],
        })
        return context


class ManageAgentsView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Broker page to view and search agents (broker role only).

    Lists all agents, each annotated with their property count and total sales.
    Supports a text search (name/email/phone) and an active/inactive status filter
    via query parameters.
    """
    allowed_roles = ('broker',)
    template_name = 'broker/manage_agents.html'
    context_object_name = 'agents'

    def get_queryset(self):
        # Annotate agents with stats so the template can show them per row.
        queryset = CustomUser.objects.filter(user_type='agent').annotate(
            property_count=Count('property'),
            sales_total=Sum('commission_slips__sale_amount'),
        )
        # Optional search box (?q=...): match first name, email, or phone.
        query = self.request.GET.get('q')
        # Optional status filter (?status=active|inactive).
        status = self.request.GET.get('status')
        if query:
            queryset = queryset.filter(Q(first_name__icontains=query) | Q(email__icontains=query) | Q(phone__icontains=query))
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('first_name', 'email')


class ManagepropertiesView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Broker page to monitor all properties (broker role only).

    Lists every non-deleted property and supports filtering by agent, listing
    status, and property type via query parameters. The agents, property types and
    statuses lists are added to the context to populate the filter dropdowns.
    """
    allowed_roles = ('broker',)
    template_name = 'broker/manage_properties.html'
    context_object_name = 'properties'

    def get_queryset(self):
        queryset = Property.objects.filter(is_deleted=False).select_related('agent')
        # Read the three optional filters from the query string.
        agent = self.request.GET.get('agent')
        status = self.request.GET.get('status')
        property_type = self.request.GET.get('property_type')
        if agent:
            queryset = queryset.filter(agent_id=agent)
        if status:
            queryset = queryset.filter(listing_status=status)
        if property_type:
            queryset = queryset.filter(property_type=property_type)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        # Supply the dropdown options used by the filter form.
        context = super().get_context_data(**kwargs)
        context['agents'] = CustomUser.objects.filter(user_type='agent')
        context['property_types'] = Property.PROPERTY_TYPE
        context['statuses'] = Property.LISTING_STATUS
        return context


@role_required('agent')
def agent_dashboard_view(request):
    """The agent's dashboard (agent role only).

    Shows the agent's own listings, recent inquiries on their properties, upcoming
    seminars, recent commission slips, and counts of their total/active/sold
    properties.
    """
    buyers = CustomUser.objects.filter(user_type='buyer')
    properties = Property.objects.filter(agent=request.user, is_deleted=False).order_by('-created_at')
    commissions = CommissionSlip.objects.filter(agent=request.user).select_related('property')[:5]
    context = {
        'buyers': buyers,
        'properties': properties,
        'total_properties': properties.count(),
        'active_listings': properties.filter(is_available=True).exclude(listing_status='sold').count(),
        'sold_properties': properties.filter(Q(is_available=False) | Q(listing_status='sold')).count(),
        # Inquiries on any of this agent's properties (property__agent=request.user).
        'recent_inquiries': PropertyInquiry.objects.filter(property__agent=request.user)[:5],
        'upcoming_seminars': Seminar.objects.filter(status='published', date__gte=timezone.localdate())[:5],
        'commissions': commissions,
    }
    return render(request, 'agent_dashboard.html', context)


@role_required('agent')
def add_property(request):
    """Create a new property listing (agent role only).

    GET  -> show the empty property form.
    POST -> validate PropertyForm; attach the current user as the agent, save the
            listing, then save each uploaded gallery image (from the 'images' file
            input) up to 5 MB each. Redirect to the agent dashboard on success.
    """
    # request.FILES carries uploaded images; needed for both the cover and gallery.
    form = PropertyForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        property_instance = form.save(commit=False)
        property_instance.agent = request.user  # Assign the logged-in agent.
        property_instance.save()
        # Save any extra gallery images, ignoring files over the 5 MB limit.
        for img in request.FILES.getlist('images'):
            if img.size <= 5 * 1024 * 1024:
                PropertyImage.objects.create(property=property_instance, image=img)
        messages.success(request, 'Property listing created.')
        return redirect('agent_dashboard')
    return render(request, 'agent/add_property.html', {'form': form})


@role_required('agent')
def edit_property(request, id):
    """Edit one of the agent's own listings (agent role only).

    Loads the listing only if it belongs to the current agent and isn't deleted
    (otherwise 404). On a valid POST it saves the form, deletes any gallery images
    whose ids were checked for removal (delete_images), and adds any newly
    uploaded images (up to 5 MB each).
    """
    property_instance = get_object_or_404(Property, id=id, agent=request.user, is_deleted=False)
    form = PropertyForm(request.POST or None, request.FILES or None, instance=property_instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        # Remove gallery images the user ticked for deletion.
        PropertyImage.objects.filter(id__in=request.POST.getlist('delete_images'), property=property_instance).delete()
        # Add any newly uploaded gallery images (<= 5 MB each).
        for img in request.FILES.getlist('images'):
            if img.size <= 5 * 1024 * 1024:
                PropertyImage.objects.create(property=property_instance, image=img)
        messages.success(request, 'Property updated successfully.')
        return redirect('agent_dashboard')
    return render(request, 'agent/edit_property.html', {'form': form, 'property': property_instance})


@role_required('agent')
def delete_property(request, id):
    """Soft-delete one of the agent's own listings (agent role only).

    GET  -> show a confirmation page.
    POST -> mark the listing as deleted and unavailable (the row is kept in the
            database, just hidden) and redirect to the agent dashboard.
    """
    property_instance = get_object_or_404(Property, id=id, agent=request.user, is_deleted=False)
    if request.method == 'POST':
        # Soft delete: flag the row instead of removing it from the database.
        property_instance.is_deleted = True
        property_instance.is_available = False
        property_instance.save(update_fields=['is_deleted', 'is_available'])
        messages.success(request, 'Property removed from active listings.')
        return redirect('agent_dashboard')
    return render(request, 'agent/delete_property.html', {'property': property_instance})


def agents(request):
    """Public page listing all active agents.

    Shows every agent account that is currently active. Open to everyone.
    """
    agents_qs = CustomUser.objects.filter(user_type='agent', is_active=True)
    return render(request, 'agent/agents.html', {'agents': agents_qs})


class ViewBuyersView(LoginRequiredMixin, RoleRequiredMixin, ListView):
    """Agent page listing all registered buyers (agent role only).

    Shows buyer accounts, newest sign-ups first.
    """
    allowed_roles = ('agent',)
    template_name = 'agent/view_buyers.html'
    context_object_name = 'buyers'

    def get_queryset(self):
        return CustomUser.objects.filter(user_type='buyer').order_by('-date_joined')


class BuyerDashboardView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """The buyer's dashboard (buyer role only).

    Shows recommended (available) properties, the buyer's saved favorites, and a
    list of active agents to contact.
    """
    allowed_roles = ('buyer',)
    template_name = 'buyer_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['agents'] = CustomUser.objects.filter(user_type='agent', is_active=True)
        # A short list of the newest available listings as recommendations.
        context['properties'] = Property.objects.filter(is_deleted=False, is_available=True).order_by('-created_at')[:6]
        # The buyer's saved properties (with their property loaded in one query).
        context['favorites'] = FavoriteProperty.objects.filter(buyer=self.request.user).select_related('property')
        return context


def search_properties(request):
    """Search and filter properties (open to everyone).

    Reads filter values from the query string (city, location, property_type,
    listing_status, minimum bedrooms/bathrooms/areas, and price/area ranges) and
    applies each one that is present. Renders the matching listings.
    """
    properties = Property.objects.filter(is_deleted=False).select_related('agent')
    # Map each query-string parameter to a Django field lookup. Empty values are
    # skipped below, so blank inputs don't filter anything out.
    filters = {
        'city__icontains': request.GET.get('city'),          # partial, case-insensitive city match
        'location__icontains': request.GET.get('location'),
        'property_type': request.GET.get('property_type'),   # exact match
        'listing_status': request.GET.get('listing_status'),
        'bedrooms__gte': request.GET.get('bedrooms'),        # "at least N" comparisons
        'bathrooms__gte': request.GET.get('bathrooms'),
        'price__gte': request.GET.get('min_price'),          # price range: min/max
        'price__lte': request.GET.get('max_price'),
        'lot_area__gte': request.GET.get('lot_area'),
        'floor_area__gte': request.GET.get('floor_area'),
    }
    for lookup, value in filters.items():
        if value:
            properties = properties.filter(**{lookup: value})
    return render(request, 'search.html', {'properties': properties.order_by('-created_at'), 'property_types': Property.PROPERTY_TYPE})


def property_detail(request, id):
    """Show a single property's detail page and handle inquiries.

    GET  -> render the listing with a "Contact Agent" form pre-filled with the
            logged-in user's details (name/email/phone) when available.
    POST -> if the 'contact_agent' field is present and the form is valid, save a
            PropertyInquiry linked to this property (and to the buyer if logged
            in), show a confirmation, and redirect back to the same page.
    Also passes is_favorite so the template can show Save/Remove Favorite.
    """
    property_instance = get_object_or_404(Property, id=id, is_deleted=False)
    # Pre-fill the inquiry form for logged-in users; empty for guests.
    form = PropertyInquiryForm(request.POST or None, initial={
        'name': request.user.get_full_name() if request.user.is_authenticated else '',
        'email': request.user.email if request.user.is_authenticated else '',
        'phone': request.user.phone if request.user.is_authenticated else '',
    })
    # Only treat it as an inquiry when the form's hidden 'contact_agent' is sent.
    if request.method == 'POST' and 'contact_agent' in request.POST and form.is_valid():
        inquiry = form.save(commit=False)
        inquiry.property = property_instance
        inquiry.buyer = request.user if request.user.is_authenticated else None
        inquiry.save()
        messages.success(request, 'Your inquiry was sent to the agent.')
        return redirect('property_detail', id=property_instance.id)
    # Whether this buyer already saved the property (controls the button label).
    is_favorite = request.user.is_authenticated and FavoriteProperty.objects.filter(buyer=request.user, property=property_instance).exists()
    return render(request, 'view_property.html', {'property': property_instance, 'form': form, 'is_favorite': is_favorite})


@role_required('buyer')
def toggle_favorite(request, id):
    """Add or remove a property from the buyer's favorites (buyer role only).

    Uses get_or_create: if the favorite doesn't exist it is created (property
    saved); if it already exists it is deleted (property removed). Redirects back
    to the property page, or to the URL in the form's 'next' field if provided.
    """
    property_instance = get_object_or_404(Property, id=id, is_deleted=False)
    favorite, created = FavoriteProperty.objects.get_or_create(buyer=request.user, property=property_instance)
    if not created:
        # It already existed, so this click removes it.
        favorite.delete()
        messages.success(request, 'Property removed from saved list.')
    else:
        messages.success(request, 'Property saved.')
    return redirect(request.POST.get('next') or 'property_detail', id=property_instance.id)


def partnerships(request):
    """Public page showing all partner companies and their logos."""
    partners = Partner.objects.all()
    return render(request, 'partnership.html', {'partners': partners})


def contact_view(request):
    """Public contact page.

    GET  -> render the contact form.
    POST -> show a success message and redirect back. NOTE: the submitted fields
            are not stored anywhere; this is a placeholder acknowledgement only.
    """
    if request.method == 'POST':
        messages.success(request, 'Message sent successfully.')
        return redirect('contact')
    return render(request, 'contact.html')


class SeminarListView(LoginRequiredMixin, ListView):
    """List seminars (any logged-in user).

    Brokers see every seminar; agents and buyers only see 'published' ones (drafts
    are hidden). Rendered as a grid of cards.
    """
    template_name = 'seminars/list.html'
    context_object_name = 'seminars'

    def get_queryset(self):
        queryset = Seminar.objects.all()
        # Non-brokers can only see published seminars.
        if self.request.user.user_type != 'broker':
            queryset = queryset.filter(status='published')
        return queryset


class SeminarCreateView(LoginRequiredMixin, RoleRequiredMixin, View):
    """Create a seminar (broker role only).

    A plain View (rather than a generic CreateView) so the creating broker can be
    attached to the record before saving. Handles file uploads for attachments.
    """
    allowed_roles = ('broker',)

    def get(self, request):
        return render(request, 'seminars/form.html', {'form': SeminarForm(), 'title': 'Create Seminar'})

    def post(self, request):
        # request.FILES carries any uploaded attachment.
        form = SeminarForm(request.POST, request.FILES)
        if form.is_valid():
            seminar = form.save(commit=False)
            seminar.created_by = request.user  # Record which broker created it.
            seminar.save()
            messages.success(request, 'Seminar saved.')
            return redirect('seminar_list')
        return render(request, 'seminars/form.html', {'form': form, 'title': 'Create Seminar'})


class SeminarUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    """Edit an existing seminar (broker role only)."""
    allowed_roles = ('broker',)
    model = Seminar
    form_class = SeminarForm
    template_name = 'seminars/form.html'
    success_url = reverse_lazy('seminar_list')  # Where to go after a successful save.


class SeminarDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    """Delete a seminar (broker role only).

    Shows a confirmation page, then removes the seminar on POST.
    """
    allowed_roles = ('broker',)
    model = Seminar
    template_name = 'seminars/confirm_delete.html'
    success_url = reverse_lazy('seminar_list')


@role_required('agent')
def register_seminar(request, pk):
    """Register the current agent for a published seminar (agent role only).

    Uses get_or_create so clicking twice does not create a duplicate registration
    (the model also enforces uniqueness). Redirects back to the seminar list.
    """
    # Only allow registering for a published seminar; 404 otherwise.
    seminar = get_object_or_404(Seminar, pk=pk, status='published')
    SeminarRegistration.objects.get_or_create(seminar=seminar, agent=request.user)
    messages.success(request, 'You are registered for this seminar.')
    return redirect('seminar_list')


class CommissionSlipListView(LoginRequiredMixin, ListView):
    """List commission slips (any logged-in user, scoped by role).

    Brokers see all slips; agents see only their own. Supports a text search
    (client, property, or agent) and a status filter via query parameters.
    """
    template_name = 'commissions/list.html'
    context_object_name = 'commissions'

    def get_queryset(self):
        # select_related loads the related agent and property in the same query.
        queryset = CommissionSlip.objects.select_related('agent', 'property')
        # Agents only see their own commission slips.
        if self.request.user.user_type == 'agent':
            queryset = queryset.filter(agent=self.request.user)
        query = self.request.GET.get('q')
        status = self.request.GET.get('status')
        if query:
            # Match the search text against client name, property title, or agent name.
            queryset = queryset.filter(Q(client__icontains=query) | Q(property__title__icontains=query) | Q(agent__first_name__icontains=query))
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class CommissionSlipCreateView(LoginRequiredMixin, RoleRequiredMixin, View):
    """Create a commission slip (broker role only).

    A plain View (like SeminarCreateView). The commission amount is calculated
    automatically by the model's save(), so the form doesn't collect it.
    """
    allowed_roles = ('broker',)

    def get(self, request):
        return render(request, 'commissions/form.html', {'form': CommissionSlipForm(), 'title': 'Create Commission Slip'})

    def post(self, request):
        form = CommissionSlipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Commission slip saved.')
            return redirect('commission_list')
        return render(request, 'commissions/form.html', {'form': form, 'title': 'Create Commission Slip'})


class CommissionSlipUpdateView(LoginRequiredMixin, RoleRequiredMixin, UpdateView):
    """Edit a commission slip (broker role only)."""
    allowed_roles = ('broker',)
    model = CommissionSlip
    form_class = CommissionSlipForm
    template_name = 'commissions/form.html'
    success_url = reverse_lazy('commission_list')


class CommissionSlipDeleteView(LoginRequiredMixin, RoleRequiredMixin, DeleteView):
    """Delete a commission slip (broker role only)."""
    allowed_roles = ('broker',)
    model = CommissionSlip
    template_name = 'commissions/confirm_delete.html'
    success_url = reverse_lazy('commission_list')


@login_required
def export_commissions(request):
    """Download commission slips as an Excel (.xlsx) file.

    Brokers export all slips; agents export only their own. Anyone else is denied.
    Builds a spreadsheet with openpyxl and returns it as a file download.
    """
    queryset = CommissionSlip.objects.select_related('agent', 'property')
    if request.user.user_type == 'agent':
        queryset = queryset.filter(agent=request.user)
    elif request.user.user_type != 'broker':
        # Only brokers (all slips) and agents (their own) may export.
        messages.error(request, 'You do not have permission to export commissions.')
        return redirect(role_dashboard_name(request.user))

    # Imported here (not at module top) so it's only needed when exporting.
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Commission Details'
    # Header row for the spreadsheet columns.
    sheet.append(['Agent', 'Email', 'Property', 'Client', 'Sale Amount', 'Commission %', 'Commission Amount', 'Date Released', 'Status'])
    for slip in queryset:
        # Decimal values are converted to float because openpyxl writes numbers,
        # not Django Decimal objects. Dates are written as ISO text (or blank).
        sheet.append([
            slip.agent.get_full_name() or slip.agent.username,
            slip.agent.email,
            slip.property.title,
            slip.client,
            float(slip.sale_amount),
            float(slip.commission_percentage),
            float(slip.commission_amount),
            slip.date_released.isoformat() if slip.date_released else '',
            slip.get_status_display(),
        ])

    # Send the workbook back as a downloadable .xlsx file.
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="commission_slips.xlsx"'
    workbook.save(response)
    return response
