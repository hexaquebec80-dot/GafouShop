from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import logout_user

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<int:id>/', views.product_detail, name='product_detail'),
    path('checkout/', views.checkout, name='checkout'),
   
    path("stripe/success/", views.stripe_success, name="stripe_success"),
    path("stripe/cancel/", views.stripe_cancel, name="stripe_cancel"),
    
    path('add-to-cart/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'), 
    path('login/', views.login_view, name='login'),
   
    path('register/', views.register, name='register'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    path('logout/', logout_user, name='logout'),
    path('cart/add/<int:id>/', views.add_quantity, name='add_quantity'),
    path('cart/remove/<int:id>/', views.remove_quantity, name='remove_quantity'),
    path('search/', views.search, name='search'),
    path('mode/', views.mode_page, name='mode'),
    path('mode/<str:type>/', views.mode_page, name='mode_type'),
    path('mode/<str:type>/', views.mode_page, name='mode'),
    
    path('beaute/', views.beaute_page, name='beaute'),
    path('beaute/<str:type>/', views.beaute_type, name='beaute_type'),
    path('hygiene/', views.hygiene_page, name='hygiene'),
    path('hygiene/<str:type_name>/', views.hygiene_type, name='hygiene_type'),
    path( 'remove-cart-item/<int:id>/',views.remove_cart_item,name='remove_cart_item' ),
    path(
    'add-mode-to-cart/<int:id>/',
    views.add_mode_to_cart,
    name='add_mode_to_cart'
    ),
    path(
    'add-hygiene-to-cart/<int:id>/',
    views.add_hygiene_to_cart,
    name='add_hygiene_to_cart'
    ),
    path(
    'add-beaute-to-cart/<int:product_id>/',
    views.add_beaute_to_cart,
    name='add_beaute_to_cart'
   ),

   path(
    'boutique-bloquee/',
    views.boutique_bloquee,
    name='boutique_bloquee'
  ),
  path('administration/', views.admin_dashboard, name='admin_dashboard'),
  path('administration/products/', views.admin_products, name='admin_products'),
  path('administration/orders/', views.admin_orders, name='admin_orders'),
  path('administration/payments/', views.admin_payments, name='admin_payments'),
  path('administration/add-product/', views.add_product, name='add_product'),
  
    # EDIT PRODUCT
  path('administration/edit-product/<int:id>/',views.edit_product,name='edit_product'),

    # DELETE PRODUCT
  path('administration/delete-product/<int:id>/',views.delete_product,name='delete_product'),

    # =========================
# ADMIN MODE
# =========================

  path('administration/mode/<str:type>/',views.admin_mode_type,name='admin_mode_type'),

# =========================
# ADMIN BEAUTE
# =========================

  path('administration/beaute/<str:type>/',views.admin_beaute_type,name='admin_beaute_type'),

# =========================
# ADMIN HYGIENE
# =========================

  path('administration/hygiene/<str:type_name>/',views.admin_hygiene_type,name='admin_hygiene_type'),


  path('administration/order/<int:order_id>/', views.admin_order_detail),

 path('administration/delete-order/<int:id>/',views.delete_order,name='delete_order'),

 path('administration/mode/<str:type>/',views.admin_mode_type,name='admin_mode_type'),

  path('administration/mode/modifier/<int:id>/',views.modifier_mode,name='modifier_mode'),

  path('administration/edit-mode/<int:id>/',views.edit_mode,name='edit_mode'),

 

  path("administration/edit-beaute/<int:id>/", views.edit_beaute,name="edit_beaute"),



  path("administration/edit-hygiene/<int:id>/",views.edit_hygiene,name="edit_hygiene"),

  path('administration/facture/<int:order_id>/', views.download_invoice,name='download_invoice'),

  path('administration/expedier-commande/<int:order_id>/',views.expedier_commande,name='expedier_commande'),
  path('administration/marquer-payee/<int:order_id>/',views.marquer_payee,name='marquer_payee'),
  path("administration/expedier-commande/<int:order_id>/",views.expedier_commande, name="expedier_commande"),
 


  path('favori/add/<int:product_id>/', views.add_favori,name='add_favori'),

  path('mode/favori/<int:mode_id>/',views.add_mode_favori,name='add_mode_favori'),
  path('hygiene/favori/<int:hygiene_id>/', views.add_hygiene_favori,name='add_hygiene_favori'),
  path('beaute/favori/<int:beaute_id>/', views.add_beaute_favori,name='add_beaute_favori'),



]
