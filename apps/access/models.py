from django.db import models


class Role(models.Model):
    """User role (e.g. Admin, Manager, Warehouse Staff, Viewer)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(
        default=False,
        help_text='System roles cannot be deleted.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Permission(models.Model):
    """Custom permission definition."""
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255, help_text='Human-readable name')
    module = models.CharField(
        max_length=50,
        help_text='Module this permission belongs to (e.g. receipts, products)',
    )

    class Meta:
        ordering = ['module', 'codename']

    def __str__(self):
        return f'{self.module}: {self.name}'


class RolePermission(models.Model):
    """Maps a permission to a role with a granted flag."""
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='role_permissions',
    )
    granted = models.BooleanField(default=True)

    class Meta:
        unique_together = ('role', 'permission')
        ordering = ['role', 'permission']

    def __str__(self):
        status = 'granted' if self.granted else 'denied'
        return f'{self.role.name} → {self.permission.codename} ({status})'
