from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from .models import Product, CartItem, Sale, SaleItem, Category
from decimal import Decimal

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()
    search_query = request.GET.get('search')
    category = request.GET.get('category')
    
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(sku__icontains=search_query)
        )
    
    if category:
        products = products.filter(category_id=category)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category
    }
    return render(request, 'inventory/product_list.html', context)

@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        size = request.POST.get('size')
        color = request.POST.get('color')
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            messages.error(request, 'La cantidad debe ser mayor a 0')
            return redirect('product_detail', product_id=product_id)
            
        if quantity > product.stock:
            messages.error(request, 'No hay suficiente stock disponible')
            return redirect('product_detail', product_id=product_id)
            
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            product=product,
            size=size,
            color=color,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
            
        messages.success(request, 'Producto agregado al carrito')
        return redirect('cart')
    
    return redirect('product_list')

@login_required
def cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total = sum(item.get_total() for item in cart_items)
    return render(request, 'inventory/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, item_id):
    CartItem.objects.filter(id=item_id, user=request.user).delete()
    messages.success(request, 'Producto eliminado del carrito')
    return redirect('cart')

@login_required
@user_passes_test(lambda u: u.is_vendor())
def manage_inventory(request):
    products = Product.objects.all()
    total_inventory_value = products.aggregate(
        total=Sum(F('stock') * F('cost')))['total'] or 0
    total_potential_revenue = products.aggregate(
        total=Sum(F('stock') * F('price')))['total'] or 0
    total_potential_profit = total_potential_revenue - total_inventory_value
    
    context = {
        'products': products,
        'total_inventory_value': total_inventory_value,
        'total_potential_revenue': total_potential_revenue,
        'total_potential_profit': total_potential_profit,
    }
    return render(request, 'inventory/manage_inventory.html', context)

@login_required
@user_passes_test(lambda u: u.is_vendor())
def add_product(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        cost = request.POST.get('cost')
        stock = request.POST.get('stock')
        sku = request.POST.get('sku')
        category_id = request.POST.get('category')
        gender = request.POST.get('gender')
        colors = request.POST.getlist('colors')
        sizes = request.POST.getlist('sizes')
        image = request.FILES.get('image')

        product = Product.objects.create(
            name=name,
            description=description,
            price=Decimal(price),
            cost=Decimal(cost),
            stock=int(stock),
            sku=sku,
            category_id=category_id,
            gender=gender,
            colors=colors,
            sizes=sizes
        )
        
        if image:
            product.image = image
            product.save()
            
        messages.success(request, 'Producto agregado exitosamente')
        return redirect('manage_inventory')
        
    categories = Category.objects.all()
    return render(request, 'inventory/add_product.html', {'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_vendor())
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = Decimal(request.POST.get('price'))
        product.cost = Decimal(request.POST.get('cost'))
        product.stock = int(request.POST.get('stock'))
        product.sku = request.POST.get('sku')
        product.category_id = request.POST.get('category')
        product.gender = request.POST.get('gender')
        product.colors = request.POST.getlist('colors')
        product.sizes = request.POST.getlist('sizes')

        if 'image' in request.FILES:
            product.image = request.FILES['image']
            
        product.save()
        messages.success(request, 'Producto actualizado exitosamente')
        return redirect('manage_inventory')
        
    categories = Category.objects.all()
    return render(request, 'inventory/edit_product.html', {
        'product': product,
        'categories': categories
    })

@login_required
@user_passes_test(lambda u: u.is_vendor())
def sales_report(request):
    sales = Sale.objects.all()
    total_revenue = sales.aggregate(total=Sum('total'))['total'] or 0
    total_profit = sum(sale.get_total_profit() for sale in sales)
    
    context = {
        'sales': sales,
        'total_revenue': total_revenue,
        'total_profit': total_profit,
    }
    return render(request, 'inventory/sales_report.html', context)

@login_required
@user_passes_test(lambda u: u.is_vendor())
def search_product(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(sku__icontains=query) |
            Q(name__icontains=query)
        )
        return JsonResponse({
            'products': list(products.values('id', 'name', 'sku', 'stock', 'price'))
        })