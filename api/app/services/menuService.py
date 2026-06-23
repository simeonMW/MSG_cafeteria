from app.repositories.menuRepo import MenuRepo


class MenuService:
    """
    Logic for Menu Management.
    Coordinates between the Chef's actions and the D2: Menu data store.
    """

    @staticmethod
    def get_public_menu():
        """
        Logic for Process 3.1 (Fetch Menu).
        Filters out unavailable items to provide a clean list for the Customer App.
        """
        items = MenuRepo.get_active_menu()
        return [item.to_dict() for item in items]

    @staticmethod
    def get_full_inventory(role):
        """
        Provides the Chef with the full list of items, including disabled ones.
        Enforces role-based access to administrative views.
        """
        if role != 'chef':
            return None, "Unauthorized: Only the Chef can view full inventory."
        
        items = MenuRepo.get_all_for_admin()
        return [item.to_dict() for item in items], None


    @staticmethod
    def add_item(item_data, role):
        """
        Logic for Process 2.1 (Menu Entry).
        Ensures data integrity before the Chef adds a new resource to D2.
        """
        if role != 'chef':
            return None, "Unauthorized: Only the Chef can add menu items."

        # Audit Check: Ensure price is non-negative
        if int(item_data.get('price', 0)) < 0:
            return None, "Invalid Price: Items cannot have a negative value."

        new_item = MenuRepo.create(item_data)
        return new_item.to_dict(), "Item added successfully."

    @staticmethod
    def update_item_details(item_id, update_data, role):
        """
        Logic for Process 2.2 (Menu Update).
        Handles updates to pricing, availability, or descriptions.
        """
        if role != 'chef':
            return None, "Unauthorized: Only the Chef can modify menu items."

        updated_item = MenuRepo.update(item_id, update_data)
        if not updated_item:
            return None, "Item not found."

        return updated_item.to_dict(), "Item updated successfully."

    @staticmethod
    def toggle_item_status(item_id, role):
        """
        Quick action logic for the Chef to mark an item as 
        'Out of Stock' without editing the whole record.
        """
        if role != 'chef':
            return None, "Unauthorized."
            
        item = MenuRepo.toggle_availability(item_id)
        if item:
            status = "available" if item.is_available else "unavailable"
            return {"id": item.id, "status": status}, f"Item is now {status}."
        return None, "Item not found."