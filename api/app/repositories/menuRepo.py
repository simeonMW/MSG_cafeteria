from app.models.menuItem import MenuItem, db




class MenuRepo:
    """
    Data Access Layer for D2: Menu.
    CRUD operations for menu items managed by the Chef.
    """

    @staticmethod
    def create(item_data):
        """
        Implementation of DFD 2.1 (Menu Entry).
        enters a new menu item to the D2 data store.
        """
        new_item = MenuItem(
            name=item_data.get('name'),
            description=item_data.get('description'),
            type=item_data.get('type', 'staple'),
            price=item_data.get('price'),
            picture_url=item_data.get('picture_url'),
            is_available=item_data.get('is_available', True)
        )
        db.session.add(new_item)
        db.session.commit()
        return new_item

    @staticmethod
    def get_by_id(item_id):
        """
        Retrieves a specific item. Used during Process 3.2 (Transaction)
        to fetch the 'order_price' snapshot.
        """
        return MenuItem.query.get(item_id)

    @staticmethod
    def get_active_menu():
        """
        Implementation of DFD 3.1 (Fetch Menu Process).
        Returns only items where is_available is True for the Customer view.
        """
        return MenuItem.query.filter_by(is_available=True).all()

    @staticmethod
    def get_all_for_admin():
        """
        Provides the Chef with a full list of all items, 
        including those currently hidden from customers.
        """
        return MenuItem.query.all()

    @staticmethod
    def update(item_id, updated_data):
        """
        Implementation of DFD 2.2 (Menu Update Process).
        Updates existing menu details and commits changes to D2.
        """
        item = MenuItem.query.get(item_id)
        if item:
            for key, value in updated_data.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            db.session.commit()
            return item
        return None

    @staticmethod
    def toggle_availability(item_id):
        """
        A specific control for the Chef to quickly enable/disable an item
        without performing a full update.
        """
        item = MenuItem.query.get(item_id)
        if item:
            item.is_available = not item.is_available
            db.session.commit()
            return item
        return None

    @staticmethod
    def delete_logical(item_id):
        """
        Audit-safe 'deletion'. Sets availability to False instead of 
        removing the row, preserving foreign key integrity in Transactions.
        """
        item = MenuItem.query.get(item_id)
        if item:
            item.is_available = False
            db.session.commit()
            return True
        return False