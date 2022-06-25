from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from datetime import datetime
#from .models import Profile
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.core.mail import send_mail


User = get_user_model()


def get_activate_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return str(settings.FRONTENDURL) + "/accounts/activate/{}/{}/".format(uid, token)


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="メールアドレス")
    password1 = forms.CharField(
        required=False, label="パスワード", widget=forms.PasswordInput)
    password2 = forms.CharField(
        required=False, label="パスワード（確認）", widget=forms.PasswordInput)
    phone = forms.CharField(required=False, label="電話番号", max_length=16)

    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'phone')

    def save(self, commit=True):
        # commit=Falseだと、DBに保存されない
        user = super().save(commit=False)
        print(user)
        user.email = self.cleaned_data["email"]

        # 確認するまでログイン不可にする
        user.is_active = False

        if commit:
            user.save()
            activate_url = get_activate_url(user)
            #message = message_template + activate_url
            from_email = "graspy@diix.info"  # settings.DEFAULT_FROM_EMAIL
            to_emails = [user.email]  # user.email
            subject = "登録確認"
            message = 'Graspyのご利用ありがとうございます。\n現在お客様のアカウントは仮登録状態です。\n以下のURLをクリック/タップして登録を完了させてください。\n\n' + activate_url
            send_mail(subject, message, from_email,
                      to_emails, fail_silently=False)
            #user.email_user(subject, message)
        return user


def activate_user(uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except Exception:
        return False

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return True

    return False


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            # 全てのフォームの部品にplaceholderを定義して、入力フォームにフォーム名が表示されるように指定する
            field.widget.attrs['placeholder'] = field.label
