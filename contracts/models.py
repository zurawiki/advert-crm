from django.contrib import admin
from django.db import models
from localflavor.us.models import USStateField, PhoneNumberField
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


class Issue(models.Model):
    title = models.CharField(_("Title"), max_length=128)
    volume = models.IntegerField(_("Volume"))
    issueNumber = models.IntegerField(_("Issue Number"))

    def __str__(self):
        return '%d, %d: %s' % (self.volume, self.issueNumber, self.title)

    class Meta:
        ordering = ['-volume', '-issueNumber']
        unique_together = ("volume", "issueNumber")


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'volume', 'issueNumber')
    list_filter = ('volume',)
    fieldsets = [('', {
        'fields': ('volume', 'issueNumber'),
    }),
                 ('', {
                     'fields': ('title',),
                 })]


class Advert(models.Model):
    SIZES = (
        ('1/4', 'Quarter Page'),
        ('1/3', 'Third Page'),
        ('1/2', 'Half Page'),
        ('2/3', 'Two-Thirds Page'),
        ('FUL', 'Full Page'),
        ('CTR', 'Center Spread')
    )
    advertiser = models.ForeignKey('Advertiser')
    size = models.CharField(max_length=3, choices=SIZES, default='1/3')
    description = models.TextField(_("Description"))
    imageFile = models.ImageField(_("Image File"), upload_to='adverts/%Y/%m')
    issues = models.ManyToManyField(Issue)
    finalPrice = models.DecimalField(_("Price"), max_digits=6, decimal_places=2, null=True)

    paid = models.BooleanField(_("Paid"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    notes = models.TextField(_("Notes"), null=True, blank=True, help_text="""
    Any notes of this contract. Remember to include how this contract was paid for.""")

    def __str__(self):
        return '(%s) %s: %s' % (self.size, self.advertiser, self.description)

    def issues_count(self):
        return self.issues.count()

    issues_count.short_description = _("Issues ordered")

    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    def get_absolute_url(self):
        from django.core.urlresolvers import reverse

        return reverse('contracts.views.detail', args=[str(self.id)])

    def salesperson(self):
        return self.advertiser.salesperson

    class Meta:
        ordering = ['-created_at']


class AdvertInline(admin.StackedInline):
    model = Advert


class AdvertAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = (
        'paid', 'description', 'advertiser', 'salesperson', 'issues_count', 'size', 'finalPrice', 'created_at')
    list_filter = ('advertiser', 'issues', 'paid', 'size')
    search_fields = ['description']

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser and \
                (obj is not None) \
                and obj.advertiser.salesperson \
                and (obj.advertiser.salesperson != request.user):
            return False
        else:
            return True


class Correspondence(models.Model):
    advertiser = models.ForeignKey('Advertiser')

    _from = models.CharField(_("From"), max_length=128)
    _to = models.CharField(_("To"), max_length=128)
    text = models.TextField()

    created_on = models.DateTimeField(_("Sent"), auto_now_add=True)

    ONE_TO_TEN = zip(range(1, 10), range(1, 10))
    receptive = models.PositiveSmallIntegerField(_("Receptiveness"), choices=ONE_TO_TEN, blank=True, null=True,
                                                 help_text="""
    enter a number from 1 to 10.""")

    def title(self):
        return self.text.splitlines()[0]

    def salesperson(self):
        return self.advertiser.salesperson

    def __unicode__(self):
        return self.title()


class CorrespondenceInline(admin.TabularInline):
    model = Correspondence


class CorrespondenceAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('title', '_from', '_to', 'created_on', 'receptive', 'salesperson')
    list_filter = ('advertiser', '_from', '_to')
    search_fields = ('advertiser', '_from', '_to', 'salesperson')
    readonly_fields = ('created_on',)

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser and \
                (obj is not None) \
                and obj.advertiser.salesperson \
                and (obj.advertiser.salesperson != request.user):
            return False
        else:
            return True


class Advertiser(models.Model):
    name = models.CharField(_("Organization"), max_length=128)

    address_1 = models.CharField(_("Address"), max_length=128)
    address_2 = models.CharField(_("Address continued"), max_length=128, null=True, blank=True)

    city = models.CharField(_("City"), max_length=64)
    state = USStateField(_("State"), max_length=2)
    zip_code = models.CharField(_("ZIP code"), max_length=5)

    contact = models.CharField(_("Contact"), max_length=128, help_text="""
    Please enter your name or the contact person for the company.""""")
    position = models.CharField(_("Position"), max_length=128)
    telephone = PhoneNumberField(_("Phone"), max_length=10, help_text="Use the format: 800-555-1212")
    email = models.EmailField(_("Email"))

    approved = models.BooleanField(_("Approved"), default=False, help_text="""
    This advertiser has been verified by Lampoon staff.""")

    salesperson = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'is_staff': True}, help_text="""
    This is the contact person on The Lampoon responsible for the client.""")


    def __unicode__(self):
        return self.name

    def address(self):
        if self.address_2:
            return "%s %s, %s, %s %s" % (self.address_1, self.address_2, self.city, self.state, self.zip_code)
        else:
            return "%s, %s, %s %s" % (self.address_1, self.city, self.state, self.zip_code)

    address.short_description = _("Mailing Address")


    @staticmethod
    def autocomplete_search_fields():
        return ("id__iexact", "name__icontains",)

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        if not request.user.is_superuser and \
                        obj is not None and \
                obj.approved and obj.salesperson != request.user:
            return False
        else:
            return True


class AdvertiserAdmin(admin.ModelAdmin):
    list_display = ('name', 'approved', 'salesperson', 'address', 'contact', 'position', 'telephone', 'email')
    list_filter = ('city', 'state', 'approved', 'salesperson')

    search_fields = ['name', 'contact', 'email', 'telephone']
    actions = ['approve', 'unapprove']

    inlines = [AdvertInline, CorrespondenceInline]

    def approve(self, request, queryset):
        for e in queryset:
            e.approved = True
            e.save()

    def unapprove(self, request, queryset):
        for e in queryset:
            e.approved = False
            e.save()