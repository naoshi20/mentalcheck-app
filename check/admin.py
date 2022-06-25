from django.contrib import admin

# Register your models here.

from .models import StressQOL, User, Construct, Question, Answer, AnswerDetail

admin.site.register(User)
admin.site.register(Construct)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(AnswerDetail)
admin.site.register(StressQOL)