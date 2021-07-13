from django.dispatch import receiver
from django.shortcuts import render

from django.shortcuts import get_object_or_404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.db import transaction
from django.db.models.signals import pre_save, pre_delete

from django.forms import inlineformset_factory

from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView

from basketapp.models import Basket
from ordersapp.forms import OrderItemEditForm
from ordersapp.models import Order, OrderItem


class OrderList(ListView):
   model = Order

   def get_queryset(self):
       return Order.objects.filter(user=self.request.user, is_active=True)

class OrderCreate(CreateView):
   model = Order
   success_url = reverse_lazy('order:list')
   fields = []

   def get_context_data(self, **kwargs):
       data = super().get_context_data(**kwargs)
       OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=1)

       if self.request.POST:
           formset = OrderFormSet(self.request.POST)
       else:
           basket_items = list(Basket.objects.filter(user=self.request.user))
           if len(basket_items):
               OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=len(basket_items))
               formset = OrderFormSet()
               for num, form in enumerate(formset.forms):
                   form.initial['product'] = basket_items[num].product
                   form.initial['quantity'] = basket_items[num].quantity
                   form.initial['price'] = basket_items[num].product.price
               for basket_item in basket_items:
                   basket_item.delete()
               # basket_items.delete()
           else:
               formset = OrderFormSet()

       data['orderitems'] = formset
       return data
   def form_valid(self, form):
       context = self.get_context_data()
       orderitems = context['orderitems']

       with transaction.atomic():
           form.instance.user = self.request.user
           self.object = form.save()
           if orderitems.is_valid():
               orderitems.instance = self.object
               orderitems.save()
       if self.object.get_total_cost() == 0:
           self.object.delete()
       return super().form_valid(form)

class OrderUpdate(UpdateView):
    model = Order
    success_url = reverse_lazy('order:list')
    fields = []

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        OrderFormSet = inlineformset_factory(Order, OrderItem, form=OrderItemEditForm, extra=1)

        if self.request.POST:
            data['orderitems'] = OrderFormSet(self.request.POST, instance=self.object)
        else:
            orderitems_fromset = OrderFormSet(instance=self.object)
            for form in orderitems_fromset.forms:
                if form.instance.pk:
                    form.initial['price'] = form.instance.product.price
            data['orderitems'] = orderitems_fromset
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        orderitems = context['orderitems']

        with transaction.atomic():
            # form.instance.user = self.request.user
            self.object = form.save()
            if orderitems.is_valid():
                orderitems.instance = self.object
                orderitems.save()
        if self.object.get_total_cost() == 0:
            self.object.delete()
        return super().form_valid(form)



class OrderDelete(DeleteView):
    model = Order
    success_url = reverse_lazy('order:list')


class OrderRead(DetailView):
    model = Order
    success_url = reverse_lazy('order:list')
def forming_complete(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order.status = Order.SENT_TO_PROCEED
    order.save()

    return HttpResponseRedirect(reverse('order:list'))

# @receiver(pre_save, sender=Order)
# @receiver(pre_save, sender=Basket)
# def products_quantity_update_save(sender, update_fields, instance, **kwargs):
#     # if 'product' in update_fields or 'quantity' in update_fields:
#     if instance.pk:
#        instance.product.quantity -= instance.quantity - instance.get_item(instance.pk).quantity
#     else:
#        instance.product.quantity -= instance.quantity
#     instance.product.save()
#
#
# @receiver(pre_delete, sender=Order)
# @receiver(pre_delete, sender=Basket)
# def products_quantity_update_delete(sender, instance, **kwargs):
#    instance.product.quantity += instance.quantity
#    instance.product.save()

def get_product_price(request, pk):
    if request.is_ajax():
        product = Product.objects.filter(pk=pk).first()
        if product:
            return JsonResponse({'price': product.price})
        else:
            return JsonResponse({'price': 0})
