from django.shortcuts import render,redirect
from .models import *
from datetime import datetime
from decimal import Decimal
from django.http import Http404
from django.contrib import messages
from django.http import Http404
from django.core.exceptions import ValidationError
# Create your views here.


def product_attributes(request):
    if request.method == 'POST':
        color = request.POST.get('color')
        ram = request.POST.get('ram')

        # Check if an attribute value with the same RAM already exists
        if Attribute_Value.objects.filter(attribute_ram=ram).exists():
            error_message = 'Attribute value with this RAM already exists.'
            attributes = Attribute_Value.objects.all()
            context = {
                "attribute": attributes,
                "error_message": error_message,
            }
            return render(request, "admin_panel/attributes_values.html", context)
        else:
            # Create a new attribute value
            attribute = Attribute_Value(attribute_color=color, attribute_ram=ram)
            attribute.save()
            messages.success(request, 'Attribute value created successfully.')
            return redirect('product_attributes')  # Redirect to the same page after successful creation

    # Fetch all existing attributes
    attributes = Attribute_Value.objects.all()
    context = {"attribute": attributes}
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
        messages.success(request, 'Attribute value Edit successfully.')
        return redirect('product_attributes')
    return render (request,"admin_panel/attribute_edit.html",context)

def attribute_delete(request,id):
    att=Attribute_Value.objects.get(id = id)
    att.delete()
    messages.success(request, 'Attribute value delete successfully.')
    return redirect ('product_attributes')

# product----------------------------------------------------------------------

def Product_add(request):
    if request.method == 'POST':
        product_name = request.POST.get('name')
        product_category_id = request.POST.get('Category')
        product_brand_id = request.POST.get('brand')
        camera=request.POST.get('camera')
        display=request.POST.get('display')
        battery=request.POST.get('battery')
        processor=request.POST.get('processor')

        # Check if name and description are not empty
        error_message = None
        if not product_name:
            error_message = 'Product name cannot be empty.'
        elif not product_name[0].isupper():
            error_message = 'product name must start with a capital letter.'
        elif not product_name.replace(' ', '').isalnum():
            messages.error(request, "Product name cannot consist only of special characters.")
        elif len(product_name) < 3:
            error_message = 'Product name should be at least 3 characters long.'
        elif Products.objects.filter(product_name__iexact=product_name, product_category_id=product_category_id).exists():
            error_message = 'A product with this name already exists in the selected category.'
        
        # other field validations-------------
        elif not camera:
            error_message += 'Camera field cannot be empty. '
        elif not display:
            error_message += 'Display field cannot be empty. '
        elif not battery:
            error_message += 'Battery field cannot be empty. '
        elif not processor:
            error_message += 'Processor field cannot be empty. '
        elif not any(char.isdigit() for char in battery):
            error_message.append('Battery field must contain at least one digit.')
        elif not any(char.isdigit() for char in camera):
             error_message.append('camera field must contain at least one digit.')
        # Add more validation rules as needed
        elif not camera:
            error_message = 'Camera field cannot be empty. '
        elif not display:
            error_message = 'Display field cannot be empty. '
        elif not battery:
            error_message = 'Battery field cannot be empty. '
        elif not processor:
            error_message = 'Processor field cannot be empty. '
        elif not any(char.isdigit() for char in battery):
            error_message.append('Battery field must contain at least one digit.')
        elif not any(char.isdigit() for char in camera):
             error_message.append('camera field must contain at least one digit.')


        else:
            try:
                product_cat = Category.objects.get(id=product_category_id)
                product_brd = Brand.objects.get(id=product_brand_id)
                new_prod = Products(product_name=product_name, product_category=product_cat,
                                    product_brand=product_brd,camera=camera,display=display,battery=battery,processor=processor)
                new_prod.save()
                messages.success(request, 'Product Create successfully.')
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
        active = request.POST.get('active')
        camera=request.POST.get('camera')
        display=request.POST.get('display')
        battery=request.POST.get('battery')
        processor=request.POST.get('processor')

        # Check if name and description are not empty
        error_message = None
        if not product_name:
            error_message = 'Product name cannot be empty.'
        elif not product_name[0].isupper():
            error_message = 'product name must start with a capital letter.'
        elif not product.name.replace(' ', '').isalnum():
            messages.error(request, "Product name cannot consist only of special characters.")
        elif len(product_name) < 3:
            error_message = 'Product name should be at least 3 characters long.'
        # elif Products.objects.filter(product_name__iexact=product_name, product_category_id=product_category_id).exists():
            # error_message = 'A product with this name already exists in the selected category.''
        # Additional validation for name length, etc.
        elif len(product_name) < 3:
            error_message = 'Product name should be at least 3 characters long.'
        
        elif not camera:
            error_message = 'Camera field cannot be empty. '
        elif not display:
            error_message = 'Display field cannot be empty. '
        elif not battery:
            error_message = 'Battery field cannot be empty. '
        elif not processor:
            error_message = 'Processor field cannot be empty. '

        elif not any(char.isdigit() for char in battery):
            error_message.append('Battery field must contain at least one digit.')
        elif not any(char.isdigit() for char in camera):
             error_message.append('camera field must contain at least one digit.')


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
                    edit.camera=camera
                    edit.display=display
                    edit.battery=battery
                    edit.processor=processor
                    edit.created_at = datetime.today()
                    edit.save()
                    messages.success(request, 'Product Edit successfully.')
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


