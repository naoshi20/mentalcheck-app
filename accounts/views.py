from .forms import SignUpForm, LoginForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from .forms import activate_user
import json
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404, render
from django.conf import settings

class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:verification")
    template_name = "registration/signup.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        print(ctx)
        ctx['question_list'] = {}
        for key in dict(self.request.GET).keys():
            ctx['question_list'][key] = self.request.GET[key]
        ctx['question_list'] = json.dumps(ctx['question_list'])
        print(ctx['question_list'])
        return ctx

class Verification(TemplateView):
    template_name = "registration/verification.html"

class ActivateView(TemplateView):
    template_name = "registration/activate.html"

    def get(self, request, uidb64, token, *args, **kwargs):
        # 認証トークンを検証して、
        result = activate_user(uidb64, token)
        # コンテクストのresultにTrue/Falseの結果を渡します。
        return super().get(request, result=result, **kwargs)


class Login(LoginView):
    template_name = "registration/login.html"
    form_class = LoginForm

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        print(ctx)
        ctx['question_list'] = {}
        for key in dict(self.request.GET).keys():
            ctx['question_list'][key] = self.request.GET[key]
        ctx['question_list'] = json.dumps(ctx['question_list'])
        print(ctx['question_list'])
        return ctx

def AfterLogin(request):
    return redirect('/')

def ProfileView(request):
    return redirect('/')
