from django.shortcuts import render,redirect
from .models import *
from datetime import datetime
from decimal import Decimal
from django.http import Http404
# Create your views here.


def product_attributes(request):
    if request.method == 'POST':
        color = request.POST.get('color')
        ram = request.POST.get('ram')

        if Attribute_Value.objects.filter(attribute_ram=ram).exists():
            error_message = 'Attribute value with this RAM already exists.'
            attr = Attribute_Value.objects.all()
            context = {
                "attribute": attr,
                "error_message": error_message,
            }
            return render(request, "admin_panel/attributes_values.html", context)
        else:
            attribute = Attribute_Value(attribute_color=color, attribute_ram=ram)
            attribute.save()
            return redirect('product_attributes')  # Redirect to the same page or a different URL

    att = Attribute_Value.objects.all()
    context = {"attribute": att}
    return render(request, "admin_panel/attributes_values.html", context)

def attribute_edit(request,id):
    att=Attribute_Value.objects.get(pk=id)
    context={'obj':att}
    if request.method == 'POST':
        color = request.POST['color']
        ram = request.POST['ram']
        active = request.POST.get('active')
        edit=Attribute_Value.objects.get(pk=id)
        edit.attribute_color=color
        edit.attribute_ram=ram
        edit.is_active=active
        edit.save()
        return redirect('product_attributes')
    return render (request,"admin_panel/attribute_edit.html",context)

def attribute_delete(request,id):
    att=Attribute_Value.objects.get(id = id)
    att.delete()
    return redirect ('product_attributes')

# product----------------------------------------------------------------------

