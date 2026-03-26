class PermissionPerActionMixin:
    """Mixin to allow different permissions per action in ViewSets or APIViews."""
    def get_permissions(self):
        if hasattr(self, "permissions_per_action"):
            current_action = getattr(self, "action", self.request.method.lower())
            if current_action in self.permissions_per_action:
                permission_classes = self.permissions_per_action[current_action]
            else:
                permission_classes = self.permission_classes
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]
