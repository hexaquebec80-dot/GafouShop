from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now


from django.db import models

class Product(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField()
    
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to='products/')
    # 🔥 NOUVEAU (IMAGES SUPPLEMENTAIRES)
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', blank=True, null=True)

    # 🔥 VIDEO
    video = models.FileField(upload_to='products/videos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=10)

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 produits similaires manuels (admin)
    similar_products = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="related_to"  
    )

    def __str__(self):
        return self.nom

    # ✅ prix final propre
    def get_price(self):
        if self.prix_promo and self.prix_promo > 0:
            return self.prix_promo
        return self.prix

# PANIER
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class CartItem(models.Model):

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    mode = models.ForeignKey(
        "Mode",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    beaute = models.ForeignKey(
        "Beaute",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    hygiene = models.ForeignKey(
        "Hygiene",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    quantity = models.IntegerField(default=1)

# COMMANDE

class Order(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'En attente'),
        ('PAID', 'Payée'),
        ('PROCESSING', 'En traitement'),
        ('SHIPPED', 'Expédiée'),
        ('DELIVERED', 'Livrée'),
    )

    PAYMENT_CHOICES = (
        ('UNPAID', 'Non payé'),
        ('PAID', 'Payé'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    prenom = models.CharField(max_length=100)

    nom = models.CharField(max_length=100)

    email = models.EmailField()

    indicatif = models.CharField(max_length=10)

    telephone = models.CharField(max_length=30)

    pays = models.CharField(max_length=100)

    adresse = models.TextField()

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='UNPAID'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Commande #{self.id} - {self.prenom} {self.nom}"


# =========================
# ORDER ITEM
# =========================

class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.IntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return self.product.nom
    

    
# PAIEMENT
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)






class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    email = models.EmailField()

    def __str__(self):
        return f"{self.prenom} {self.nom}"
    


from django.db import models

class Mode(models.Model):

    TYPE_CHOICES = [
        ('homme', 'Hommes'),
        ('femme', 'Femmes'),
        ('enfant', 'Enfants'),
    ]

    nom = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    prix = models.DecimalField(max_digits=10, decimal_places=2)

    prix_promo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    image = models.ImageField(upload_to='modes/', blank=True, null=True)

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    stock = models.PositiveIntegerField(default=0)  # ✅ ajouté

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    # ✅ prix final (important)
    def get_price(self):
        if self.prix_promo and self.prix_promo < self.prix:
            return self.prix_promo
        return self.prix

    # 🔥 POURCENTAGE DE REDUCTION
    def reduction(self):
        if self.prix_promo and self.prix_promo < self.prix:
            reduction = ((self.prix - self.prix_promo) / self.prix) * 100
            return round(reduction)
        return 0
    




class Beaute(models.Model):

    TYPE_CHOICES = [
        ('cosmetique', 'Cosmétiques'),
        ('soin', 'Soins'),
    ]

    nom = models.CharField(max_length=200)
    description = models.TextField()

    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    image = models.ImageField(upload_to='beaute/')

    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    # ✅ PRIX FINAL (UTILISÉ PARTOUT)
    def get_price(self):
        if self.prix_promo and self.prix_promo < self.prix:
            return self.prix_promo
        return self.prix

    # 🔥 POURCENTAGE DE RÉDUCTION
    def reduction(self):
        if self.prix_promo and self.prix_promo < self.prix:
            reduction = ((self.prix - self.prix_promo) / self.prix) * 100
            return round(reduction)
        return 0
    




class Hygiene(models.Model):
    TYPE_CHOICES = [
        ('corps', 'Corps'),
        ('sante', 'Santé'),
    ]

    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    prix = models.FloatField()
    prix_promo = models.FloatField(blank=True, null=True)
    image = models.ImageField(upload_to='hygiene/')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.nom

    def get_price(self):
        if self.prix_promo and self.prix_promo < self.prix:
            return self.prix_promo
        return self.prix

    def reduction(self):
        if self.prix_promo and self.prix_promo < self.prix:
            return round(((self.prix - self.prix_promo) / self.prix) * 100)
        return 0




class Boutique(models.Model):
    nom = models.CharField(max_length=200)

    is_blocked = models.BooleanField(default=False)

    raison_blocage = models.TextField(
        blank=True,
        null=True
    )