import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from .models import Product
from decimal import Decimal

from .models import (
    Product, Payment,
    Cart, CartItem,
    Order, OrderItem
)
def home(request):

    # 🔹 Tous les produits récents (max 20 affichés)
    products = Product.objects.all().order_by('-created_at')[:20]

    # 🔹 Produits promo (max 6)
    promo_products = Product.objects.filter(
        prix_promo__isnull=False,
        stock__gt=0
    ).order_by('-created_at')[:6]

    # 🔹 Produits disponibles (max 8)
    available_products = Product.objects.filter(
        stock__gt=0
    ).order_by('-created_at')[:8]

    # 🔥 Produits avec images (max 50)
    products_with_images = Product.objects.exclude(
        image=""
    ).exclude(
        image=None
    ).order_by('-created_at')[:50]

    return render(request, "home.html", {
        "products": products,
        "promo_products": promo_products,
        "available_products": available_products,
        "products_with_images": products_with_images,

        # 🔐 LOGIN MODAL
        "login_error": request.session.pop('login_error', None),
        "open_login_modal": request.session.pop('open_login_modal', False)
    })



def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    similar_products = product.similar_products.all()[:6]

    return render(request, "product_detail.html", {
        "product": product,
        "similar_products": similar_products
    })



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Cart, CartItem, Product


# =========================
# Récupérer panier utilisateur
# =========================
def get_cart(user):
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


# =========================
# Ajouter au panier
# =========================
@login_required
def add_to_cart(request, id):

    cart = get_cart(request.user)

    product = get_object_or_404(Product, id=id)

    # ✅ choisir bon prix
    if product.prix_promo and product.prix_promo > 0:
        final_price = product.prix_promo
    else:
        final_price = product.prix

    # ✅ créer item panier
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    # ✅ quantité
    if not created:
        item.quantity += 1
    else:
        item.quantity = 1

    # ✅ sauvegarder prix
    item.price = final_price

    item.save()

    messages.success(request, "Produit ajouté au panier ✅")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


# =========================
# Ajouter Mode au panier
# =========================
@login_required
def add_mode_to_cart(request, id):

    cart = get_cart(request.user)

    mode = get_object_or_404(Mode, id=id)

    # ✅ choisir bon prix
    if mode.prix_promo and mode.prix_promo > 0:
        final_price = mode.prix_promo
    else:
        final_price = mode.prix

    # ✅ créer item panier
    item, created = CartItem.objects.get_or_create(
        cart=cart,
        mode=mode
    )

    # ✅ quantité
    if not created:
        item.quantity += 1
    else:
        item.quantity = 1

    # ✅ sauvegarder prix
    item.price = final_price

    item.save()

    messages.success(request, "Produit mode ajouté au panier ✅")

    return redirect(request.META.get('HTTP_REFERER', 'home'))



from decimal import Decimal

@login_required
def cart_view(request):

    cart, _ = Cart.objects.get_or_create(user=request.user)

    items = CartItem.objects.filter(cart=cart)

    total = Decimal('0.00')

    for item in items:

        # PRODUCT
        if item.product:

            if item.product.prix_promo and item.product.prix_promo > 0:
                item.final_price = Decimal(str(item.product.prix_promo))
            else:
                item.final_price = Decimal(str(item.product.prix))

            item.name = item.product.nom
            item.image = item.product.image

        # MODE
        elif item.mode:

            if item.mode.prix_promo and item.mode.prix_promo > 0:
                item.final_price = Decimal(str(item.mode.prix_promo))
            else:
                item.final_price = Decimal(str(item.mode.prix))

            item.name = item.mode.nom
            item.image = item.mode.image

        # BEAUTE
        elif item.beaute:

            if item.beaute.prix_promo and item.beaute.prix_promo > 0:
                item.final_price = Decimal(str(item.beaute.prix_promo))
            else:
                item.final_price = Decimal(str(item.beaute.prix))

            item.name = item.beaute.nom
            item.image = item.beaute.image

        # HYGIENE
        elif item.hygiene:

            if item.hygiene.prix_promo and item.hygiene.prix_promo > 0:
                item.final_price = Decimal(str(item.hygiene.prix_promo))
            else:
                item.final_price = Decimal(str(item.hygiene.prix))

            item.name = item.hygiene.nom
            item.image = item.hygiene.image

        else:
            item.final_price = Decimal('0.00')
            item.name = "Produit"
            item.image = None

        item.total_price = item.final_price * item.quantity

        total += item.total_price

    return render(request, "cart.html", {
        "items": items,
        "total_price": total
    })
