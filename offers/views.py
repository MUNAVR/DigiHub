from django.shortcuts import render
from .models import *
from datetime import datetime
from django.contrib import messages
from django.shortcuts import render,redirect
from products.models import Products, Product_Variant
from category.models import Brand
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
# Create your views here.


def create_offer(request):
    if request.method == 'POST':
       
        offer_type = request.POST.get('offer_type')
        discount_percentage = request.POST.get('discount_percentage')
        maximum_discount_amount = request.POST.get('maximum_discount_amount')
        minimum_discount_amount = request.POST.get('minimum_discount_amount')
        valid_to = request.POST.get('valid_to')

         # Perform validation
        error_messages = []

        # Validation for discount percentage
        try:
            discount_percentage = float(discount_percentage.replace('%', ''))
            if not 1 < discount_percentage <= 100:
                error_messages.append("Discount percentage must be between 1 and 100%.")
        except ValueError:
            error_messages.append("Invalid discount percentage format. Please provide a number without special characters.")


         # Validation for maximum discount amount
        try:
            maximum_discount_amount = float(maximum_discount_amount.replace(',', ''))
            if maximum_discount_amount <= 1:
                error_messages.append("Maximum discount amount must be greater than 1.")
        except ValueError:
            error_messages.append("Invalid maximum discount amount format. Please provide a valid number.")


         # Validation for minimum discount amount
        try:
            minimum_discount_amount = float(minimum_discount_amount.replace(',', ''))
            if minimum_discount_amount < 1:
                error_messages.append("Minimum discount amount must be greater than or equal to 1.")
        except ValueError:
            error_messages.append("Invalid minimum discount amount format. Please provide a valid number.")

        if error_messages:
            # If there are validation errors, render the form with error messages
            product = Products.objects.filter(is_active=True)
            brand = Brand.objects.filter(is_active=True)
            customers = Customers.objects.filter(is_blocked=False)
            context = {
                "product": product,
                "brand": brand,
                "customers": customers,
                "error_messages": error_messages
            }
            return render(request, 'admin_panel/create_offer.html', context)


        if offer_type == 'referral':
            referral_code = request.POST.get('referral_code')
            referred_by = request.POST.get('referred_by')
            try:
                referred=Customers.objects.get(id=referred_by)
                offer = ReferralOffer(
                    discount_percentage=discount_percentage,
                    maximum_discountAmount=maximum_discount_amount,
                    minimum_discountAmount=minimum_discount_amount,
                    valid_to=valid_to,
                    referral_code=referral_code,
                    referred_by=referred
                )
                offer.save()
                messages.success(request, "Offer created successfully.")
                return redirect('referral_offer_list')
            except Products.DoesNotExist:
                return HttpResponse("Product with the provided name does not exist.")
            
        elif offer_type == 'product':
            product_name = request.POST.get('product_name')
            print(product_name)
            try:
                products = Products.objects.get(id=product_name)
                print(products)
                offer = ProductOffer(
                    discount_percentage=discount_percentage,
                    maximum_discountAmount=maximum_discount_amount,
                    minimum_discountAmount=minimum_discount_amount,
                    valid_to=valid_to,
                    product=products
                )
                offer.save()
                messages.success(request, "Offer created successfully.")
                return redirect('product_offer_list')
            except Products.DoesNotExist:
                return HttpResponse("Product with the provided name does not exist.")
        elif offer_type == 'brand':
            brand_name = request.POST.get('brand_name')
            try:
                brand = Brand.objects.get(id=brand_name)
                offer = BrandOffer(
                    discount_percentage=discount_percentage,
                    maximum_discountAmount=maximum_discount_amount,
                    minimum_discountAmount=minimum_discount_amount,
                    valid_to=valid_to,
                    brand=brand
                )
                offer.save()
                messages.success(request, "Offer created successfully.")
                return redirect('brand_offer_list')
            except Brand.DoesNotExist:
                return HttpResponse("Brand with the provided name does not exist.")
    
    product = Products.objects.filter(is_active=True)
    brand = Brand.objects.filter(is_active=True)
    customers = Customers.objects.filter(is_blocked=False)
    context = {
        "product": product,
        "brand": brand,
        "customers": customers
    }
    return render(request, 'admin_panel/create_offer.html', context)


def product_offer_list(request):
    offers=ProductOffer.objects.all()
    context={
        "offers":offers
    }
    return render(request,"admin_panel/product_offer_list.html",context)

def referral_offer_list(request):
    offers= ReferralOffer.objects.all()
    context={
        "offers":offers
    }
    return render(request,"admin_panel/referral_offer_list.html",context)

def brand_offer_list(request):
    offers=BrandOffer.objects.all()
    context={
        "offers":offers
    }
    return render(request,"admin_panel/brand_offer_list.html",context)



def get_offers(request):
    product_offers = ProductOffer.objects.all()
    brand_offers = BrandOffer.objects.all()

    # Prepare offer data
    offers = []
    for offer in product_offers:
        offers.append({"type": "Product", "discount_percentage": offer.discount_percentage})
    for offer in brand_offers:
        offers.append({"type": "Brand", "discount_percentage": offer.discount_percentage})

    return JsonResponse(offers, safe=False)