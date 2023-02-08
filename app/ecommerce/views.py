from django.shortcuts import render, redirect

from .models import Category, Item, Attribute,ItemsInventory,ItemsImage
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.views import View
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.contrib import messages
from django.db.models import Max, Q

import os
from django.core.mail import send_mail, EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.conf import settings

from .cart import Cart
from account.models import Customer, Address
from order.models import Order, OrderItem, OrderStatus
# import pagination
from django.core.paginator import Paginator
from account.forms import AnonymousCustomerForm, AddressForm

def redirect_home(request):
    return redirect(reverse('ecommerce:shop-all'))

class CheckOutView(View):
    template_pickup = 'checkout-pickup.html'
    template_ship = 'checkout-ship.html'
    template_confirmation = 'order-confirmation.html'
    
    attr = Attribute.objects.all()

    def get(self, request, shipping_method):
        if request.user.is_authenticated:
            customer = Customer.objects.get(email=request.user.email)
            form = AnonymousCustomerForm(instance=customer)
            try: 
                address = Address.objects.filter(customer_id=customer, default=True).latest('date_created')
                form2 = AddressForm(instance = address)
            except Address.DoesNotExist:
                form2 = AddressForm()
        else: 
            form = AnonymousCustomerForm()
            form2 = AddressForm()
                
        cart = Cart(request)
        SKU = [i['product'] for i in cart]
        ordered_item = ItemsInventory.objects.filter(SKU__in = SKU)

        context = {'ordered_items' : ordered_item,
                    'cart_length' : cart.__len__(),
                    'cart' : cart,
                    'category' : get_shop_categories(),
                    }

        if shipping_method == 'pickup':
            context['form'] = form
            context['sub_total'] = round(cart.get_total_price(),2)
            context['total'] = round(cart.get_total_price(),2)
            return render(request, self.template_pickup, context)
        elif shipping_method == 'shiptohome':
            context['form'] = form
            context['form2'] = form2
            context['ship_cost'] = float(self.attr.get(parent_name='Shipping Cost').name)
            context['sub_total'] = round(cart.get_total_price(),2)
            context['total'] = round(cart.get_total_price(),2) + float(self.attr.get(parent_name='Shipping Cost').name)
            return render(request, self.template_ship, context)
        else:
            raise Http404('Page not found')

    def post(self, request, shipping_method):
        
        cart = Cart(request).__dict__.get('cart')
        if cart.__len__() == 0:
            messages.error(request, "Nothing in your cart",extra_tags='outofstock')
            return redirect(reverse('ecommerce:checkout',args=[shipping_method])) 

        try:
            customer = Customer.objects.get(email=request.POST.get('email'))
            form = AnonymousCustomerForm(request.POST, instance = customer)
        except Customer.DoesNotExist:
            form = AnonymousCustomerForm(request.POST)

        # Validation to check if items still available
        ordered_item = ItemsInventory.objects.filter(SKU__in = list(cart.keys()))
        for i in ordered_item:
            for j in cart:
                if i.SKU == j:
                    if cart[j].get('qty') > i.quantity:
                        messages.error(request, "Checkout error, '{0}' more than our inventory".format(i.item_id.title)
                                        ,extra_tags='outofstock')
                        return redirect(reverse('ecommerce:checkout',args=[shipping_method])) 
        if form.is_valid():
                form.save()
                customer = Customer.objects.get(email=form.cleaned_data.get('email'))
        
        if shipping_method == 'pickup':
            order_type_value=self.attr.get(name=shipping_method)
            new_order  = Order.objects.create(customer_id=customer,
                                                    discount_amount = 0,
                                                    order_type = order_type_value,
                                                    shipping_price = float(request.POST.get('shipcost')),
                                                    subtotal = float(request.POST.get('subtotal')),
                                                    undiscounted_total = float(request.POST.get('subtotal')),
                                                    total_net = float(request.POST.get('totalnet')),
                                                    created_by = form.cleaned_data.get('email')
                                                    )
            
            
            default_status = self.attr.get(name='Received')
            OrderStatus.objects.create(order_id=new_order,
                                        status = default_status,
                                        created_by = form.cleaned_data.get('email')
                                        )
            for i in cart:
                SKU = ordered_item.get(SKU=i)
                OrderItem.objects.create(order_id=new_order,
                                        SKU = SKU,
                                        quantity = cart[i].get('qty')
                                        )
            Cart(request).clear()
        else:
            try:
                child = Address.objects.get(customer_id=customer,
                                            street_address=str(request.POST.get('street_address')),
                                            apartment_address=str(request.POST.get('apartment_address')),
                                            city=str(request.POST.get('city')),
                                            state=str(request.POST.get('state')),
                                            zip=str(request.POST.get('zip'))
                                            )
                if request.user.is_authenticated and request.POST.get('default') == 'on':
                    if not child.default:
                        try:
                            unsaved_address = Address.objects.get(customer_id=customer,default=True)
                            unsaved_address.default = False
                            unsaved_address.save()
                        except Address.DoesNotExist:
                            pass
                        child.default = True
                        child.save()                   
            except Address.DoesNotExist:
                if request.user.is_authenticated and request.POST.get('default') == 'on':
                    try:
                        unsaved_address = Address.objects.get(customer_id=customer,default=True)
                        unsaved_address.default = False
                        unsaved_address.save()
                    except Address.DoesNotExist:
                        pass
                    form2 = AddressForm(request.POST)
                    if form2.is_valid():
                        child = form2.save(commit=False)
                        child.customer_id = customer
                        child.save()
                elif request.user.is_authenticated and not request.POST.get('default'):
                    form2 = AddressForm(request.POST)
                    if form2.is_valid():
                        child = form2.save(commit=False)
                        child.customer_id = customer
                        child.save()
                else:
                    form2 = AddressForm(request.POST)
                    if form2.is_valid():
                        child = form2.save(commit=False)
                        child.customer_id = customer
                        child.save()
            
                
            order_type_value=self.attr.get(name=shipping_method)
            new_order  = Order.objects.create(customer_id=customer,
                                                    discount_amount = 0,
                                                    order_type = order_type_value,
                                                    shipping_address = child,
                                                    shipping_price = float(request.POST.get('shipcost')),
                                                    subtotal = float(request.POST.get('subtotal')),
                                                    undiscounted_total = float(request.POST.get('subtotal')),
                                                    total_net = float(request.POST.get('totalnet')),
                                                    created_by = form.cleaned_data.get('email')
                                                    )
            default_status = self.attr.get(name='Received')
            OrderStatus.objects.create(order_id=new_order,
                                        status = default_status,
                                        created_by = form.cleaned_data.get('email')
                                        )
            for i in cart:
                SKU = ordered_item.get(SKU=i)
                OrderItem.objects.create(order_id=new_order,
                                        SKU = SKU,
                                        quantity = cart[i].get('qty')
                                        )
            Cart(request).clear()
        
        order_items = OrderItem.objects.filter(order_id = new_order)

        context = { 'cart_length' : Cart(request).__len__(),
                    'cart' : Cart(request),
                    'category' : get_shop_categories(),
                    'order_ref_id' : new_order,
                    'ordered_items': order_items}
        
        
        subject = 'VietAoDaiBoutique Order Confirmation'

        html_content = render_to_string('email/order-email.html', context)
        receipient = [form.cleaned_data.get('email')]

        msg = EmailMultiAlternatives(subject, html_content, 'vietaodaiwebapp@gmail.com' , to = receipient)
        msg.content_subtype = 'html'  # Main content is text/html
        msg.mixed_subtype = 'related'  # This is critical, otherwise images will be displayed as attachments!

        for view in order_items:
            image = MIMEImage(view.SKU.item_id.images.read())
            image.add_header('Content-ID', '<{}>'.format(view.SKU.item_id.filename()))
            image.add_header('Content-Disposition', 'inline', filename=view.SKU.item_id.filename())
            msg.attach(image)

        logo = 'assets/images/logo.png'
        resolved_path = os.path.join(settings.STATIC_ROOT, logo)

        with open(resolved_path, 'rb') as f:
            img = MIMEImage(f.read())
            img.add_header('Content-ID', '<{name}>'.format(name='logo.png'))
            img.add_header('Content-Disposition', 'inline', filename='logo.png')
        msg.attach(img)

        msg.send()

        return render(request, self.template_confirmation, context)


