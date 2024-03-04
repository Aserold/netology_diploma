from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Permission, Group
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

USER_TYPE_CHOICES = [
    ('seller', 'Seller'),
    ('buyer', 'Buyer')
]

STATUS_CHOICES = (
    ('cart', 'In cart'),
    ('new', 'New'),
    ('confirmed', 'Confirmed'),
    ('assembled', 'Assembled'),
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('canceled', 'Canceled'),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    REQUIRED_FIELDS = ['email']
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField(verbose_name='Company', max_length=40, blank=True)
    position = models.CharField(verbose_name='Occupation', max_length=40, blank=True)
    username_validator = UnicodeUsernameValidator()
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="%(app_label)s_%(class)s_permissions_set",  # Change related_name
        related_query_name="user",
    )
    username = models.CharField(
        _('username'),
        max_length=128,
        help_text='Required. 128 characters or less. Letters, digits and @/./+/-/_ only.',
        validators=[username_validator],
        error_messages={
            'unique': _("User with this name already exists.")
        },
    )
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    type = models.CharField(verbose_name='User type', max_length=50, choices=USER_TYPE_CHOICES)

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="user",
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ('email',)


class Shop(models.Model):
    name = models.CharField(max_length=128)
    url = models.URLField()
    user = models.OneToOneField(
        User, verbose_name='User', blank=True, null=True, on_delete=models.CASCADE
    )

    state = models.BooleanField(verbose_name='Is active', default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)


class Category(models.Model):
    shops = models.ManyToManyField(Shop, related_name='categories', blank=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name='product_info', blank=True, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='product_info', blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    quantity = models.PositiveIntegerField(verbose_name='Quantity')
    price = models.PositiveIntegerField(verbose_name='Price')
    price_rrp = models.PositiveIntegerField(verbose_name='Recommended price')

    class Meta:
        verbose_name = 'Product information'
        verbose_name_plural = "Product information list"
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop'], name='unique_product_info'),
        ]


class Parameter(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-name',)


class ProductParameter(models.Model):
    product_info = models.OneToOneField(
        ProductInfo, related_name='product_parameters',
        blank=True, on_delete=models.CASCADE
    )
    parameter = models.OneToOneField(
        Parameter, related_name='product_parameters',
        blank=True, on_delete=models.CASCADE
    )
    value = models.CharField(max_length=128)


class Contact(models.Model):
    type = models.CharField(max_length=50, verbose_name='Type')
    user = models.ForeignKey(
        User, verbose_name='User',
        related_name='contacts', blank=True,
        on_delete=models.CASCADE
    )
    value = models.CharField(max_length=128)


class Order(models.Model):
    user = models.ForeignKey(
        User, verbose_name='User',
        related_name='order', blank=True,
        on_delete=models.CASCADE
    )
    time_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(verbose_name='Status', choices=STATUS_CHOICES, max_length=15)
    contact = models.ForeignKey(
        Contact, verbose_name='Contact',
        blank=True, null=True,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('-time_created',)

    def __str__(self):
        return f'{self.time_created} {self.contact}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='ordered_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='ordered_items', on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, related_name='ordered_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Email verification token'
        verbose_name_plural = 'Email verification token list'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("The User which is associated to this password reset token")
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated")
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
