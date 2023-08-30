from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
# verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from cart.views import _cart_id
from cart.models import CartItem, Cart
import requests


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phonenumber = form.cleaned_data['phonenumber']
            password = form.cleaned_data['password']
            username = email.split('@')[0]
            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
            user.phonenumber = phonenumber
            user.save()

            current_site = get_current_site(request)
            mail_subject = ' Please Activate Your account'
            message = render_to_string('accounts/account_verifecation_mail.html',
           {    'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])

            # email.content_subtype = 'html'
            send_email.send()

            # messages.success(request, 'We have sent you an account verification email to your email address.')

            return redirect(f'/accounts/login/?command=verification&email='+email)
            # return redirect('register')


    else:
        form = RegistrationForm()
    context = {
        'form': form
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exist = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exist:
                    cart_items = CartItem.objects.filter(cart=cart)

                    product_variations = []
                    idp = []
                    for item in cart_items:
                        variation = item.variations.all()
                        product_variations.append(list(variation))
                        idp.append(item.id)

                    cart_items = CartItem.objects.filter(user=user)
                    existing_variations = []
                    id = []
                    for item in cart_items:
                        existing_variation = item.variations.all()
                        existing_variations.append(list(existing_variation))
                        id.append(item.id)
                    for pr in product_variations:
                        if pr in existing_variations:
                            index = existing_variations.index(pr)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            index = product_variations.index(pr)
                            item_id = idp[index]
                            item = CartItem.objects.get(id=item_id)
                            item.user = user
                            item.save()
            except:
                pass
            auth.login(request, user)
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid login credential')
            return redirect('login')
    return render(request, 'accounts/login.html')

@login_required(login_url = 'login')
def logout(request):
    auth.logout(request)
    messages.success(request, 'You have successfully log out.')
    return redirect( 'login' )


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist ):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account has been activated Successfully.')
        return redirect('login')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('register')


@login_required(login_url = 'login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html')


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email__exact=email).exists():

            user = Account.objects.get(email=email)

            current_site = get_current_site(request)
            mail_subject = ' Password Resetting '
            message = render_to_string('accounts/reset_password_email.html',
                                       {'user': user,
                                        'domain': current_site,
                                        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                        'token': default_token_generator.make_token(user),
                                        })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'We have sent you an password reset email to your email address. '+email+".")
        else:
            messages.error(request, 'Account Does not exist.')
            return redirect('forgotpassword')
    return render(request, 'accounts/forgotpassword.html')


def reset_password_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist ):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('newpassword')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('forgotpassword')


def newpassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirmpassword']

        if password == confirm_password:
            uid = request.session['uid']
            user = Account._default_manager.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Congratulation Your password has been changed.')
            return redirect('login')
        else:
            messages.error(request, 'Password does not match!')
            return redirect('newpassword')

    else:
        return render(request, 'accounts/newpassword.html')