def get_shop_categories():
    ''' category for dropdown navbar'''
    category_results = Category.objects.filter(hierarchy_level=2, 
                                               date_deleted__isnull=True,
                                              )
    return category_results

class LookbookView(View):
    template = 'lookbook.html'

    def get(self, request):
              
        # Set up pagination
        item = Item.objects.filter(date_deleted__isnull=True).order_by('-item_id')
       
        paginator = Paginator(item, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = { 'category' : get_shop_categories(),
                    'page_obj' : page_obj,
                    'cart_length' : Cart(request).__len__(),
                    }


        return render(request, self.template, context)

class ShopView(View):
    template = 'shop.html'

    def get(self, request):

        attr = Attribute.objects.all()
        attribute_results = attr.filter(hierarchy_level=1, 
                                                    date_deleted__isnull=True,
                                                    is_filtered = True)
        attribute = attr.filter(hierarchy_level = 2, 
                                        date_deleted__isnull=True,
                                        is_filtered = True)   
        
        # Set up pagination
        item_total = Item.objects.filter(date_deleted__isnull=True)
        item = Item.objects.filter(date_deleted__isnull=True).order_by('-item_id')
        
        aux_images = ItemsImage.objects.filter(item_id__in = item.values_list('item_id')).distinct('item_id')

        context = { 'request' : 'all',
                    'category' : get_shop_categories(),
                    'attribute_type' : attribute,
                    'attribute' : attribute_results,
                    'product' : item,
                    'aux_images' :  aux_images,
                    'cart_length' : Cart(request).__len__(),
                    'price_filter' :  item_total.aggregate(Max('price')),
                    }


        return render(request, self.template, context)

class ShopCategoryView(View):
    template = 'shop.html'

    def get(self, request, slug_url):

        attr = Attribute.objects.all()
        attribute_results = attr.filter(hierarchy_level=1, 
                                                    date_deleted__isnull=True,
                                                    is_filtered = True)
        attribute = attr.filter(hierarchy_level = 2, 
                                        date_deleted__isnull=True,
                                        is_filtered = True)
        
        category_results = get_shop_categories()
        
        for i, j in enumerate(category_results): 
            if category_results[i].slug_url == slug_url:
                category_filter = category_results[i].id
        
        
        # Set up pagination
        item_total = Item.objects.filter(date_deleted__isnull=True, category= category_filter)
        item = Item.objects.filter(date_deleted__isnull=True, category= category_filter).order_by('-item_id')
        
        
        aux_images = ItemsImage.objects.filter(item_id__in = item.values_list('item_id')).distinct('item_id')

        context = { 'request' : slug_url,
                    'category' : category_results,
                    'attribute_type' : attribute,
                    'attribute' : attribute_results,
                    'product' : item,
                    'aux_images' :  aux_images,
                    'cart_length' : Cart(request).__len__(),
                    'price_filter' :  item_total.aggregate(Max('price')),
                    }
        return render(request, self.template, context)

class ProductDetailView(View):
    template_name = 'product_detail.html'

    def get(self, request, slug):
       
        all_product = Item.objects.all()
        product = all_product.get(slug=slug)

        inventory = ItemsInventory.objects.filter(item_id__slug = slug)
        color = inventory.values('color_id__name','color_id__id', 'color_id__presentation').distinct()
        size = inventory.values('size_id__name','size_id__id', 'size_id__presentation').distinct()
        
        aux_images = ItemsImage.objects.filter(item_id__slug = slug)

        related_product = all_product.filter(category = product.category).filter(~Q(item_id=product.item_id))
        
        context = {'color'   : color,
                    'size'    : size,
                    'data'        : product,
                    'inventory'     : inventory,
                    'related_product' : related_product, 
                    'aux_images'   : aux_images,
                    'cart_length' : Cart(request).__len__(),
                    'category' : get_shop_categories()}

        return render(request, self.template_name, context)

class CartView(View):
    template_name = 'shop-cart.html'
    
    def get(self, request):
        
        cart = Cart(request)

        SKU = [i['product'] for i in Cart(request)]
        ordered_item = ItemsInventory.objects.filter(SKU__in = SKU)
        context = {'ordered_items' : ordered_item,
                'total_ordered_prices' : round(cart.get_total_price(),2),
                'cart_length' : cart.__len__(),
                'cart' : cart,
                'category' : get_shop_categories()}

        if not cart:
            return render(request, 'empty-cart.html', context)
        else:
            return render(request, self.template_name , context)


#################### Ajax called ##########################
def filter_data_all(request):
    
    attribute_results = Attribute.objects.filter(hierarchy_level=1, 
                                                 date_deleted__isnull=True,
                                                 is_filtered = True).order_by('name')
    
    colors, sizes, minPrice, maxPrice  = [], [], 0, 0
    
    for i in attribute_results.values():
        if i.get('name') in ['Colors','Color']:
            str_array = str(i.get('name')) + '[]'
            colors = request.GET.getlist(str_array)
        elif i.get('name') in ['Sizes','Size']:
            str_array = str(i.get('name')) + '[]'
            sizes = request.GET.getlist(str_array)
        elif i.get('name') in ['Price','Prices']:
            minPrice = request.GET.get('minPrice')
            maxPrice = request.GET.get('maxPrice')

    category_results = get_shop_categories()

    allProducts = Item.objects.filter(date_deleted__isnull=True,
                                        price__gte= minPrice,
                                        price__lte= maxPrice).order_by('-item_id').distinct()
    
    if len(colors)>0:
        allProducts=allProducts.filter(itemsinventory__color_id__in=colors).distinct()
    if len(sizes)>0:
        allProducts=allProducts.filter(itemsinventory__size_id__in=sizes).distinct()
    
    aux_images = ItemsImage.objects.filter(item_id__in = allProducts.values_list('item_id')).distinct('item_id')

    context = {'product':allProducts, 'aux_images': aux_images}

    t=render_to_string('ajax/product.html',context)

    return JsonResponse({'product':t})

def filter_data_category(request, slug_url):
    
    attribute_results = Attribute.objects.filter(hierarchy_level=1, 
                                                 date_deleted__isnull=True,
                                                 is_filtered = True).order_by('name')
    
    colors, sizes, minPrice, maxPrice  = [], [], 0, 0
    
    for i in attribute_results.values():
        if i.get('name') in ['Colors','Color']:
            str_array = str(i.get('name')) + '[]'
            colors = request.GET.getlist(str_array)
        elif i.get('name') in ['Sizes','Size']:
            str_array = str(i.get('name')) + '[]'
            sizes = request.GET.getlist(str_array)
        elif i.get('name') in ['Price','Prices']:
            minPrice = request.GET.get('minPrice')
            maxPrice = request.GET.get('maxPrice')

    category_results = get_shop_categories()

    if slug_url != 'all':
        for i, j in enumerate(category_results): 
            if category_results[i].slug_url == slug_url:
                category_filter = category_results[i].id


    if slug_url != 'all': 
        allProducts= Item.objects.filter(date_deleted__isnull=True, 
                                         category=category_filter, 
                                         price__gte= minPrice,
                                         price__lte= maxPrice).order_by('-item_id').distinct()
    else:
        allProducts = Item.objects.filter(date_deleted__isnull=True,
                                            price__gte= minPrice,
                                            price__lte= maxPrice).order_by('-item_id').distinct()
    
    if len(colors)>0:
        allProducts=allProducts.filter(itemsinventory__color_id__in=colors).distinct()
    if len(sizes)>0:
        allProducts=allProducts.filter(itemsinventory__size_id__in=sizes).distinct()
    
    aux_images = ItemsImage.objects.filter(item_id__in = allProducts.values_list('item_id')).distinct('item_id')
    
    context = {'product':allProducts, 'aux_images': aux_images}

    t=render_to_string('ajax/product.html',context)

    return JsonResponse({'product':t})

def product_color_choice(request, slug):
    size = ItemsInventory.objects.filter(item_id__slug = slug,
                                         color_id__id  = request.GET.get('colorChoice')).values('size_id__name','size_id__id', 'size_id__presentation').distinct()
    
    context = {'size':size}
    t=render_to_string('ajax/size.html',context)

    return JsonResponse({'size':t})

def quantity_choice(request, slug):
    quantity = ItemsInventory.objects.get(item_id__slug = slug,
                                             color_id__id  = request.GET.get('colorChoice'),
                                             size_id__id  = request.GET.get('sizeChoice')
                                         ).quantity
    
    quantity = range(1, quantity + 1) if quantity < 15 else range(1, 15 + 1)
    context = {'quantity':quantity}
    t=render_to_string('ajax/quantity.html',context)

    return JsonResponse({'quantity':t})


############ AJAX for Cart related #######################
def add_to_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('productid'))
        color_id = int(request.POST.get('colorid'))
        size_id = int(request.POST.get('sizeid'))
        product_qty = int(request.POST.get('productqty'))
        product = get_object_or_404(ItemsInventory, item_id=product_id, color = color_id, size = size_id)

        cart.add(product=product, qty=product_qty)

        cart_quantity = cart.__len__()
        return JsonResponse({'qty': cart_quantity})

def delete_from_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = str(request.POST.get('SKU'))
        cart.delete(product=product_id)

        cart_quantity = cart.__len__()
        
        return JsonResponse({'qty': cart_quantity})

def update_cart(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = str(request.POST.get('SKU'))
        product_qty = int(request.POST.get('productqty'))
        cart.update(product=product_id, qty=product_qty)

        cart_quantity = cart.__len__()
        return JsonResponse({'qty': cart_quantity})
         