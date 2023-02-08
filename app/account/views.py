from django.shortcuts import  render, redirect
from django.views import View

from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages

from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from django.urls import reverse
from django.db.models import Sum

# import pagination
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import NewUserForm, ProfileCustomerForm, AddressForm, PasswordResetForm
from ecommerce.cart import Cart
from ecommerce.views import get_shop_categories
from .models import Customer, Address
from order.models import OrderItem, OrderStatus, Order

def delete_address(request, id):
    
    obj = get_object_or_404(Address, id = id)

    if request.method =="GET":
        obj.delete()
        return redirect(request.GET.get('next'))

class LoginView(View):
    template_name = 'portal.html'

    def get(self, request):
        form = NewUserForm()
        context = {'form': form, 'cart_length': Cart(request).__len__(), 'category' : get_shop_categories(),}
        return render(request, self.template_name, context)

    def post(self,request):
        if 'Login' in request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            if not email or not password:
                messages.error(request, 'Both email address and password are required.', extra_tags='login')
                return redirect('account:login')
            user_obj = User.objects.filter(email=email).first()
            if user_obj is None:
                messages.error(request, 'User not found.', extra_tags='login')
                return redirect('account:login')
            user = authenticate(username = user_obj.username, password = password)
            if user is not None:
                login(request, user)
                cust_uuid = Customer.objects.get(email=request.user.email).customer_uuid
                request.session['customer'] = str(cust_uuid)
                if not self.request.GET.get('next'):
                    return redirect(reverse('account:profile'))
                else:
                    return redirect(self.request.GET.get('next'))
            else:
                messages.error(request, 'Wrong password', extra_tags='login')
                return redirect('account:login')
        elif 'Register' in request.POST:
            form = NewUserForm(request.POST)
            if form.is_valid():
                newuser = form.save()
                try:
                    cust_profile = Customer.objects.get(email=form.cleaned_data.get('email'))
                    cust_profile.is_signup_user = True
                    cust_profile.save()
                except Customer.DoesNotExist:
                    customer = Customer.objects.create(user=newuser,
                                              first_name=form.cleaned_data.get('first_name'),
                                              last_name=form.cleaned_data.get('last_name'),
                                              is_signup_user=True,
                                              email=form.cleaned_data.get('email'))

                username = form.cleaned_data.get('email')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                customer = Customer.objects.get(email=request.user.email)
                request.session['customer'] = str(customer.customer_uuid)
                if not self.request.GET.get('next'):
                    return redirect(reverse('account:profile'))
                else:
                    return redirect(self.request.GET.get('next'))
            else:
                context = {'form': form, 
                            'registration': "active", 
                            'cart_length':  Cart(request).__len__(),
                            'category' : get_shop_categories(),}
                return render(request, self.template_name, context)

def logout_view(request):
    logout(request)
    if not request.GET.get('next'):
        return redirect(reverse('ecommerce:shop-all'))
    else:
        return redirect(request.GET.get('next'))
     

class ProfileView(LoginRequiredMixin, View):
    profile_template = 'profile.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        form = ProfileCustomerForm(instance = profile)
            
        context = {'profile' :profile,
                    'form':form,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),}
        return render(request, self.profile_template, context)
    
    def post(self, request):
        
        profile = Customer.objects.get(customer_uuid = request.session['customer'])
        form = ProfileCustomerForm(request.POST, instance= profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Update successfully', extra_tags='success')
            return redirect('account:profile')
        else:
            messages.error(request, 'Unable to update', extra_tags='error')
            context = { 'profile' :profile,
                        'form':form,
                        'cart_length': Cart(request).__len__(),
                        'category' : get_shop_categories(),}
            return render(request, self.profile_template, context)

class PasswordResetView(LoginRequiredMixin, View):
    template = 'password.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        if request.user.is_authenticated:
            form = PasswordResetForm(instance=request.user)
            
        context = {'profile' :profile,
                    'form':form,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),}
        return render(request, self.template, context)

    def post(self,request):
        
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        
        form = PasswordResetForm(instance=request.user,data=request.POST)

        if form.is_valid():
            user = request.user

            if user.check_password(request.POST.get('oldpassword')):
                form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Update successfully', extra_tags='success')
                return redirect('account:password-reset')
            else:
                messages.error(request, 'You entered a wrong current password', extra_tags='error')
                return redirect('account:password-reset')
        else:
            context = {'profile' :profile,
                    'form':form,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),}
            return render(request, self.template, context)
    