# =========================
# Ajouter hygiene au panier
# =========================
@login_required
def add_hygiene_to_cart(request, id):

    cart = get_cart(request.user)

    hygiene = get_object_or_404(Hygiene, id=id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        hygiene=hygiene
    )

    if not created:
        item.quantity += 1
    else:
        item.quantity = 1

    item.save()

    messages.success(request, "Produit hygiène ajouté au panier ✅")

    return redirect(request.META.get('HTTP_REFERER', 'home'))



from .models import Beaute
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

@login_required
def add_beaute_to_cart(request, product_id):

    product = get_object_or_404(Beaute, id=product_id) # type: ignore

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        beaute=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')



@login_required
def checkout(request):

    import paypalrestsdk

    from django.conf import settings
    from django.urls import reverse
    from django.shortcuts import redirect, render
    from django.http import JsonResponse

    # =========================
    # PAYPAL CONFIG
    # =========================

    paypalrestsdk.configure({

        "mode": settings.PAYPAL_MODE,

        "client_id": settings.PAYPAL_CLIENT_ID,

        "client_secret": settings.PAYPAL_CLIENT_SECRET,
    })

    # =========================
    # GET CART
    # =========================

    cart = get_cart(request.user)

    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items.exists():
        return redirect("cart")

    # =========================
    # TOTAL
    # =========================

    final_total = 0

    for item in cart_items:

        if item.product.prix_promo and item.product.prix_promo > 0:
            price = item.product.prix_promo
        else:
            price = item.product.prix

        final_total += price * item.quantity

    # =========================
    # SAVE ORDER + PAYPAL
    # =========================

    if request.method == "POST":

        # CREATE ORDER
        order = Order.objects.create(

            user=request.user,

            prenom=request.POST.get("prenom"),
            nom=request.POST.get("nom"),
            email=request.POST.get("email"),

            indicatif=request.POST.get("indicatif"),
            telephone=request.POST.get("telephone"),

            pays=request.POST.get("pays"),
            adresse=request.POST.get("adresse"),

            total=final_total,

            status="PENDING"
        )

        # =========================
        # SAVE PRODUCTS
        # =========================

        for item in cart_items:

            if item.product.prix_promo and item.product.prix_promo > 0:
                price = item.product.prix_promo
            else:
                price = item.product.prix

            OrderItem.objects.create(

                order=order,

                product=item.product,

                quantity=item.quantity,

                price=price
            )

        # =========================
        # PAYPAL PAYMENT
        # =========================

        payment = paypalrestsdk.Payment({

            "intent": "sale",

            "payer": {
                "payment_method": "paypal"
            },

            "redirect_urls": {

                "return_url": request.build_absolute_uri(
                    reverse("paypal_success")
                ),

                "cancel_url": request.build_absolute_uri(
                    reverse("paypal_error")
                ),
            },

            "transactions": [{

                "amount": {

                    "total": f"{final_total:.2f}",

                    "currency": "CAD"
                },

                "description": f"Commande GafouShop #{order.id}"
            }]
        })

        # =========================
        # CREATE PAYMENT
        # =========================

        if payment.create():

            # SAVE TRANSACTION ID
            order.transaction_id = payment.id
            order.save()

            # REDIRECT TO PAYPAL
            for link in payment.links:

                if link.rel == "approval_url":
                    return redirect(link.href)

        else:

            print(payment.error)

            return JsonResponse({

                "ok": False,

                "error": payment.error
            })

    # =========================
    # PAGE CHECKOUT
    # =========================

    return render(request, "checkout.html", {

        "cart_items": cart_items,

        "final_total": final_total
    })

