from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages

# Create your views here.
def category(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    if request.method =='POST':
        category_name = request.POST. get('name')
        cat=Category(name = category_name)
        cat.save()
        messages.success(request, ' Create successfully.')
        return redirect('category')
    categories = Category.objects.all()
    context = {"categories":categories}
    return render(request,"admin_panel/categories.html",context)

def category_edit(request,id):
    if 'username' not in request.session:
        return redirect('admin_login') 
    categories = Category.objects.get(id = id)
    context={"obj":categories}
    if request.method == 'POST':
        active = request.POST.get('active')
        edit = Category.objects.get(id=id)
        edit.is_active = active
        edit.save()
        messages.success(request, ' Edit successfully.')
        return redirect('category')
    return render(request,"admin_panel/category_edit.html",context)

def category_delete(request,id):
    delete = Category.objects.get(id = id)
    delete.delete()
    messages.success(request, ' Delete successfully.')
    return redirect ('category')

# Brands----------------------------------------------------------------------------------

def brands_manage(request):
    if 'username' not in request.session:
        return redirect('admin_login') 
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        offer_percentage=request.POST.get('offer_percentage')

        category = Category.objects.get(id=category_id)

        # Perform custom validation
        if not name:
            error_message = 'Brand name cannot be empty.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)
        
        elif not name[0].isupper():
            error_message = 'Username must start with a capital letter.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)

        elif any(char.isdigit() for char in name):
            error_message = 'Brand name cannot contain numbers.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)
        
        elif not name.isalnum():
            error_message = 'Brand name cannot contain special characters.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)
        
        elif len(name) > 10:
            error_message = 'Brand name cannot exceed 10 characters.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)
        
        elif Brand.objects.filter(name__iexact=name, category=category).exists():
            error_message = 'Brand with this name already exists.'
            brands = Brand.objects.all()
            categories = Category.objects.filter(is_active=True)
            context = {
                "brd": brands,
                "category": categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brands.html", context)
        
        else:
            if offer_percentage:
                if not offer_percentage.isdigit() or int(offer_percentage) < 1 or int(offer_percentage) > 100:
                    error_message = 'Offer percentage must be a number between 1 and 100.'
                else:
                    brand = Brand(name=name, category=category, offer=offer_percentage)
                    brand.save()
                    messages.success(request, 'Brand created successfully.')
                    return redirect('admin_brands')
        
            else:
                brand = Brand(name=name, category=category)
                brand.save()
                messages.success(request, 'Brand created successfully.')
                return redirect('admin_brands')

    brands = Brand.objects.all()
    categories = Category.objects.filter(is_active = True)
    context = {
        "brd": brands,
        "category": categories
    }
    return render(request, "admin_panel/brands.html", context)

def brand_edit(request, id):
    if 'username' not in request.session:
        return redirect('admin_login') 
    
    brand = Brand.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == 'POST':
        name = request.POST.get("name")
        category_id = request.POST.get("category")
        active = request.POST.get('active')
        category = Category.objects.get(id=category_id)

        # Perform custom validation
        error_message = None
        if not name:
            error_message = 'Brand name cannot be empty.'
        elif not name[0].isupper():
            error_message = 'Username must start with a capital letter.'
        elif any(char.isdigit() for char in name):
            error_message = 'Brand name cannot contain numbers.'
        elif not name.isalnum():
            error_message = 'Brand name cannot contain special characters.'
        elif len(name) > 10:
            error_message = 'Brand name cannot exceed 10 characters.'
        elif Brand.objects.filter(name__iexact=name, category=category).exclude(id=id).exists():
            error_message = 'Brand with this name already exists.'

        if error_message:
            context = {
                "obj": brand,
                'category': categories,
                "error_message": error_message
            }
            return render(request, "admin_panel/brand_edit.html", context)
        else:
            brand.name = name
            brand.category = category
            brand.is_active = active
            brand.save()
            messages.success(request, ' Edit successfully.')
            return redirect('admin_brands')

    context = {
        "obj": brand,
        'category': categories
    }
    return render(request, "admin_panel/brand_edit.html", context)



def brand_delete(request,id):
    brand=Brand.objects.get(id = id)
    brand.delete()
    messages.success(request, 'Delete successfully.')
    return redirect('admin_brands')