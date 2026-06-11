from django.contrib import admin
from .models import Product, Order, Payment, OrderItem, Cart, CartItem
from django.utils.html import format_html



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    list_display = ('nom', 'prix','prix_promo', 'stock', 'created_at', 'preview')
    search_fields = ('nom',)
    list_filter = ('created_at',)
    filter_horizontal = ('similar_products',)

    # 🔥 ORGANISATION PRO
    fieldsets = (
        ("Infos produit", {
            'fields': ('nom', 'description', 'prix','prix_promo', 'stock')
        }),

        ("Images", {
            'fields': ('image', 'image2', 'image3', 'image4')
        }),

        ("Vidéo", {
            'fields': ('video',)
        }),

        ("Produits similaires", {
            'fields': ('similar_products',)
        }),
    )

    # 🔥 PREVIEW IMAGE DANS ADMIN
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" style="border-radius:5px;" />', obj.image.url)
        return "-"
    
    preview.short_description = "Image"


# 🔹 ORDER ITEM INLINE (afficher produits dans commande)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0

    readonly_fields = (
        'product',
        'quantity',
        'price',
    )
# =========================
# ORDER ITEM INLINE
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'prenom',
        'nom',
        'email',
        'telephone',
        'pays',
        'total',
        'status',
        'payment_status',

        'transaction_id',

        'created_at',
    )

    list_filter = (
        'status',
        'payment_status',
        'created_at',
        'pays',
    )

    search_fields = (
        'prenom',
        'nom',
        'email',
        'telephone',

        'transaction_id',

    )

    readonly_fields = (
        'created_at',

        'transaction_id',

    )

    inlines = [OrderItemInline]


# =========================
# ORDER ITEM ADMIN
# =========================

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'order',
        'product',
        'quantity',
        'price',
        'total_price',
    )

    search_fields = (
        'product__nom',
    )
# 🔹 PAIEMENT
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'order', 'amount', 'transaction_id', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('transaction_id',)


# 🔹 PANIER
@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'cart',
        'product',
        'mode',
        'beaute',
        'hygiene',
        'quantity'
    )




from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'prenom',
        'nom',
        'email',
        'telephone',
    )

    search_fields = (
        'user__username',
        'prenom',
        'nom',
        'email',
        'telephone',
    )

    list_filter = (
        'prenom',
        'nom',
    )

    ordering = ('nom',)

    fieldsets = (
        ('Compte utilisateur', {
            'fields': ('user',)
        }),
        ('Informations personnelles', {
            'fields': ('prenom', 'nom', 'email', 'telephone', 'adresse')
        }),
    )

admin.site.register(Profile, ProfileAdmin)



from django.contrib import admin
from .models import Mode


@admin.register(Mode)
class ModeAdmin(admin.ModelAdmin):

    # 🔥 colonnes affichées dans admin
    list_display = ('nom', 'type', 'prix', 'prix_promo', 'stock', 'image_preview')

    # 🔍 filtres à droite
    list_filter = ('type',)

    # 🔎 recherche
    search_fields = ('nom', 'description')

    # 📝 champs éditables directement
    list_editable = ('prix', 'prix_promo', 'stock')

    # 📄 pagination
    list_per_page = 20

    # 🖼️ aperçu image
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" style="border-radius:5px;" />'
        return "-"
    
    image_preview.allow_tags = True
    image_preview.short_description = "Image"






from .models import Beaute


@admin.register(Beaute)
class BeauteAdmin(admin.ModelAdmin):

    # ✅ Colonnes affichées
    list_display = (
        'nom',
        'type',
        'prix',
        'prix_promo',
        'prix_final',
        'reduction_percent',
        'created_at'
    )

    # ✅ Filtres à droite
    list_filter = ('type', 'created_at')

    # ✅ Barre de recherche
    search_fields = ('nom', 'description')

    # ✅ Tri par défaut
    ordering = ('-created_at',)

    # ✅ Champs éditables directement
    list_editable = ('prix', 'prix_promo')

    # ✅ Pagination
    list_per_page = 20

    # ✅ GROUPES (UI propre)
    fieldsets = (
        ("Informations produit", {
            'fields': ('nom', 'description', 'type')
        }),
        ("Prix", {
            'fields': ('prix', 'prix_promo')
        }),
        ("Image", {
            'fields': ('image',)
        }),
    )

    # ✅ AFFICHAGE PRIX FINAL
    def prix_final(self, obj):
        return f"{obj.get_price()} CAD"
    prix_final.short_description = "Prix final"

    # 🔥 AFFICHAGE REDUCTION %
    def reduction_percent(self, obj):
        if obj.reduction() > 0:
            return f"-{obj.reduction()}%"
        return "—"
    reduction_percent.short_description = "Promo"




    from django.contrib import admin
from .models import Hygiene

@admin.register(Hygiene)
class HygieneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type', 'prix', 'prix_promo', 'created_at')
    list_filter = ('type',)
    search_fields = ('nom',)


from django.contrib import admin
from .models import Favori

from django.contrib import admin
from .models import Favori


@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):

    list_display = (
        'user',
        'get_article',
        'get_type',
        'created_at',
    )

    list_filter = (
        'created_at',
        'user',
    )

    search_fields = (
        'user__username',
        'product__nom',
        'mode__nom',
        'hygiene__nom',
        'beaute__nom',
    )

    ordering = ('-created_at',)

    def get_article(self, obj):

        if obj.product:
            return obj.product.nom

        if obj.mode:
            return obj.mode.nom

        if obj.hygiene:
            return obj.hygiene.nom

        if hasattr(obj, 'beaute') and obj.beaute:
            return obj.beaute.nom

        return "-"

    get_article.short_description = "Article"

    def get_type(self, obj):

        if obj.product:
            return "Produit"

        if obj.mode:
            return "Mode"

        if obj.hygiene:
            return "Hygiène"

        if hasattr(obj, 'beaute') and obj.beaute:
            return "Beauté"

        return "-"

    get_type.short_description = "Catégorie"



from django.contrib import admin
from .models import Boutique

admin.site.register(Boutique)