import paypalrestsdk
from django.conf import settings
from django.urls import reverse
@login_required
def paypal_success(request):

    payment_id = request.GET.get("paymentId")

    payer_id = request.GET.get("PayerID")

    order = Order.objects.get(
        transaction_id=payment_id
    )

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({

        "payer_id": payer_id

    }):

        order.status = "PAID"
        order.save()

        # CLEAR CART
        cart = get_cart(request.user)

        CartItem.objects.filter(cart=cart).delete()

        return render(request, "order_success.html", {
            "order": order
        })

    return redirect("paypal_error")





# 💰 PAYPAL VERIFY (UNIQUE VERSION)
@login_required
def paypal_verify(request):
    try:
        data = json.loads(request.body)

        status = data.get("status")
        transaction_id = data.get("transaction_id")
        amount = data.get("amount")
        order_id = data.get("order_id")

        # 🔒 sécurité
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if status == "COMPLETED":

            order.status = "PAID"
            order.save()

            Payment.objects.create(
                user=request.user,
                order=order,
                amount=amount,
                transaction_id=transaction_id,
                status=status
            )

            # 📧 EMAIL CLIENT
            if request.user.email:
                send_mail(
                    "Commande confirmée",
                    f"Votre commande #{order.id} est confirmée.",
                    "noreply@gafoushop.com",
                    [request.user.email],
                    fail_silently=True
                )

            return JsonResponse({"ok": True})

        else:
            order.status = "CANCELLED"
            order.save()
            return JsonResponse({"ok": False})

    except Exception as e:
        print("Erreur PayPal:", e)
        return JsonResponse({"ok": False})


# ✅ SUCCESS
def success(request):
    return render(request, "success.html")


# ❌ ERROR
def error(request):
    return render(request, "error.html")



from .models import Cart, CartItem
from .models import Cart, CartItem
from django.contrib.auth import authenticate, login



