from django.db import models

from django.conf import settings
from mainapp.models import Product


class Order(models.Model):
    FORMING = 'FM'
    SENT_TO_PROCEED = 'STP'
    PROCEEDED = 'PRD'
    PAID = 'PD'
    READY = 'RD'
    CANCEL = 'CNC'
    DELIVERED = 'DVD'

    STATUSES = (
        (FORMING, 'формируется'),
        (SENT_TO_PROCEED, 'отправлен в обработку'),
        (PAID, 'оплачен'),
        (PROCEEDED, 'обработан'),
        (READY, 'готов к выдаче'),
        (CANCEL, 'отменен'),
        (DELIVERED, 'выдан'),

    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='создан', auto_now_add=True)
    updated = models.DateTimeField(verbose_name='обновлен', auto_now=True)
    status = models.CharField(verbose_name='статус', choices=STATUSES, default=FORMING, max_length=3)
    is_active = models.BooleanField(verbose_name='активен', default=True)

    def get_total_quantity(self):
        _items = self.orderitems.select_related()
        _totalquantiti = sum(list(map(lambda x: x.quantity, _items)))
        return _totalquantiti

    def get_total_cost(self):
        _items = self.orderitems.select_related()
        _totalquantiti = sum(list(map(lambda x: x.get_product_cost(), _items)))
        return _totalquantiti

    def delete(self):
        for item in self.orderitems.select_related():
            item.product.quantity += item.quantity
            item.product.save()

        self.is_active = False
        self.save()


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="orderitems", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name='продукт', on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(verbose_name='количество', default=0)

    def get_product_cost(self):
        return self.product.price * self.quantity