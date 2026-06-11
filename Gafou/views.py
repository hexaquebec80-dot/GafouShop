import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from urllib3 import request
from .models import Product
from decimal import Decimal

from django.db.models import Count


from .models import (
    Product, Payment,
    Cart, CartItem,
    Order, OrderItem
)
def home(request):


    # 🔹 Tous les produits récents avec nombre de favoris
    products = Product.objects.annotate(
        total_favoris=Count('favoris')
    ).order_by('-created_at')[:20]

    # 🔹 Produits promo avec nombre de favoris
    promo_products = Product.objects.filter(
        prix_promo__isnull=False,
        stock__gt=0
    ).annotate(
        total_favoris=Count('favoris')
    ).order_by('-created_at')[:6]

    # 🔹 Produits disponibles avec nombre de favoris
    available_products = Product.objects.filter(
        stock__gt=0
    ).annotate(
        total_favoris=Count('favoris')
    ).order_by('-created_at')[:8]

    # 🔥 Produits avec images avec nombre de favoris

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

    ).annotate(
        total_favoris=Count('favoris')

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


import stripe

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .models import Order, OrderItem, Payment, CartItem



stripe.api_key = settings.STRIPE_SECRET_KEY


# =========================
# CHECKOUT + STRIPE
# =========================

@login_required
def checkout(request):

    cart = get_cart(request.user)
    cart_items = CartItem.objects.filter(cart=cart)

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
    # SAVE ORDER + STRIPE
    # =========================

    if request.method == "POST":

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
            status="PENDING",
            payment_status="PENDING"
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
        # STRIPE PAYMENT
        # =========================

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",

            line_items=[
                {
                    "price_data": {
                        "currency": "eur",
                        "product_data": {
                            "name": f"Commande GafouShop #{order.id}",
                        },
                        "unit_amount": int(final_total * 100),
                    },
                    "quantity": 1,
                }
            ],

            metadata={
                "order_id": order.id
            },

            success_url=request.build_absolute_uri(
                reverse("stripe_success")
            ) + "?session_id={CHECKOUT_SESSION_ID}",

            cancel_url=request.build_absolute_uri(
                reverse("stripe_cancel")
            ),
        )

        order.transaction_id = session.id
        order.save()

        return redirect(session.url)

    # =========================
    # PAGE CHECKOUT
    # =========================

    return render(request, "checkout.html", {
        "cart_items": cart_items,
        "final_total": final_total
    })


# =========================
# STRIPE SUCCESS
# =========================

@login_required
def stripe_success(request):

    session_id = request.GET.get("session_id")

    if not session_id:
        print("Aucun session_id reçu")
        return redirect("stripe_cancel")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        print("Erreur récupération session Stripe:", e)
        return redirect("stripe_cancel")

    try:
        metadata = session["metadata"]
        order_id = metadata["order_id"]
    except Exception as e:
        print("Erreur metadata Stripe:", e)
        return redirect("stripe_cancel")

    if not order_id:
        print("Aucun order_id dans metadata Stripe")
        return redirect("stripe_cancel")

    order = Order.objects.filter(
        id=order_id,
        user=request.user
    ).first()

    if not order:
        print("Commande introuvable:", order_id)
        return redirect("stripe_cancel")

    if session.payment_status == "paid":

        order.status = "PAID"
        order.payment_status = "PAID"
        order.transaction_id = session.id
        order.save()

        cart = get_cart(request.user)
        CartItem.objects.filter(cart=cart).delete()

        try:
            Payment.objects.get_or_create(
                transaction_id=session.id,
                defaults={
                    "user": request.user,
                    "order": order,
                    "amount": order.total,
                    "status": "COMPLETED"
                }
            )
        except Exception as e:
            print("Erreur enregistrement Payment:", e)

        try:
            envoyer_email_commande(order)
            print("EMAIL COMMANDE + FACTURE ENVOYÉ")
        except Exception as e:
            print("ERREUR EMAIL FACTURE :", e)

        return redirect("stripe_success_page")

    return redirect("stripe_cancel")


# =========================
# STRIPE CANCEL
# =========================

@login_required
def stripe_cancel(request):
    return render(request, "stripe_cancel.html")

from io import BytesIO
from django.template.loader import get_template
from django.core.mail import EmailMessage
from xhtml2pdf import pisa


