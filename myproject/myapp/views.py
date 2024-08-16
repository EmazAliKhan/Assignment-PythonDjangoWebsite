from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout
from .models import User, Category, Product
from django.contrib import messages
from django.db.models import Max
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import random
import datetime
import pathlib
import os

# Create your views here.

def home(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in first.")
        return redirect('login')
    return render(request, 'home.html')

    
def signup(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        pass1 = request.POST.get("password1")
        pass2 = request.POST.get("password2")
        
        if pass1 != pass2:
            msg = "Passwords do not match"
            return render(request, 'signup.html', {'msg': msg})
        
        if User.objects.filter(email=email).exists():
            msg = "Email already exists"
            return render(request, 'signup.html', {'msg': msg})
        else:
            user = User(name=name, email=email, password=pass1)
            user.save()
            msg = "You have signed up successfully"
            messages.success(request, msg)
            return redirect("login")
    return render(request, 'signup.html')


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        pass1 = request.POST.get("pass")
        try: 
            user = User.objects.get(email=email,password=pass1)
            request.session['id'] = user.id
            request.session['name'] = user.name
            request.session['email'] = user.email
            
            return redirect("home")
        except User.DoesNotExist:
            msg = "Invalid username or password"
            return render(request, 'login.html', {'msg': msg})
    else:
        return render(request,'login.html')
    

def password_reset_request(request):
    if request.method == "POST":
        email = request.POST.get('email')
        
        try:
            user = User.objects.get(email=email)

            reset_code = random.randint(1000, 9999)

            request.session['reset_code'] = reset_code
            request.session['reset_email'] = email

            send_mail(
                'Password Reset Code',
                f'Your password reset code is {reset_code}.',
                'your-email@example.com', 
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'A reset code has been sent to your email.')
            return redirect('password_reset_confirm')
        
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            return redirect('password_reset_request')

    return render(request, 'password_reset_request.html')

def password_reset_confirm(request):
    if request.method == "POST":
        code = request.POST.get('code')
        new_password = request.POST.get('new_password')

        if request.session.get('reset_code') == int(code):
            email = request.session.get('reset_email')
            try:
                user = User.objects.get(email=email)
                user.password = (new_password)
                user.save()
                del request.session['reset_code']
                del request.session['reset_email']

                messages.success(request, 'Your password has been reset successfully.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
        else:
            messages.error(request, 'Invalid reset code.')
            return redirect('password_reset_confirm')

    return render(request, 'password_reset_confirm.html')



def createprod(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in to add a product.")
        return redirect('login')
    if request.method == "POST":
        title = request.POST.get("title")
        brand = request.POST.get("brand")
        price = request.POST.get("price")
        qty = request.POST.get("qty")
        desc = request.POST.get("desc")
        category_id = request.POST.get("category")
        # Check if the user ID is set in the session
        user_id = request.session.get('id')
        if not user_id:
            messages.error(request, "You must be logged in to create a product.")
            return redirect('login')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request,"User not found.")
            return redirect('login')

        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Category not found.")
            return render(request, 'addprod.html', {'catmsg': msg, 'category1': Category.objects.all()})

        # Check if a file has been uploaded
        if bool(request.FILES.get('file', False)):
            file = request.FILES['file']
            file.name = file.name.lower()

            # File type validation
            if not file.name.endswith(('.jpg', '.png', '.jpeg')):
                msg = 'File type should be .jpg, .png, or .jpeg'
                return render(request, 'addprod.html', {'typemsg': msg, 'category1': Category.objects.all()})
            
            # Check if the product already exists
            if Product.objects.filter(name=title).exists():
                msg = 'Product already exists'
                return render(request, 'addprod.html', {'existmsg': msg, 'category1': Category.objects.all()})

            # Save the product without the image first
            product = Product(
                name=title, 
                brand=brand, 
                price=price, 
                qty=qty, 
                description=desc, 
                category=category, 
                user=user
            )
            product.save()

            # Save the image with the product ID as the filename     
            fss = FileSystemStorage()
            file_name = fss.save(f"{product.id}.png", file)

            product.imgurl = fss.url(file_name)
            product.save(update_fields=['imgurl'])

            messages.success(request, "Product created successfully.")
            return redirect("showall")
        else:
            msg = 'Please select a file'
            return render(request, 'addprod.html', {'filemsg': msg, 'category1': Category.objects.all()})
    else:
        categories = Category.objects.all()
        return render(request, 'addprod.html', {'category1': categories})


def editprod(request, id):
    product = Product.objects.get(id=id)
    
    if request.method == "POST":
        product.name = request.POST.get("name")
        product.brand = request.POST.get("brand")
        product.price = request.POST.get("price")
        product.qty = request.POST.get("qty")
        product.description = request.POST.get("description")

        category_id = request.POST.get("category")
        try:
            product.category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            messages.error(request, "Category not found.")
            return render(request, 'editprod.html', {'product': product, 'categories': Category.objects.all()})
        
        # Handle file upload if a new image is uploaded
        if bool(request.FILES.get('imgurl', False)) == True:
            file = request.FILES.get('imgurl')
            file.name = file.name.lower()
             # Validate the file type
            if not file.name.endswith(('.jpg', '.png', '.jpeg')):
                messages.error(request, 'File type should be .jpg, .png, or .jpeg')
                return render(request, 'editprod.html', {'product': product, 'categories': Category.objects.all()})

            chk = pathlib.Path(__file__).parent.parent.joinpath("media").joinpath(str(id)+ ".png").exists()   
            if chk is True:
                ap = pathlib.Path(__file__).parent.parent.joinpath("media").joinpath(str(id)+ ".png")
                os.remove(ap)
            
            fss = FileSystemStorage()
            Upload = request.FILES['imgurl']
            file = fss.save(str(product.id) +".png", Upload)
            fileUrl = fss.url(file)
            product.imgurl = fileUrl
            product.save(update_fields=['imgurl'])

        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect("showall")
    else:
        categories = Category.objects.all()
        return render(request, 'editprod.html', {'product': product, 'categories': categories})


def showall(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in see the product details.")
        return redirect('login')
    product = Product.objects.all()
    return render(request, 'showall.html', {'product': product})

def deleteprod(request, id):
    product = Product.objects.get(id=id)
    product.delete()
    chk = pathlib.Path(__file__).parent.parent.joinpath("media").joinpath(str(id) + ".png").exists()
    if chk is True:
            ap = pathlib.Path(__file__).parent.parent.joinpath("media").joinpath(str(id) + ".png")
            os.remove(ap)
    messages.success(request, "Product deleted successfully!")
    return redirect("showall")

def deleteall(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in first.")
        return redirect('login')
    products = Product.objects.all()
    for product in products:
        file_path = pathlib.Path(__file__).parent.parent.joinpath("media").joinpath(str(product.id) + ".png")
        
        if file_path.exists():
            os.remove(file_path)
        
        product.delete()
    messages.success(request, "All products have been deleted successfully!")
    return redirect("showall")

def prod_details(request, id):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in see the product details.")
        return redirect('login')
    product = Product.objects.get(id=id)
    return render(request, 'details.html', {'product': product})



def add_category(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in to add a category.")
        return redirect('login')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name, created_at=datetime.datetime.now(), created_by_id=user_id)
            messages.success(request, "Category added successfully!")
            return redirect('list_categories')  
    return render(request, 'category.html')


def list_categories(request):
    user_id = request.session.get('id')
    if not user_id:
        messages.error(request, "You must be logged in to see a list of categories.")
        return redirect('login')
    if request.method == 'POST':
        if 'delete_all' in request.POST:
            Category.objects.all().delete()
            messages.success(request, "All categories deleted successfully.")
            return redirect('list_categories')

    categories = Category.objects.all()
    return render(request, 'list_categories.html', {'categories': categories})



def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    messages.success(request, "Category deleted successfully!")
    return redirect("list_categories")



def logout(request):
    auth_logout(request)  
    logoutmsg = "You have successfully logged out."
    messages.success(request,logoutmsg)
    return redirect('login')  
