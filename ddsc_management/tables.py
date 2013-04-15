from django.contrib.auth.models import User
import django_tables2 as tables


class UserTable(tables.Table):
    roles = tables.Column(empty_values=(), sortable=False)

    class Meta:
        attrs = {"class": "paleblue"}
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "date_joined",
            "roles",
        )

    def render_roles(self, record):
        """Return the (lizard-security) groups a user belongs to."""
        roles = []
        for role in record.user_group_memberships.order_by("name"):
            roles.append(role.name)
        return ", ".join(roles)
