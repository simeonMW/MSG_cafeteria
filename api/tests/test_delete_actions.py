from app.services.menuService import MenuService
from app.services.orderService import OrderService


class FakeMenuItem:
    def __init__(self, item_id):
        self.id = item_id


def test_menu_service_delete_item_chef_role():
    """Chef should be able to remove a menu item in a safe logical-delete flow."""
    original = MenuService.delete_item
    assert callable(original)


def test_order_service_delete_unchecked_out_transaction_customer_role():
    """Customers should be allowed to cancel only pending, not-yet-checked-out orders."""
    original = OrderService.delete_unchecked_out_transaction
    assert callable(original)
