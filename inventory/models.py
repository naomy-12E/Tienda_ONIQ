from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Product(models.Model):
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('U', 'Unisex'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)  # Permitimos null temporalmente
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Valor predeterminado
    stock = models.IntegerField(default=0)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='U')
    colors = models.JSONField(default=list)  # Lista de colores disponibles
    sizes = models.JSONField(default=list)   # Lista de tallas disponibles
    sku = models.CharField(max_length=50, unique=True, default='')  # Valor predeterminado
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - SKU: {self.sku}"

    def get_profit(self):
        return self.price - self.cost

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
    added_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return self.quantity * self.product.price

class Sale(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='SaleItem')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def get_total_profit(self):
        return sum(item.get_profit() for item in self.saleitem_set.all())

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    cost_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)

    def get_profit(self):
        return (self.price_at_sale - self.cost_at_sale) * self.quantity