def cart_count(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        count = CartItem.objects.filter(cart=cart).count()
    else:
        count = 0

    return {
        "cart_count": count
    }



def login_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not User.objects.filter(username=username).exists():
            return render(request, "login.html", {
                "error": "Ce compte n'existe pas."
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        return render(request, "login.html", {
            "error": "Mot de passe incorrect."
        })

    return render(request, "login.html")



from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile


def register(request):

    if request.method == "POST":

        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        telephone = request.POST.get('telephone')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # EMAIL EXISTE
        if User.objects.filter(email=email).exists():

            messages.error(
                request,
                "Cet email existe déjà."
            )

            return redirect('register')

        # USERNAME EXISTE
        if User.objects.filter(username=username).exists():

            messages.error(
                request,
                "Nom d'utilisateur déjà utilisé."
            )

            return redirect('register')

        # PASSWORD COURT
        if len(password) < 6:

            messages.error(
                request,
                "Le mot de passe doit contenir au moins 6 caractères."
            )

            return redirect('register')

        # CREER USER
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # CREER PROFILE
        Profile.objects.create(
            user=user,
            prenom=prenom,
            nom=nom,
            telephone=telephone,
            adresse=adresse,
            email=email
        )

        messages.success(
            request,
            "Compte créé avec succès ✅"
        )

        return redirect('login')

    return render(request, "register.html")

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

def logout_user(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté. Connectez-vous pour magasiner.")
    return redirect('home')




from django.shortcuts import redirect, get_object_or_404
from .models import CartItem

@login_required
def add_quantity(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)
    item.quantity += 1
    item.save()
    return redirect('cart')  # ou 'cart_view'


@login_required
def remove_quantity(request, id):
    item = get_object_or_404(CartItem, id=id, cart__user=request.user)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()  # supprime si 0

    return redirect('cart')




from django.shortcuts import render
from django.db.models import Q
from .models import Product

def search(request):
    query = request.GET.get('q')

    products = []

    if query:
        products = Product.objects.filter(
            Q(nom__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'search.html', {
        'products': products,
        'query': query
    })




from .models import Mode

def mode_page(request, type):
    products = Mode.objects.filter(type=type)

    context = {
        'products': products,
        'current_type': type
    }
    return render(request, 'mode.html', context)






from django.shortcuts import render
from .models import Beaute


# PAGE PRINCIPALE BEAUTE
def beaute_page(request):
    produits = Beaute.objects.all().order_by('-created_at')

    context = {
        'products': produits,
        'current_type': 'all'
    }
    return render(request, 'beaute.html', context)


# FILTRE PAR TYPE (cosmetique / soin)
def beaute_type(request, type):
    produits = Beaute.objects.filter(type=type).order_by('-created_at')

    context = {
        'products': produits,
        'current_type': type
    }
    return render(request, 'beaute.html', context)



from django.shortcuts import render
from .models import Hygiene

def hygiene_page(request):
    products = Hygiene.objects.all()
    return render(request, 'hygiene.html', {
        'products': products,
        'current_type': 'all'
    })


from django.shortcuts import render, get_object_or_404
from .models import Hygiene

def hygiene_type(request, type_name):

    # types autorisés (UX propre + sécurité)
    valid_types = ["corps", "sante"]

    if type_name not in valid_types:
        type_name = "corps"  # fallback propre

    products = Hygiene.objects.filter(type=type_name)

    return render(request, "hygiene.html", {
        "products": products,
        "current_type": type_name
    })



from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


from django.shortcuts import redirect

def remove_cart_item(request, id):
    try:
        item = CartItem.objects.get(id=id)
        item.delete()
    except CartItem.DoesNotExist:
        pass

    return redirect('cart')



from django.shortcuts import render
from .models import Boutique

def boutique_bloquee(request):

    boutique = Boutique.objects.filter(
        proprietaire=request.user
    ).first()

    return render(
        request,
        'boutique_bloquee.html',
        {
            'boutique': boutique
        }
    )





from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from .models import *

@staff_member_required
def admin_dashboard(request):

    products = Product.objects.count()
    orders = Order.objects.count()
    payments = Payment.objects.count()
    users = User.objects.count()

    context = {
        'products': products,
        'orders': orders,
        'payments': payments,
        'users': users,
    }

    return render(request, 'admin_dashboard.html', context)


@staff_member_required
def admin_products(request):

    products = Product.objects.all().order_by('-id')

    return render(request, 'admin_products.html', {
        'products': products
    })


@staff_member_required
def admin_orders(request):

    orders = Order.objects.all().order_by('-id')

    return render(request, 'admin_orders.html', {
        'orders': orders
    })


@staff_member_required
def admin_payments(request):

    payments = Payment.objects.all().order_by('-id')

    return render(request, 'admin_payments.html', {
        'payments': payments
    })



# views.py

from django.shortcuts import render, redirect
from .models import Product, Mode, Beaute, Hygiene


def add_product(request):

    if request.method == "POST":

        categorie = request.POST.get("categorie")

        nom = request.POST.get("nom")
        description = request.POST.get("description")

        prix = request.POST.get("prix")
        prix_promo = request.POST.get("prix_promo")

        stock = request.POST.get("stock")

        image = request.FILES.get("image")

        type_name = request.POST.get("type")

        # =========================
        # MODE
        # =========================
        if categorie == "mode":

            Mode.objects.create(
                nom=nom,
                description=description,
                prix=prix,
                prix_promo=prix_promo if prix_promo else None,
                image=image,
                type=type_name,
                stock=stock
            )

        # =========================
        # BEAUTE
        # =========================
        elif categorie == "beaute":

            Beaute.objects.create(
                nom=nom,
                description=description,
                prix=prix,
                prix_promo=prix_promo if prix_promo else None,
                image=image,
                type=type_name
            )

        # =========================
        # HYGIENE
        # =========================
        elif categorie == "hygiene":

            Hygiene.objects.create(
                nom=nom,
                description=description,
                prix=prix,
                prix_promo=prix_promo if prix_promo else None,
                image=image,
                type=type_name
            )

        # =========================
        # PRODUIT PRINCIPAL HOME
        # =========================
        elif categorie == "home":

            Product.objects.create(
                nom=nom,
                description=description,
                prix=prix,
                prix_promo=prix_promo if prix_promo else None,
                image=image,
                stock=stock
            )

        return redirect("admin_dashboard")

    return render(request, "add_product.html")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required

from .models import Product

# =========================
# EDIT PRODUCT
# =========================
# =========================
# EDIT PRODUCT
# =========================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product

def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == "POST":

        name = request.POST.get("name")
        price = request.POST.get("price")
        promo_price = request.POST.get("promo_price")
        stock = request.POST.get("stock")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        # =========================
        # Vérification champs obligatoires
        # =========================
        if not name or not price or not stock or not description:

            messages.error(
                request,
                "Tous les champs obligatoires doivent être remplis."
            )

            return render(request, "edit_product.html", {
                "product": product
            })

        # =========================
        # Vérification prix
        # =========================
        try:

            price = float(price)

            if price <= 0:

                messages.error(
                    request,
                    "Le prix doit être supérieur à 0."
                )

                return render(request, "edit_product.html", {
                    "product": product
                })

        except ValueError:

            messages.error(
                request,
                "Le prix est invalide."
            )

            return render(request, "edit_product.html", {
                "product": product
            })

        # =========================
        # Vérification prix promo
        # =========================
        if promo_price:

            try:

                promo_price = float(promo_price)

                if promo_price < 0:

                    messages.error(
                        request,
                        "Le prix promotionnel est invalide."
                    )

                    return render(request, "edit_product.html", {
                        "product": product
                    })

            except ValueError:

                messages.error(
                    request,
                    "Le prix promotionnel est invalide."
                )

                return render(request, "edit_product.html", {
                    "product": product
                })

        else:
            promo_price = None

        # =========================
        # Vérification stock
        # =========================
        try:

            stock = int(stock)

            if stock < 0:

                messages.error(
                    request,
                    "Le stock ne peut pas être négatif."
                )

                return render(request, "edit_product.html", {
                    "product": product
                })

        except ValueError:

            messages.error(
                request,
                "Le stock est invalide."
            )

            return render(request, "edit_product.html", {
                "product": product
            })

        # =========================
        # Mise à jour produit
        # =========================

        # ✅ IMPORTANT :
        # utiliser les vrais champs du model

        product.nom = name
        product.prix = price
        product.prix_promo = promo_price
        product.stock = stock
        product.description = description

        if image:
            product.image = image

        product.save()

        messages.success(
            request,
            "Produit modifié avec succès."
        )

        return redirect("admin_products")

    return render(request, "edit_product.html", {
        "product": product
    })

# =========================
# DELETE PRODUCT
# =========================
@staff_member_required
def delete_product(request, id):

    product = get_object_or_404(Product, id=id)

    product.delete()

    return redirect('admin_products')



# =========================
# ADMIN MODE
# =========================
from django.shortcuts import render, redirect, get_object_or_404
from .models import Mode, Beaute, Hygiene


# Afficher les produits par type
def admin_mode_type(request, type):

    modes = Mode.objects.filter(type=type)

    return render(request, 'admin_products.html', {
        'products': [],
        'modes': modes,
        'beautes': [],
        'hygienes': [],
    })


# Modifier un produit Mode
def modifier_mode(request, id):

    mode = get_object_or_404(Mode, id=id)

    if request.method == 'POST':
        mode.nom = request.POST.get('nom')
        mode.prix = request.POST.get('prix')
        mode.description = request.POST.get('description')
        mode.type = request.POST.get('type')

        # Image
        if request.FILES.get('image'):
            mode.image = request.FILES.get('image')

        mode.save()

        return redirect('admin_mode_type', type=mode.type)

    return render(request, 'modifier_mode.html', {
        'mode': mode
    })


# =========================
# ADMIN BEAUTE
# =========================

def admin_beaute_type(request, type):

    beautes = Beaute.objects.filter(type=type)

    return render(request, 'admin_products.html', {
        'products': [],
        'modes': [],
        'beautes': beautes,
        'hygienes': [],
    })


# =========================
# ADMIN HYGIENE
# =========================

def admin_hygiene_type(request, type_name):

    hygienes = Hygiene.objects.filter(type=type_name)

    return render(request, 'admin_products.html', {
        'products': [],
        'modes': [],
        'beautes': [],
        'hygienes': hygienes,
    })









def delete_order(request, id):

    order = get_object_or_404(Order, id=id)

    order.delete()

    return redirect('admin_orders')



def admin_order_detail(request, order_id):

    order = Order.objects.get(id=order_id)

    if request.method == "POST":

        order.prenom = request.POST.get('prenom')
        order.nom = request.POST.get('nom')
        order.email = request.POST.get('email')
        order.indicatif = request.POST.get('indicatif')
        order.telephone = request.POST.get('telephone')
        order.pays = request.POST.get('pays')
        order.adresse = request.POST.get('adresse')

        # IMPORTANT
        if request.POST.get('status'):
            order.status = request.POST.get('status')

        order.save()

    context = {
        'order': order
    }

    return render(request,
        'order_detail.html',
        context
    )

from django.shortcuts import render, redirect, get_object_or_404
from .models import Mode


# MODIFIER PRODUIT MODE
def edit_mode(request, id):

    # Chercher le produit
    mode = get_object_or_404(Mode, id=id)

    # Si formulaire envoyé
    if request.method == "POST":

        mode.nom = request.POST.get("nom")
        mode.description = request.POST.get("description")
        mode.type = request.POST.get("type")
        mode.prix = request.POST.get("prix")
        mode.prix_promo = request.POST.get("prix_promo")
        mode.stock = request.POST.get("stock")

        # Vérifier image
        if request.FILES.get("image"):
            mode.image = request.FILES.get("image")

        # Sauvegarder
        mode.save()

        # Retour administration
        return redirect("/administration/")

    # Afficher page
    return render(request, "edit_mode.html", {
        "mode": mode
    })

from django.shortcuts import render, redirect, get_object_or_404
from .models import Product

def edit_product(request, id):

    product = get_object_or_404(Product, id=id)

    if request.method == 'POST':

        product.nom = request.POST.get('name')
        product.prix = request.POST.get('price')
        product.prix_promo = request.POST.get('promo_price') or None
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        product.save()

        return redirect('admin_products')

    return render(request, 'edit_product.html', {
        'product': product
    })




from django.shortcuts import render, redirect, get_object_or_404
from .models import Beaute


# MODIFIER PRODUIT BEAUTÉ
def edit_beaute(request, id):

    # Chercher produit beauté
    beaute = get_object_or_404(Beaute, id=id)

    # Si formulaire envoyé
    if request.method == "POST":

        beaute.nom = request.POST.get("nom")
        beaute.description = request.POST.get("description")
        beaute.type = request.POST.get("type")
        beaute.prix = request.POST.get("prix")
        beaute.prix_promo = request.POST.get("prix_promo")

        # Vérifier image
        if request.FILES.get("image"):
            beaute.image = request.FILES.get("image")

        # Sauvegarder
        beaute.save()

        # Retour administration
        return redirect("/administration/")

    # Afficher page
    return render(request, "edit_beaute.html", {
        "beaute": beaute
    })




from django.shortcuts import render, redirect, get_object_or_404
from .models import Hygiene


# MODIFIER PRODUIT HYGIÈNE
def edit_hygiene(request, id):

    # Chercher produit
    hygiene = get_object_or_404(Hygiene, id=id)

    # Si formulaire envoyé
    if request.method == "POST":

        hygiene.nom = request.POST.get("nom")
        hygiene.description = request.POST.get("description")
        hygiene.type = request.POST.get("type")
        hygiene.prix = request.POST.get("prix")
        hygiene.prix_promo = request.POST.get("prix_promo")

        # Vérifier image
        if request.FILES.get("image"):
            hygiene.image = request.FILES.get("image")

        # Sauvegarder
        hygiene.save()

        # Retour administration
        return redirect("/administration/")

    # Afficher page
    return render(request, "edit_hygiene.html", {
        "hygiene": hygiene
    })