class OrdersView(LoginRequiredMixin, View):
    template = 'orders.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        orders = Order.objects.filter(customer_id = profile).order_by('-created_at')
        paginator = Paginator(orders, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)


        try:
            order_status = OrderStatus.objects.filter(order_id__in = orders)\
                            .order_by('order_id','-created_at')\
                            .distinct('order_id')
        except:
            order_status = None

        try:
            order_item  = OrderItem.objects.filter(order_id__in = orders)
        except:
            order_status = None

        
            
        context = { 'profile' :profile,
                    'order_status': order_status,
                    'order_item' : order_item,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),
                    'page_obj' : page_obj}
        return render(request, self.template, context)

class AddressesView(LoginRequiredMixin, View):
    template = 'address.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        address = Address.objects.filter(customer_id = profile).order_by('-date_created')
        form = AddressForm()
            
        context = { 'form2' : form,
                    'profile' : profile,
                    'addresses' : address,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),}
        return render(request, self.template, context)
    
    def post(self, request):
        try:
            profile = Customer.objects.get(customer_uuid = request.session['customer'])
        except:
            messages.error(request, 'User not found.', extra_tags='login')
            return redirect('account:login')
        
        try:
            child = Address.objects.get(customer_id=profile,
                                        street_address=str(request.POST.get('street_address')),
                                        apartment_address=str(request.POST.get('apartment_address')),
                                        city=str(request.POST.get('city')),
                                        state=str(request.POST.get('state')),
                                        zip=str(request.POST.get('zip'))
                                        )
            if request.user.is_authenticated and request.POST.get('default') == 'on':
                if not child.default:
                    try:
                        unsaved_address = Address.objects.get(customer_id=profile,default=True)
                        unsaved_address.default = False
                        unsaved_address.save()
                    except Address.DoesNotExist:
                        pass
                    child.default = True
                    child.save()                   
        except Address.DoesNotExist:
            if request.user.is_authenticated and request.POST.get('default') == 'on':
                try:
                    unsaved_address = Address.objects.get(customer_id=profile,default=True)
                    unsaved_address.default = False
                    unsaved_address.save()
                except Address.DoesNotExist:
                    pass
                form = AddressForm(request.POST)
                if form.is_valid():
                    child = form.save(commit=False)
                    child.customer_id = profile
                    child.save()
            elif request.user.is_authenticated and not request.POST.get('default'):
                form = AddressForm(request.POST)
                if form.is_valid():
                    child = form.save(commit=False)
                    child.customer_id = profile
                    child.save()
            else:
                form = AddressForm(request.POST)
                if form.is_valid():
                    child = form.save(commit=False)
                    child.customer_id = profile
                    child.save()

        address = Address.objects.filter(customer_id = profile).order_by('-date_created')   
        context = { 'form2' : form,
                    'profile' : profile,
                    'addresses' : address,
                    'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),}
        return render(request, self.template, context)


class DashboardView(LoginRequiredMixin, View):
    template = 'owner/dashboard.html'
    login_url = '/account/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        order = Order.objects.all()
        order_total = order.aggregate(Sum('total_net'))
        order_cnt = order.count()
        
        order_status = OrderStatus.objects.all()

        received_order_status_cnt = order_status\
                                .order_by('order_id','-created_at')\
                                .distinct('order_id')\
                                .filter(status__name = 'Received').count()
        completed_order_status_cnt = order_status\
                                .order_by('order_id','-created_at')\
                                .distinct('order_id')\
                                .filter(status__name = 'Completed').count()
        
        latest_order_status = order_status\
                                .order_by('order_id','-created_at')\
                                .distinct('order_id')


        context = {'cart_length': Cart(request).__len__(),
                    'category' : get_shop_categories(),
                    'profile': request.user,
                    'order_total' : order_total,
                    'order_cnt' : order_cnt,
                    'received_order_status_cnt' : received_order_status_cnt,
                    'completed_order_status_cnt' : completed_order_status_cnt,
                    'latest_order_status' : latest_order_status}
        return render(request, self.template, context)


def termsandservices(request):
    
    context = {'cart_length': Cart(request).__len__(),
                'category' : get_shop_categories()}
    
    return render(request, 'service-terms.html', context )


