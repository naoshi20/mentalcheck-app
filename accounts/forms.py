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
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils.text import capfirst
from check.views import save_answer
import json
from urllib.parse import urlencode


User = get_user_model()


def get_activate_url(user, params):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return str(settings.FRONTENDURL) + "/accounts/activate/{}/{}/?{}".format(uid, token, params)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="メールアドレス")
    password1 = forms.CharField(required=True, label="パスワード", widget=forms.PasswordInput)
    #phone = forms.CharField(required=True, label="電話番号（ハイフンなし）", max_length=16)
    answers = forms.CharField(required=False, label="", widget=forms.HiddenInput)

    class Meta:
        model = User
        fields = ('email', 'password1')#, 'phone'

    def save(self, commit=True):
        # commit=Falseだと、DBに保存されない
        user = super().save(commit=False)
        print(user)
        user.email = self.cleaned_data["email"]

        # 確認するまでログイン不可にする
        user.is_active = False

        #クエリパラメータに回答があれば保存する。
        print(self.cleaned_data["answers"])

        #回答があれば
        q_a = json.loads(self.cleaned_data["answers"])
        params = ''
        if 'question_stress_1' in q_a.keys():
            # url = f'{redirect_url}?{parameters}'
            params = urlencode(q_a)
            print(q_a)
            print(params)
            #save_answer(q_a, user)

        if commit:
            user.save()
            activate_url = get_activate_url(user, params)
            from_email = "graspy@diix.info"
            to_emails = [user.email]
            subject = "登録確認"
            message = 'Graspyのご利用ありがとうございます。\n現在お客様のアカウントは仮登録状態です。\n以下のURLをクリック/タップして登録を完了させてください。\n\n' + activate_url
            send_mail(subject, message, from_email, to_emails, fail_silently=False)
            #user.email_user(subject, message)
        return user
    
    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        del self.fields['password2']
        self.fields['password1'].help_text = None
        for field in self.fields.values():
            field.widget.attrs['placeholder'] = field.label 

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
    error_messages = {
        'invalid_login': ["メールアドレスかパスワードが間違っています。"],
        'inactive': ["このアカウントは存在しません。"],
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.label == 'Email address':
                field.label = 'メールアドレス'
            elif field.label == 'Password':
                field.label = 'パスワード'
            else:
                pass
            field.widget.attrs['placeholder'] = field.label



