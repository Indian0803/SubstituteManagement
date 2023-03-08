from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField, AuthenticationForm
from .models import User
from django.forms import formset_factory

# Form to create user


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'middle_name',
                  'last_name', 'role', 'subject', 'is_admin')
        widgets = {
            'schedule_uploaded': forms.HiddenInput(),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

# Form to edit user information


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password',
                  'is_active', 'is_admin', 'first_name', 'middle_name', 'last_name', 'role', 'subject')

    def clean_password(self):
        return self.initial["password"]


# Form to receive the day the teacher will be absent for
class AbsenceDayForm(forms.Form):
    day = forms.DateField()

    # possibly add option to choose today

    def __init__(self, year=None, *args, **kwargs):
        self.year = year
        super().__init__(*args, **kwargs)
        if year != None:
            self.fields["day"].widget = forms.SelectDateWidget(
                years=range(2000+year[0], 2000+year[1] + 1))

# Form to receive which period the teacher will miss


class AbsenceForm(forms.Form):
    period = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)

    def __init__(self, periods=None, *args, **kwargs):
        self.base_fields["period"].choices = periods
        super().__init__(*args, **kwargs)

# Form to receive message to send to substitute teacher


class MessageForm(forms.Form):
    message = forms.CharField(required=False,
                              widget=forms.widgets.Textarea(attrs={'rows': 10, 'cols': 60}))


# Creating formset to use multiple of these forms
MessageFormSet = formset_factory(MessageForm, extra=10)

# Form to receive email and password for login


class LoginForm(forms.Form):
    email = forms.CharField(label='メールアドレス', max_length=30)
    password = forms.CharField(
        label='パスワード', max_length=128, widget=forms.PasswordInput())