def Product_add(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_category_id = request.POST.get('Category')
        product_brand_id = request.POST.get('brand')
        product_description = request.POST.get('description')

        # Check if name and description are not empty
        error_message = None
        if not product_name:
            error_message = 'Product name cannot be empty.'
        elif not product_description:
            error_message = 'Product description cannot be empty.'
        # Additional validation for name length, etc.
        elif len(product_name) < 3:
            error_message = 'Product name should be at least 3 characters long.'
        elif Products.objects.filter(product_name__iexact=product_name, product_category_id=product_category_id).exists():
            error_message = 'A product with this name already exists in the selected category.'

        # Add more validation rules as needed
        else:
            try:
                product_cat = Category.objects.get(id=product_category_id)
                product_brd = Brand.objects.get(id=product_brand_id)
                new_prod = Products(product_name=product_name, product_category=product_cat,
                                    product_brand=product_brd, product_description=product_description)
                new_prod.save()
                return redirect('product_list')
            except Category.DoesNotExist:
                error_message = 'Selected category does not exist.'
            except Brand.DoesNotExist:
                error_message = 'Selected brand does not exist.'

        # If validation fails, render the form with error message
        brand = Brand.objects.filter(is_active=True)
        category = Category.objects.filter(is_active=True)
        context = {
            "brand": brand,
            "category": category,
            "error_message": error_message
        }
        return render(request, "admin_panel/product_add.html", context)


    # GET request - render the form
    brand = Brand.objects.filter(is_active=True)
    category = Category.objects.filter(is_active=True)
    context = {
        "brand": brand,
        "category": category,
    }
    return render(request, "admin_panel/product_add.html", context)


def Product_list(request):
    products = Products.objects.all().order_by("created_at")
    context={"products":products}
    return render(request,"admin_panel/product_list.html",context)

from django.shortcuts import render, redirect
from datetime import datetime
from .models import Products, Category, Brand

def product_edit(request, id):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_category_id = request.POST.get('Category')
        product_brand_id = request.POST.get('brand')
        product_description = request.POST.get('description')
        active = request.POST.get('active')

        # Check if name and description are not empty
        error_message = None
        if not product_name:
            error_message = 'Product name cannot be empty.'
        elif not product_description:
            error_message = 'Product description cannot be empty.'
        # Additional validation for name length, etc.
        elif len(product_name) < 3:
            error_message = 'Product name should be at least 3 characters long.'
        else:
            try:
                product_cat = Category.objects.get(id=product_category_id)
                product_brd = Brand.objects.get(id=product_brand_id)
                existing_product = Products.objects.filter(product_name__iexact=product_name, product_category=product_cat).exclude(id=id)
                if existing_product.exists():
                    error_message = 'A product with this name already exists in the selected category.'
                else:
                    edit = Products.objects.get(id=id)
                    edit.product_name = product_name
                    edit.product_category = product_cat
                    edit.product_brand = product_brd
                    edit.is_active = active
                    edit.created_at = datetime.today()
                    edit.product_description = product_description
                    edit.save()
                    return redirect('product_list')
            except Category.DoesNotExist:
                error_message = 'Selected category does not exist.'
            except Brand.DoesNotExist:
                error_message = 'Selected brand does not exist.'

        # If validation fails, render the form with error message
        product = Products.objects.get(id=id)
        cat = Category.objects.filter(is_active=True)
        brand = Brand.objects.filter(is_active=True)
        context = {
            "obj": product,
            "category": cat,
            "brand": brand,
            "error_message": error_message
        }
        return render(request, "admin_panel/product_edit.html", context)

    # GET request - render the form
    product = Products.objects.get(id=id)
    cat = Category.objects.filter(is_active=True)
    brand = Brand.objects.filter(is_active=True)
    context = {
        "obj": product,
        "category": cat,
        "brand": brand
    }
    return render(request, "admin_panel/product_edit.html", context)



def product_delete(request,id):
    product=Products.objects.get(id = id)
    product.delete()
    return redirect ('product_list')


def product_grid(request):
    return render(request,"admin_panel/product_grid.html")


# variant---------------------------------------------------------------------------------------

def variant_add(request):
    attributes = Attribute_Value.objects.filter(is_active=True)
    products = Products.objects.filter(is_active=True)
    context = {
        "variant": attributes,
        "product": products
    }

    if request.method == 'POST':
        product_id = request.POST.get('product')
        max_price = request.POST['max_price']
        sale_price = request.POST['sale_price']
        stock = request.POST['stock']
        thumbnail_image = request.FILES.get('image')

        # Perform strong validation for max price, sale price, and stock
        error_message = None
        try:
            max_price = float(max_price)
        except ValueError:
            error_message = 'Max price must be a valid number.'
        try:
            sale_price = float(sale_price)
        except ValueError:
            error_message = 'Sale price must be a valid number.'
        if not stock.isdigit():
            error_message = 'Stock must be a valid integer.'
        elif float(max_price) > 1.5 * float(sale_price):  # Adjust threshold as needed
            error_message = 'Max price should not be significantly higher than sale price.'
        elif int(stock) <= 0:
            error_message = 'Stock must be greater than 0.'
        elif not product_id:
            error_message = 'Please select a product.'

        if error_message:
            context['error_message'] = error_message
            return render(request, "admin_panel/variant_add.html", context)

        try:
            product = Products.objects.get(id=product_id)
            # Check if a variant with the same attributes already exists for the product
            existing_variant = Product_Variant.objects.filter(product=product, max_price=max_price, sale_price=sale_price, stock=stock)
            if existing_variant.exists():
                # Update the existing variant instead of creating a new one
                variant = existing_variant.first()
                variant.thumbnail_image = thumbnail_image
                variant.save()
            else:
                # Create a new variant
                obj = Product_Variant(product=product, max_price=max_price, sale_price=sale_price,
                                      stock=stock, thumbnail_image=thumbnail_image)
                obj.save()

                # Add variant attributes
                variant_attribute_ids = request.POST.getlist('variant')
                for attribute_id in variant_attribute_ids:
                    if attribute_id:  # Check if attribute_id is not empty
                        try:
                            attribute_value = Attribute_Value.objects.get(pk=attribute_id)
                            obj.attributes.add(attribute_value)
                        except Attribute_Value.DoesNotExist:
                            raise Http404("Attribute_Value with ID {} does not exist".format(attribute_id))

            return redirect('variant_list')
        except Products.DoesNotExist:
            raise Http404("Product with ID {} does not exist".format(product_id))

    return render(request, "admin_panel/variant_add.html", context)







def variant_list(request):
    variants = Product_Variant.objects.select_related().order_by('created_at')
    context = {"variant": variants}
    return render(request,"admin_panel/variant_list.html",context)

def variant_delete(request,id):
    variant = Product_Variant.objects.get(id=id)
    variant.delete()
    return redirect('variant_list')

def variant_edit(request,id):
    attributes = Attribute_Value.objects.filter(is_active=True)
    products = Products.objects.filter(is_active=True)
    obj = Product_Variant.objects.get(id=id)
    context = {
        "variant": attributes,
        "product": products,
        "obj": obj
    }
    if request.method == 'POST':
        product_id = request.POST['product']
        max_price = float(request.POST['max_price'])
        sale_price = request.POST['sale_price']
        stock = request.POST['stock']
        thumbnail_image = request.FILES['image']
        is_active = request.POST['active']

        product = Products.objects.get(id = product_id)

        # Create the Product_Variant instance
        edit = Product_Variant.objects.get(id=id)
        edit.product = product
        edit.max_price = max_price
        edit.sale_price = sale_price
        edit.stock = stock
        edit.thumbnail_image = thumbnail_image
        edit.is_active = is_active
        edit.save()

        variant_attribute_ids = request.POST.getlist('variant')
        for attribute_id in variant_attribute_ids:
            if attribute_id:  # Check if attribute_id is not empty
                try:
                    attribute_value = Attribute_Value.objects.get(pk=attribute_id)
                    edit.attributes.add(attribute_value)
                except Attribute_Value.DoesNotExist:
                    # Handle the case where the Attribute_Value object does not exist
                    raise Http404("Attribute_Value with ID {} does not exist".format(attribute_id))

        return redirect('variant_list')
    return render(request, "admin_panel/variant_edit.html", context)