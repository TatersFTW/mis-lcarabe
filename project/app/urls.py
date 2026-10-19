# =============================================================================
# FILE: app/urls.py
# -----------------------------------------------------------------------------
# PURPOSE:  Maps URL paths to view functions/classes for the whole application.
# ROLE:     Included by the project's root URL config (project/urls.py) at the
#           empty prefix '', so these paths are served from the site root.
#           Each path() gives a URL, the view that handles it, and a name used to
#           build links in templates ({% url 'name' %}).
# DEPENDS:  The views and view classes defined in app/views.py.
# NOTE:     The final block only serves uploaded MEDIA files while DEBUG=True
#           (development). In production a web server handles media instead.
# =============================================================================
from django.conf import settings
from django.conf.urls.static import static
# Django's built-in logout view; configured to return to the login page after.
from django.contrib.auth.views import LogoutView
from django.urls import path

# Every view this module routes to (functions and class-based views alike).
from .views import (
    AboutPageView,
    BrokerDashboardView,
    BuyerDashboardView,
    CommissionSlipCreateView,
    CommissionSlipDeleteView,
    CommissionSlipListView,
    CommissionSlipUpdateView,
    ListingsPageView,
    ManageAgentsView,
    ManagepropertiesView,
    SeminarCreateView,
    SeminarDeleteView,
    SeminarListView,
    SeminarUpdateView,
    ViewBuyersView,
    add_property,
    agent_dashboard_view,
    agents,
    contact_view,
    dashboard_redirect,
    delete_property,
    edit_property,
    export_commissions,
    home,
    login_view,
    partnerships,
    property_detail,
    register_seminar,
    register_view,
    search_properties,
    toggle_favorite,
)

urlpatterns = [
    # --- Public pages (no login required) ---
    path('', home, name='home'),                                   # Landing page.
    path('register/', register_view, name='register'),             # Sign-up form.
    path('login/', login_view, name='login'),                      # Login form.
    # Built-in logout; next_page sends the user to 'login' afterwards.
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    # Sends a logged-in user to the dashboard for their role.
    path('dashboard/', dashboard_redirect, name='dashboard_redirect'),
    path('about/', AboutPageView.as_view(), name='about'),         # About + reviews.
    path('contact/', contact_view, name='contact'),                # Contact page.
    path('agent/listings/', ListingsPageView.as_view(), name='listings'),  # All listings.
    path('search/', search_properties, name='search_properties'),  # Property search.

    # --- Single property ---
    path('property/<int:id>/', property_detail, name='property_detail'),        # Detail page.
    path('property/<int:id>/favorite/', toggle_favorite, name='toggle_favorite'),  # Save/unsave.

    # --- Broker-only pages ---
    path('broker_dashboard/', BrokerDashboardView.as_view(), name='broker_dashboard'),
    path('broker/agents/', ManageAgentsView.as_view(), name='manage_agents'),
    path('broker/properties/', ManagepropertiesView.as_view(), name='manage_properties'),

    # --- Agent pages ---
    path('agent/agents/', agents, name='agents'),                  # Public agent directory.
    path('agent/dashboard/', agent_dashboard_view, name='agent_dashboard'),
    path('agent/add-property/', add_property, name='add_property'),
    path('agent/edit-property/<int:id>/', edit_property, name='edit_property'),
    path('agent/delete-property/<int:id>/', delete_property, name='delete_property'),
    path('agent/buyers/', ViewBuyersView.as_view(), name='view_buyers'),

    # --- Buyer page ---
    path('buyer_dashboard/', BuyerDashboardView.as_view(), name='buyer_dashboard'),

    # --- Seminars (list is open to any logged-in user; the rest are role-gated) ---
    path('seminars/', SeminarListView.as_view(), name='seminar_list'),
    path('seminars/create/', SeminarCreateView.as_view(), name='seminar_create'),
    path('seminars/<int:pk>/edit/', SeminarUpdateView.as_view(), name='seminar_update'),
    path('seminars/<int:pk>/delete/', SeminarDeleteView.as_view(), name='seminar_delete'),
    path('seminars/<int:pk>/register/', register_seminar, name='seminar_register'),

    # --- Commission slips ---
    path('commissions/', CommissionSlipListView.as_view(), name='commission_list'),
    path('commissions/create/', CommissionSlipCreateView.as_view(), name='commission_create'),
    path('commissions/<int:pk>/edit/', CommissionSlipUpdateView.as_view(), name='commission_update'),
    path('commissions/<int:pk>/delete/', CommissionSlipDeleteView.as_view(), name='commission_delete'),
    path('commissions/export/', export_commissions, name='commission_export'),  # Excel download.

    # --- Partnerships ---
    path('partnerships/', partnerships, name='partnerships'),
]

# Development-only: serve user-uploaded media files (MEDIA_URL) straight from
# MEDIA_ROOT so images show up while DEBUG is on. Not used in production.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