def envoyer_email_commande(order):
    template = get_template("invoice_pdf.html")
    html = template.render({
        "order": order
    })

    pdf_file = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_file)

    if pisa_status.err:
        print("Erreur création PDF")
        return

    pdf_file.seek(0)

    email = EmailMessage(
        subject=f"Votre facture GafouShop - Commande #{order.id}",
        body=f"""
Bonjour {order.prenom},

Merci pour votre commande sur GafouShop.

Votre paiement a bien été reçu.
Vous trouverez votre facture professionnelle en pièce jointe.

Merci pour votre confiance.

GafouShop
""",
        from_email="GafouShop <gafoushop211@gmail.com>",
        to=[order.email],
    )

    email.attach(
        f"facture_gafoushop_{order.id}.pdf",
        pdf_file.getvalue(),
        "application/pdf"
    )

    email.send(fail_silently=False)



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



from django.shortcuts import render
from django.db.models import Count
from .models import Mode

def mode_page(request, type):

    products = Mode.objects.filter(
        type=type
    ).annotate(
        total_favoris=Count('favoris')
    ).order_by('-id')

    context = {
        'products': products,
        'current_type': type,
    }

    return render(request, 'mode.html', context)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Beaute, Favori


def beaute_page(request, type):

    products = Beaute.objects.filter(
        type=type
    ).annotate(
        total_favoris=Count('favoris', distinct=True)
    )

    return render(request, 'beaute.html', {
        'products': products,
        'current_type': type
    })

@login_required
def add_beaute_favori(request, beaute_id):

    beaute = get_object_or_404(Beaute, id=beaute_id)

    Favori.objects.get_or_create(
        user=request.user,
        beaute=beaute
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))


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


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from .models import Hygiene, Favori


def hygiene_page(request):

    products = Hygiene.objects.annotate(
        total_favoris=Count('favoris')
    ).order_by('-id')



from django.shortcuts import render
from .models import Hygiene

def hygiene_page(request):
    products = Hygiene.objects.all()

    return render(request, 'hygiene.html', {
        'products': products,
        'current_type': 'all'
    })

@login_required
def add_hygiene_favori(request, hygiene_id):

    hygiene = get_object_or_404(Hygiene, id=hygiene_id)

    Favori.objects.get_or_create(
        user=request.user,
        hygiene=hygiene
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))





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

from .models import Order


@staff_member_required
def admin_payments(request):
    payments = Order.objects.filter(
        payment_status="PAID"
    ).order_by('-id')

    total_amount = sum(
        order.total for order in payments
    )

    return render(
        request,
        'admin_payments.html',
        {
            'payments': payments,
            'total_amount': total_amount,
        }
    )



    payments = Payment.objects.all().order_by('-id')

    return render(request, 'admin_payments.html', {
        'payments': payments
    })



# views.p
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

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import os


