from django.db import models
from django.contrib.auth.models import Group

class Portal(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ssid = models.CharField(max_length=32, blank=True)
    psk = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)
    allow_printing = models.ManyToManyField(Group, blank=True)

    def __str__(self):
        return self.name

    def roll_count(self):
        return self.roll_set.count()

    def available_rolls(self):
        return self.roll_set.filter(active=True)

class Roll(models.Model):
    portal = models.ForeignKey(Portal, on_delete=models.CASCADE)
    number = models.IntegerField()
    description = models.CharField(max_length=200)
    time_limit = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    voucher_csv = models.FileField(null=True,blank=True)

    def __str__(self):
        return "%s - %s" %(self.portal.name, self.description)

    def save(self, *args, **kwargs):
        """Save the database record and file, then process the file and delete it."""
        super(Roll, self).save(*args, **kwargs)
        if self.voucher_csv and hasattr(self.voucher_csv, 'url'):
            voucherfile = self.voucher_csv.open(mode='r')
            for line in voucherfile.read().splitlines():
                if line.startswith("#"):
                    continue

                vouchercode = line.strip("\" ")

                # Skip vouchers that already exist in the database.
                if(Voucher.objects.filter(code=vouchercode).exists()):
                    continue

                self.voucher_set.create(code=vouchercode)

            self.voucher_csv.delete()


    def total_vouchers(self):
        return self.voucher_set.count()

    def remaining_vouchers(self):
        return self.voucher_set.filter(date_printed__isnull=True).count()

class Voucher(models.Model):
    roll = models.ForeignKey(Roll, on_delete=models.CASCADE)
    code = models.CharField(max_length=30, unique=True)
    date_printed = models.DateTimeField('date printed', null=True, blank=True)
    printed_by = models.CharField(max_length=200, blank=True)

    def portal(self):
        return self.roll.portal.name
