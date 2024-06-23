from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm ,MySetPasswordForm
from . import views


urlpatterns = [
    path("", views.home, name="index"),
    path("category/<uuid:id>", views.CategoryView.as_view(), name="category"),
    path("product/<uuid:id>", views.ProductDetail.as_view(), name="product"),

    # ! ADD TO CART
    path('add-to-cart', views.add_to_cart, name='add_to_cart'),
    path('add-to-cart-quantity/', views.add_to_cart_quantity, name='add_to_cart_quantity'),
    path('cart', views.show_cart, name="show_cart"),
    path("checkout", views.CheckoutView.as_view(), name="checkout"),
    path("orders", views.OrderView.as_view(), name="orders"),



    # ! auth
    path("register", views.CustomerRegistrationView.as_view(), name="register"),
    path(
        "accounts/login",
        auth_view.LoginView.as_view(
            template_name="auth/login.html", authentication_form=LoginForm
        ),
        name="login",
    ),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("logout", auth_view.LogoutView.as_view(next_page="login"), name="logout"),
    # ! Password Change
    path(
        "password-change",
        auth_view.PasswordChangeView.as_view(
            template_name="auth/password_change.html",
            form_class=MyPasswordChangeForm,
            success_url="/password-change-done",
        ),
        name="password_change",
    ),
    path(
        "password-change-done",
        auth_view.PasswordChangeDoneView.as_view(
            template_name="auth/password_change_done.html",
        ),
        name="password_change_done",
    ),
    # ! Password Reset
    path(
        "password-reset",
        auth_view.PasswordResetView.as_view(
            template_name="auth/password_reset.html", 
            form_class=MyPasswordResetForm
        ),
        name="password_reset",
    ),
    path(
        "password-reset-done",
        auth_view.PasswordResetDoneView.as_view(
            template_name="auth/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>",
        auth_view.PasswordResetConfirmView.as_view(
            template_name="auth/password_reset_confirm.html",
            form_class=MySetPasswordForm,
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset-complete",
        auth_view.PasswordResetCompleteView.as_view(
            template_name="auth/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Admin Site Header"
admin.site.site_title = "Admin Site Title"
admin.site.site_index_title = "Welcome to Admin Shop"