def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="Facture_GafouShop_{order.id}.pdf"'
    )

    pdf = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=26,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=14,
    )

    normal = styles["Normal"]
    normal.fontSize = 10
    normal.leading = 14

    elements = []

    # =========================
    # LOGO + INFO ENTREPRISE
    # =========================
    logo_path = os.path.join(
        settings.BASE_DIR,
        "static",
        "images",
        "Gafoulogo.png"
    )

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=6 * cm, height=3.6 * cm)
    else:
        logo = Paragraph("<b>GafouShop</b>", title_style)

    company_info = Paragraph(
        """
        <font size="18" color="#0f766e"><b>GafouShop</b></font><br/><br/>
        Boutique en ligne<br/>
        Beauté • Cosmétiques • Hygiène • Mode<br/><br/>
        <b>Email :</b> gafoushop211@gmail.com<br/>
        <b>Facture générée automatiquement</b>
        """,
        normal
    )

    header_table = Table(
        [[logo, company_info]],
        colWidths=[7 * cm, 9 * cm]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(header_table)

    # =========================
    # TITRE
    # =========================
    elements.append(Paragraph(f"FACTURE #{order.id}", title_style))
    elements.append(Spacer(1, 10))

    status_text = "Payé reçu" if order.payment_status == "PAID" else "Non payé"

    info_data = [
        ["Date", order.created_at.strftime("%d/%m/%Y %H:%M")],
        ["Statut paiement", status_text],
        ["Transaction PayPal", order.transaction_id or "Aucune"],
    ]

    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#ecfdf5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 18))

    # =========================
    # CLIENT
    # =========================
    elements.append(Paragraph("<b>Informations client</b>", styles["Heading2"]))

    client_data = [
        ["Client", f"{order.prenom} {order.nom}"],
        ["Email", order.email],
        ["Téléphone", f"{order.indicatif} {order.telephone}"],
        ["Pays", order.pays],
        ["Adresse", order.adresse],
    ]

    client_table = Table(client_data, colWidths=[5 * cm, 11 * cm])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))

    elements.append(client_table)
    elements.append(Spacer(1, 22))

    # =========================
    # PRODUITS
    # =========================
    elements.append(Paragraph("<b>Produits commandés</b>", styles["Heading2"]))

    product_data = [["Produit", "Qté", "Prix unitaire", "Total"]]

    for item in order.orderitem_set.all():
        line_total = item.price * item.quantity

        product_data.append([
            item.product.nom,
            str(item.quantity),
            f"{item.price:.2f} €",
            f"{line_total:.2f} €",
        ])

    product_table = Table(
        product_data,
        colWidths=[7 * cm, 2 * cm, 3.5 * cm, 3.5 * cm]
    )

    product_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#fbfdff")),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # =========================
    # TOTAL
    # =========================
    total_table = Table(
        [["TOTAL À PAYER", f"{order.total:.2f} €"]],
        colWidths=[11 * cm, 5 * cm]
    )

    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 16),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 14),
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 18))

    # =========================
    # NOTE
    # =========================
    elements.append(Paragraph(
        "<font color='#16a34a'><b>✓ Paiement sécurisé via PayPal</b></font>",
        styles["Heading3"]
    ))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph(
        "Merci pour votre achat chez GafouShop. Cette facture est générée automatiquement et peut être conservée comme preuve d’achat.",
        normal
    ))

    pdf.build(elements)

    return response



from io import BytesIO
from django.core.mail import EmailMessage
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
import os




def generer_facture_pdf(order):
    buffer = BytesIO()

    pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=26,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=14,
    )

    normal = styles["Normal"]
    normal.fontSize = 10
    normal.leading = 14

    elements = []

    logo_path = os.path.join(settings.BASE_DIR, "static", "images", "Gafoulogo.png")

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=6 * cm, height=3.6 * cm)
    else:
        logo = Paragraph("<b>GafouShop</b>", title_style)

    company_info = Paragraph(
        """
        <font size="18" color="#0f766e"><b>GafouShop</b></font><br/><br/>
        Boutique en ligne<br/>
        Beauté • Cosmétiques • Hygiène • Mode<br/><br/>
        <b>Email :</b> gafoushop211@gmail.com<br/>
        <b>Facture générée automatiquement</b>
        """,
        normal
    )

    header_table = Table([[logo, company_info]], colWidths=[7 * cm, 9 * cm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
    ]))

    elements.append(header_table)

    elements.append(Paragraph(f"FACTURE #{order.id}", title_style))
    elements.append(Spacer(1, 10))

    status_text = "Payé reçu" if order.status == "PAID" else "Non payé"

    info_data = [
        ["Date", order.created_at.strftime("%d/%m/%Y %H:%M")],
        ["Statut paiement", status_text],
        ["Transaction PayPal", order.transaction_id or "Aucune"],
    ]

    info_table = Table(info_data, colWidths=[5 * cm, 11 * cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("BACKGROUND", (1, 0), (1, -1), colors.HexColor("#ecfdf5")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(info_table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("<b>Informations client</b>", styles["Heading2"]))

    client_data = [
        ["Client", f"{order.prenom} {order.nom}"],
        ["Email", order.email],
        ["Téléphone", f"{order.indicatif} {order.telephone}"],
        ["Pays", order.pays],
        ["Adresse", order.adresse],
    ]

    client_table = Table(client_data, colWidths=[5 * cm, 11 * cm])
    client_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(client_table)
    elements.append(Spacer(1, 22))

    elements.append(Paragraph("<b>Produits commandés</b>", styles["Heading2"]))

    product_data = [["Produit", "Qté", "Prix unitaire", "Total"]]

    for item in order.orderitem_set.all():
        line_total = item.price * item.quantity
        product_data.append([
            item.product.nom,
            str(item.quantity),
            f"{item.price:.2f} €",
            f"{line_total:.2f} €",
        ])

    product_table = Table(product_data, colWidths=[7 * cm, 2 * cm, 3.5 * cm, 3.5 * cm])
    product_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    total_table = Table(
        [["TOTAL PAYÉ", f"{order.total:.2f} €"]],
        colWidths=[11 * cm, 5 * cm]
    )

    total_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 16),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("PADDING", (0, 0), (-1, -1), 14),
    ]))

    elements.append(total_table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph(
        "Merci pour votre achat chez GafouShop. Cette facture est générée automatiquement.",
        normal
    ))

    pdf.build(elements)

    buffer.seek(0)
    return buffer


