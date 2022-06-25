from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils.html import escape
from django.utils import timezone
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse
from urllib.parse import urlencode
from django.http import HttpResponse

from .models import Construct, Question, Answer, User, AnswerDetail, StressQOL

import json
import pandas as pd


def defore_index(request):
    q_a = {}
    if 'question_stress_1' in dict(request.GET).keys():
        for key in dict(request.GET).keys():
            q_a[key] = request.GET[key]
        save_answer(q_a, request.user)
        print(q_a)
        return redirect('check:stress_qol_result_latest')
    else:
        return redirect('check:index')

def save_answer(params, user):
    stress = Construct.objects.get(construct_slug='stress')
    qol = Construct.objects.get(construct_slug='qol')
    stress_qol = StressQOL(
        user=user, created_at=timezone.localtime(timezone.now()))
    stress_qol.save()
    answer_stress = Answer(user=user, construct=stress,
                           created_at=timezone.localtime(timezone.now()), stress_qol=stress_qol)
    answer_stress.save()
    answer_qol = Answer(user=user, construct=qol,
                        created_at=timezone.localtime(timezone.now()), stress_qol=stress_qol)
    answer_qol.save()
    sum_stress = 0
    cnt_stress = 0
    sum_qol = 0
    cnt_qol = 0

    for key in dict(params).keys():
        if (not key.startswith("question_")):
            continue
        question_order = int(key.split("_")[2])
        answer_value = str(int(params[key]) - 1)
        if key.split("_")[1] == 'stress':
            answer = answer_stress
            slug = 'stress'
            sum_stress += int(answer_value)
            cnt_stress += 1
        else:
            answer = answer_qol
            slug = 'qol'
            sum_qol += int(answer_value)
            cnt_qol += 1
        answer_detail = AnswerDetail(answer=answer, question=Question.objects.get(
            construct_id__construct_slug=slug, question_order=question_order), answer_value=answer_value)  # 作成した回答に回答の詳細を紐づける
        answer_detail.save()

    avg_stress = sum_stress / cnt_stress  # 純粋な回答平均
    avg_qol = sum_qol / cnt_qol  # 純粋な回答平均
    point_stress = int(25*avg_stress)
    point_qol = int(25*avg_qol)
    answer_stress.avg = point_stress
    answer_stress.save()  # 回答平均をAnswerに保存、回答平均とは今回のチェックの総合点
    answer_qol.avg = point_qol
    answer_qol.save()  # 回答平均をAnswerに保存、回答平均とは今回のチェックの総合点

class IndexView(generic.ListView):
    template_name = 'check/index.html'
    context_object_name = 'construct_list'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query_set = Question.objects.filter(
            Q(construct_id__construct_slug='stress') | Q(construct_id__construct_slug='qol')).all()
        ctx['stress_qol_questions'] = query_set
        return ctx

    def get_queryset(self):
        query_set = Construct.objects.order_by('created_at')
        return query_set

    def post(self, request):
        q_a = {}
        for key in dict(request.POST).keys():
            if (not key.startswith("question_")):
                continue
            question_order = int(key.split("_")[2])
            answer_value = str(int(request.POST[key]))
            q_a[key] = answer_value[0]
        #ゲストで回答を送信したとき、回答をパラメータにのせたログインURLにリダイレクト
        if str(request.user) == 'AnonymousUser':
            redirect_url = reverse('accounts:login')
            parameters = urlencode(q_a)
            url = f'{redirect_url}?{parameters}'
            return redirect(url)
        else:
            save_answer(q_a, request.user)
            return redirect('check:stress_qol_result_latest')