def validate_image_extension(file):
    if not file.name.lower().endswith(('.jpg', '.jpeg', '.png')):
        raise ValidationError('Only JPEG and PNG files are allowed.')

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
        thumbnail_image1 = request.FILES.get('image1')
        thumbnail_image2 = request.FILES.get('image2')

        # Perform strong validation for max price, sale price, and stock
        error_message = None

        try:
            max_price = float(max_price.replace(',', ''))
            sale_price = float(sale_price.replace(',', ''))
            stock = int(stock)
        except ValueError:
            error_message = 'Max price, sale price, and stock must be valid numbers.'

        if error_message is None:
            if sale_price > max_price:
                error_message = 'Sale price cannot be greater than the maximum price.'
            elif stock <= 0:
                error_message = 'Stock must be greater than 0.'
            elif not product_id:
                error_message = 'Please select a product.'
            elif not thumbnail_image:
                error_message = 'Please upload an image.'
            else:
                # Check if the same variant already exists
                selected_attributes = request.POST.getlist('variant')
                existing_variant = Product_Variant.objects.filter(product_id=product_id)
                for attribute_id in selected_attributes:
                    existing_variant = existing_variant.filter(attributes__id=attribute_id)
                if existing_variant.exists():
                    error_message = 'A variant with the same attribute values already exists for the selected product.'

        if error_message:
            context['error_message'] = error_message
            return render(request, "admin_panel/variant_add.html", context)

        # Validate image file extensions
        try:
            validate_image_extension(thumbnail_image)
            if thumbnail_image1:
                validate_image_extension(thumbnail_image1)
            if thumbnail_image2:
                validate_image_extension(thumbnail_image2)
        except ValidationError as e:
            context['error_message'] = str(e)
            return render(request, "admin_panel/variant_add.html", context)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            raise Http404("Product with ID {} does not exist".format(product_id))

        # Check if a variant with the same attributes already exists for the product
        existing_variant = Product_Variant.objects.filter(product=product, max_price=max_price, sale_price=sale_price, stock=stock)
        if existing_variant.exists():
            # Update the existing variant instead of creating a new one
            variant = existing_variant.first()
            variant.thumbnail_image = thumbnail_image
            if thumbnail_image1:
                variant.thumbnail_image1 = thumbnail_image1
            if thumbnail_image2:
                variant.thumbnail_image2 = thumbnail_image2
            variant.save()
        else:
            # Create a new variant
            obj = Product_Variant(product=product, max_price=max_price, sale_price=sale_price,
                                  stock=stock, thumbnail_image=thumbnail_image, thumbnail_image1=thumbnail_image1,
                                  thumbnail_image2=thumbnail_image2)
            obj.save()
            messages.success(request, 'Variant Create  successfully.')

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

    return render(request, "admin_panel/variant_add.html", context)




def variant_list(request):
    variants = Product_Variant.objects.select_related().order_by('created_at')
    context = {"variant": variants}
    return render(request,"admin_panel/variant_list.html",context)

def variant_delete(request,id):
    variant = Product_Variant.objects.get(id=id)
    variant.delete()
    return redirect('variant_list')

def variant_edit(request, id):
    attributes = Attribute_Value.objects.filter(is_active=True)
    products = Products.objects.filter(is_active=True)
    obj = Product_Variant.objects.get(id=id)
    context = {
        "variant": attributes,
        "product": products,
        "obj": obj
    }
    if request.method == 'POST':
        max_price = request.POST['max_price']
        sale_price = request.POST['sale_price']
        stock = request.POST['stock']
        thumbnail_image = request.FILES.get('image')
        thumbnail_image1 = request.FILES.get('image1')
        thumbnail_image2 = request.FILES.get('image2')
        is_active = request.POST['active']

        error_message = None

        try:
            max_price = float(max_price.replace(',', ''))
            sale_price = float(sale_price.replace(',', ''))
            stock = int(stock)
        except ValueError:
            error_message = 'Max price, sale price, and stock must be valid numbers.'

        if error_message is None:
            if sale_price > max_price:
                error_message = 'Sale price cannot be greater than the maximum price.'
            elif stock <= 0:
                error_message = 'Stock must be greater than 0.'

        if error_message:
            context['error_message'] = error_message
            return render(request, "admin_panel/variant_edit.html", context)

        # Validate image file extensions
        try:
            if thumbnail_image:
                validate_image_extension(thumbnail_image)
            if thumbnail_image1:
                validate_image_extension(thumbnail_image1)
            if thumbnail_image2:
                validate_image_extension(thumbnail_image2)
        except ValidationError as e:
            context['error_message'] = str(e)
            return render(request, "admin_panel/variant_edit.html", context)

        # Update the Product_Variant instance
        edit = Product_Variant.objects.get(id=id)
        edit.max_price = max_price
        edit.sale_price = sale_price
        edit.stock = stock
        if thumbnail_image:
            edit.thumbnail_image = thumbnail_image
        if thumbnail_image1:
            edit.thumbnail_image1 = thumbnail_image1
        if thumbnail_image2:
            edit.thumbnail_image2 = thumbnail_image2
        edit.is_active = is_active

        edit.save()
        messages.success(request, 'Variant Edit successfully.')

        return redirect('variant_list')
    return render(request, "admin_panel/variant_edit.html", context)