from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order
from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order

from django.shortcuts import get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Order


@staff_member_required
def expedier_commande(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    order.status = "SHIPPED"
    order.save()

    if not order.email:
        messages.error(request, "Aucun email client trouvé.")
        return redirect("/administration/orders/")

    try:
        resultat = send_mail(
            subject=f"Confirmation d'expédition - Commande #{order.id}",
            message=f"""
Bonjour {order.prenom},

Votre commande #{order.id} a été expédiée.

Si vous n'avez pas reçu votre commande, veuillez nous le signaler immédiatement.

Merci pour votre confiance.

Équipe GafouShop
""",
            from_email="GafouShop <gafoushop211@gmail.com>",
            recipient_list=[order.email],
            fail_silently=False,
        )

        print("RESULTAT EMAIL =", resultat)

        if resultat == 1:
            print("EMAIL VRAIMENT ENVOYE A", order.email)
        else:
            print("EMAIL NON ENVOYE")

    except Exception as e:
        print("ERREUR EMAIL =", e)
        messages.error(request, f"Erreur email : {e}")

    return redirect("/administration/orders/")



from django.shortcuts import get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.contrib import messages
from .models import Order


@staff_member_required
def marquer_payee(request, order_id):

    order = get_object_or_404(Order, id=order_id)

    order.payment_status = "PAID"
    order.status = "PAID"
    order.save()

    if order.email:
        try:
            send_mail(
                subject=f"Paiement confirmé - Commande #{order.id}",
                message=f"""Bonjour {order.prenom},

Nous confirmons la réception de votre paiement.

Numéro de commande : #{order.id}
Montant payé : {order.total} €
Statut : Payée

Merci pour votre confiance.

GafouShop
""",
                from_email=None,
                recipient_list=[order.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Commande marquée payée et email envoyé au client."
            )

        except Exception as e:
            messages.warning(
                request,
                f"Commande marquée payée, mais email non envoyé : {e}"
            )

    else:
        messages.warning(
            request,
            "Commande marquée payée, mais aucun email client trouvé."
        )

    return redirect("admin_orders")





def envoyer_email_commande(order):
    if not order.email:
        return

    pdf_buffer = generer_facture_pdf(order)

    email = EmailMessage(
        subject=f"Votre commande #{order.id} a été envoyée - Facture GafouShop",
        body=f"""
Bonjour {order.prenom},

Merci pour votre commande chez GafouShop.

Votre commande #{order.id} a bien été envoyée.

Vous trouverez votre facture en pièce jointe au format PDF.

Si vous n'avez pas reçu votre commande ou si vous constatez un problème, veuillez nous le signaler immédiatement en répondant à cet email.

Merci pour votre confiance.

Équipe GafouShop
""",
        from_email="GafouShop <gafoushop211@gmail.com>",
        to=[order.email],
    )

    email.attach(
        f"Facture_GafouShop_{order.id}.pdf",
        pdf_buffer.getvalue(),
        "application/pdf"
    )

    email.send(fail_silently=False)    



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Product,Favori

@login_required
def add_favori(request, product_id):

    product = get_object_or_404(Product, id=product_id)

    favori, created = Favori.objects.get_or_create(
        user=request.user,
        product=product
    )

    if created:
        messages.success(request, "Produit ajouté aux favoris.")
    else:
        messages.info(request, "Produit déjà dans vos favoris.")

    return redirect('product_detail', id=product.id)



from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Mode, Favori

@login_required
def add_mode_favori(request, mode_id):

    mode = get_object_or_404(Mode, id=mode_id)

    Favori.objects.get_or_create(
        user=request.user,
        mode=mode
    )

    return redirect(request.META.get('HTTP_REFERER', '/'))




