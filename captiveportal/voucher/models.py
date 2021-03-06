# Copyright (C) 2021 Grant Emsley <grant@emsley.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.db import models
from django.contrib.auth.models import Group

class PrintTemplate(models.Model):
    PRINT_TYPE_CHOICES = [
        ('Dymo', 'Dymo Labelwriter'),
        ('Paper', 'Regular Paper'),
    ]
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=16,choices=PRINT_TYPE_CHOICES,default="Paper")
    template = models.TextField(help_text="""<p>For regular paper templates, the template is a block of HTML that will be repeated once for each voucher code. The following text will be substituted in the template:</p>
        <ul>
            <li>#PORTALNAME# - The name of the portal
            <li>#SSID# - SSID set in the portal
            <li>#PSK# - Password set in the portal
            <li>#CODE# - The voucher code for this voucher
            <li>#TIMELIMIT# - The time limit set in the roll
            <li>#ROLLNUMBER# - The roll number
            <li>#ROLLDESCRIPTION# - The description of the roll
            <li>#LOOPCOUNTER# - The number of the ticket from this print job. Useful for creating unique HTML IDs
        </ul>
        <p>For Dymo Labelwriter templates, the template is a valid Dymo XML file. The following objects will be replaced with their corresponding values:</p>
        <ul>
            <li>PortalName
            <li>SSID
            <li>PSK
            <li>TimeLimit
            <li>VoucherCode
            <li>QRCode - replaced with the QR string to connect to the network, eg. WIFI:T:WPA;S:MySSID;P:MyPresharedKey;;
        </ul>
        <p>Note: The Dymo library does not properly parse Color tags without any content in them. Add a space between the opening and closing Color tags if you get an error.</p>
    """)

    def __str__(self):
        return self.name

class Portal(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    ssid = models.CharField(max_length=32, blank=True)
    psk = models.CharField(max_length=64, blank=True)
    active = models.BooleanField(default=True)
    allow_printing = models.ManyToManyField(Group, blank=True)
    print_templates = models.ManyToManyField(PrintTemplate, blank=False)

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