class LatestStressSQLResultView(LoginRequiredMixin, generic.TemplateView):
    template_name = "check/stressqol_result.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        user = self.request.user
        
        stress = Construct.objects.get(construct_slug='stress')
        qol = Construct.objects.get(construct_slug='qol')

        gross_answer_stress = Answer.objects.filter(construct=stress)
        gross_answer_qol = Answer.objects.filter(construct=qol)

        user_answer_stress = Answer.objects.filter(
            Q(user=user) & Q(construct=stress))
        user_answer_qol = Answer.objects.filter(
            Q(user=user) & Q(construct=qol))

        user_answer_stress_latest = user_answer_stress.latest('id')
        user_answer_qol_latest = user_answer_qol.latest('id')

        ctx['username'] = user.username
        ctx['answer_stress_id'] = str(user_answer_stress_latest.id)
        ctx['answer_qol_id'] = str(user_answer_qol_latest.id)
        ctx['stress'] = stress.construct_name
        ctx['qol'] = qol.construct_name

        #数値
        ctx['point_stress'] = user_answer_stress_latest.avg
        ctx['point_qol'] = user_answer_qol_latest.avg

        ctx['gross_avg_stress'] = int(gross_answer_stress.aggregate(
            Avg('avg'))['avg__avg'])
        ctx['gross_avg_qol'] = int(gross_answer_qol.aggregate(
            Avg('avg'))['avg__avg'])
        ctx['gross_cnt_stress'] = gross_answer_stress.count()
        ctx['gross_cnt_qol'] = gross_answer_qol.count()

        ctx['rank_stress'] = list(gross_answer_stress.order_by(
            '-avg').values_list('pk', flat=True)).index(user_answer_stress_latest.id)+1
        ctx['rank_qol'] = list(gross_answer_qol.order_by(
            '-avg').values_list('pk', flat=True)).index(user_answer_qol_latest.id)+1

        ctx['criteria_stress'] = stress.criteria_point
        ctx['criteria_qol'] = qol.criteria_point

        #説明文
        def get_statement(construct, point):
            if point < 20:  # 結果に表示する文言を選択
                stetement = construct.result_statement_lowest
            elif point >= 20 and point < 40:
                stetement = construct.result_statement_lower
            elif point >= 40 and point < 60:
                stetement = construct.result_statement_moderate
            elif point >= 60 and point < 80:
                stetement = construct.result_statement_higher
            else:
                stetement = construct.result_statement_highest
        ctx['statement_stress'] = get_statement(stress, ctx['point_stress'])
        ctx['statement_qol'] = get_statement(qol, ctx['point_qol'])

        #線グラフ
        ctx['past_data_values_stress'] = list(
            user_answer_stress.order_by('created_at').values_list('avg', flat=True))
        ctx['past_data_values_qol'] = list(
            user_answer_qol.order_by('created_at').values_list('avg', flat=True))
        ctx['past_data_at_stress'] = list(map(lambda x: json.dumps(x.strftime('%Y-%m-%d %H:%M:%S')).replace(
            '"', ''), list(user_answer_stress.order_by('created_at').values_list('created_at', flat=True))))
        ctx['past_data_at_qol'] = list(map(lambda x: json.dumps(x.strftime('%Y-%m-%d %H:%M:%S')).replace(
            '"', ''), list(user_answer_stress.order_by('created_at').values_list('created_at', flat=True))))

        #バブルチャート用
        #user_answer_stressqol_stress = list(Answer.objects.filter(
        #    Q(user=user) & Q(construct=stress) & Q(stress_qol__isnull=False)).order_by('created_at').values_list('avg', flat=True))
        #user_answer_stressqol_qol = list(Answer.objects.filter(
        #    Q(user=user) & Q(construct=qol) & Q(stress_qol__isnull=False)).order_by('created_at').values_list('avg', flat=True))
        #past_data_stressqol = list(
        #    zip(user_answer_stressqol_stress, user_answer_stressqol_qol))
        #count = collections.Counter(past_data_stressqol)
        #past_data_stressqol = []
        #for k, v in dict(count).items():
        #    past_data_stressqol.append({'x': k[0], 'y': k[1], 'r': v})
        #ctx['past_data_stressqol'] = json.dumps(past_data_stressqol)

        #ヒストグラム
        hist_labels = [str(i) + '-' for i in range(0, 100, 10)]
        bins = [i for i in range(-1, 100, 10)]
        bins[-1] = 100
        cats_stress = list(
            pd.cut(list(gross_answer_stress.values_list('avg', flat=True)), bins, labels=hist_labels))
        cats_qol = list(
            pd.cut(list(gross_answer_qol.values_list('avg', flat=True)), bins, labels=hist_labels))
        hist_thistime_stress = [0] * 10
        hist_thistime_stress[9 if ctx['point_stress'] >= 100 else ctx['point_stress']//10] = 1
        hist_thistime_qol = [0] * 10
        hist_thistime_qol[9 if ctx['point_qol'] >= 100 else ctx['point_qol']//10] = 1
        ctx['hist_stress'] = [cats_stress.count(hist_labels[0]), cats_stress.count(hist_labels[1]), cats_stress.count(hist_labels[2]), cats_stress.count(
            hist_labels[3]), cats_stress.count(hist_labels[4]), cats_stress.count(hist_labels[5]), cats_stress.count(hist_labels[6]), cats_stress.count(hist_labels[7]), cats_stress.count(hist_labels[8]), cats_stress.count(hist_labels[9])]
        ctx['hist_qol'] = [cats_qol.count(hist_labels[0]), cats_qol.count(hist_labels[1]), cats_qol.count(hist_labels[2]), cats_qol.count(
            hist_labels[3]), cats_qol.count(hist_labels[4]), cats_qol.count(hist_labels[5]), cats_qol.count(hist_labels[6]), cats_qol.count(hist_labels[7]), cats_qol.count(hist_labels[8]), cats_qol.count(hist_labels[9])]
        ctx['hist_thistime_stress'] = hist_thistime_stress
        ctx['hist_thistime_qol'] = hist_thistime_qol
        ctx['hist_labels'] = hist_labels

        #ctx['previous_stress_rank'] = ctx['past_data_values_qol'][-2]
        #ctx['previous_qol_rank'] = user_answer_qol.latest('id')
        return ctx


class ConstructIndexView(generic.ListView):
    template_name = 'check/construct_index.html'
    model = Question
    context_object_name = 'question_list'
    
    def get_queryset(self, **kwargs):
        slug = self.kwargs.get('slug')
        query_set = Question.objects.filter(construct_id__construct_slug=slug).all()
        return query_set

    def get_context_data(self, **kwargs):
        slug = self.kwargs.get('slug')
        ctx = super().get_context_data()
        ctx['slug'] = get_object_or_404(Construct, construct_slug=slug)
        return ctx

    def post(self, request, slug):
        user = request.user  # User.objects.get(id=1)
        construct = Construct.objects.get(construct_slug=slug)
        answer = Answer(user=user, construct=construct,
                        created_at=timezone.localtime(timezone.now()))#回答を作成
        answer.save()
        params = {}
        params['username'] = user.username
        params['answer_id'] = str(answer.id)
        params['construct'] = construct.construct_name
        params['answer_details'] = {}
        sum = 0
        cnt = 0
        for key in dict(request.POST).keys():
            if (not key.startswith("question_")): continue
            question_order = int(key.split("question_")[1])
            answer_value = str(int(request.POST[key]) - 1)
            answer_detail = AnswerDetail(answer=answer, question=Question.objects.get(
                construct_id__construct_slug=slug, question_order=question_order), answer_value=answer_value) #作成した回答に回答の詳細を紐づける
            answer_detail.save()
            params['answer_details'][key] = request.POST[key]
            sum += int(answer_value)
            cnt += 1
        avg = sum / cnt #純粋な回答平均
        point = int(25*avg) #maxを100%とした回答平均
        params['point'] = point
        answer.avg = point
        answer.save() #回答平均をAnswerに保存、回答平均とは今回のチェックの総合点
        answers = Answer.objects.filter(
            construct_id__construct_slug=slug)
        params['gross_avg'] = int(answers.aggregate(Avg('avg'))['avg__avg'])  # 全体平均を構成概念に保存
        params['gross_cnt'] = answers.count()  # 回答数
        answer_id = answer.id
        params['rank'] = list(answers.order_by('-avg').values_list('pk', flat=True)).index(answer_id)+1 #全体の中で何番目に大きいか
        constructs = Construct.objects.get(construct_slug=slug)
        params['criteria'] = constructs.criteria_point
        if point < 20: #結果に表示する文言を選択
            stetement = constructs.result_statement_lowest
        elif point >= 20 and point < 40:
            stetement = constructs.result_statement_lower
        elif point >= 40 and point < 60:
            stetement = constructs.result_statement_moderate
        elif point >= 60 and point < 80:
            stetement = constructs.result_statement_higher
        else:
            stetement = constructs.result_statement_highest
        params['statement'] = stetement
        params['past_data_values'] = list(Answer.objects.filter(Q(user=user) & Q(construct=construct)).order_by('created_at').values_list('avg', flat=True))
        params['past_data_at'] = list(map(lambda x: json.dumps(x.strftime('%Y-%m-%d %H:%M:%S')).replace('"', ''), list(Answer.objects.filter(Q(user=user) & Q(construct=construct)).order_by('created_at').values_list('created_at', flat=True))))

        return render(request, 'check/result.html', {'params': params})


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'check/results.html'


