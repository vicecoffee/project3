from django import forms
from django.contrib.auth.models import User
from orders.models import Order_item, Menu_item
import re

# Most of the account forms are built in, but I couldn't find a registration form class
# From https://docs.djangoproject.com/en/2.0/topics/forms/

class RegisterForm(forms.Form):
    username = forms.CharField(label='User name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    firstname = forms.CharField(label='First name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    lastname = forms.CharField(label='Last name', widget=forms.TextInput(attrs={"class": "form-control"}), max_length=100)
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label='Password')
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), label='Confirm password')
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}), label='Email address')

    # Make sure the password is typed twice for confirmation
    # From https://docs.djangoproject.com/en/2.0/ref/forms/validation/
    # From https://stackoverflow.com/questions/34609830/django-modelform-how-to-add-a-confirm-password-field
    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("password_confirm")

        if password != confirm_password:
            raise forms.ValidationError('Please make sure that "Password" and "Confirm Password" match')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("The requested user name is already taken.  Please try another name.")

class AddItemForm(forms.ModelForm):
    class Meta:
        model = Order_item
        fields = ["size", "quantity", "toppings", "extras", "id"]
        widgets = {
            "toppings": forms.CheckboxSelectMultiple,
            "extras": forms.CheckboxSelectMultiple,
            "size": forms.RadioSelect
        }

    id = forms.IntegerField(widget=forms.HiddenInput())

    def clean(self):
        cleaned_data = super(AddItemForm, self).clean()

        # Match the correct number of toppings using regular expressions
        # From https://docs.python.org/2/howto/regex.html
        toppings_match = re.compile(r'(?P<count>\d+) (topping(s)?|item(s)?)', re.IGNORECASE)
        match_results = toppings_match.match(self.item_model.name)
        topping_count = int(match_results.group("count")) if match_results else 0

        if topping_count and cleaned_data["toppings"].count() != topping_count:
            raise forms.ValidationError(
                "Please select exactly {} topping(s) for a {} pizza.".format(topping_count, self.item_model.name)
                )

        if "special" in self.item_model.name.lower() and cleaned_data["toppings"].count() <= 3:
            raise forms.ValidationError(
                "Please select more than 3 toppings for a {} pizza.".format(self.item_model.name)
                )

    # Add some data from a menu item into the form
    def __init__(self, *args, **kwargs):
        self.item_model = item_model = kwargs.pop("item_model")
        super(AddItemForm, self).__init__(*args, **kwargs)

        self.fields["id"].initial = item_model.id

        extras = item_model.extras
        toppings = item_model.toppings

        if extras.count() == 0:
            del self.fields["extras"]

        if toppings.count() == 0:
            del self.fields["toppings"]

        # Convert the choices in the model into a set then use list comprehension to remove the "NA" choice, then
        # convert it back to a tuple
        if item_model.has_sizes:
            self.fields["size"].choices = tuple(choice for choice in set(Order_item.SIZE_CHOICES) if choice[0] != Order_item.NA)
            self.fields["size"].initial = Order_item.SMALL
        else:
            del self.fields["size"]
