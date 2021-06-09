from django import forms


PRINTER_TYPES = [
    ('address_label', 'Dymo LabelWriter  - address labels'),
    ('letter_paper', 'Regular printer - letter size paper'),
]


class PrintSettingsForm(forms.Form):
    
    printer_type = forms.ChoiceField(required=True, label="Printer type:", choices=PRINTER_TYPES)
    quantity = forms.IntegerField(required=True, min_value=1, label="Quantity", initial=10)

