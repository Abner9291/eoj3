import json

from django.db import transaction
from django.db.models import Q
from django.shortcuts import HttpResponse, redirect
from django.urls import reverse
from django.views.generic import UpdateView
from django.views.generic import View
from django.views.generic.list import ListView
from rest_framework.response import Response
from rest_framework.views import APIView
from tagging.models import Tag

from backstage.problem.forms import SkillEditForm
from problem.models import Problem, Skill
from ..base_views import BaseBackstageMixin


class ProblemList(BaseBackstageMixin, ListView):
    template_name = 'backstage/problem/problem.jinja2'
    paginate_by = 250
    context_object_name = 'problem_list'

    def get_queryset(self):
        queryset = Problem.objects
        kw = self.request.GET.get('keyword')
        if kw:
            q = Q(title__icontains=kw) | Q(alias=kw)
            if kw.isdigit():
                q |= Q(pk=kw)
            queryset = queryset.filter(q)
        return queryset.order_by("-update_time").all()


class ProblemVisibleSwitch(BaseBackstageMixin, View):
    def post(self, request, pk):
        with transaction.atomic():
            problem = Problem.objects.select_for_update().get(pk=pk)
            problem.visible = True if not problem.visible else False
            problem.save(update_fields=["visible"])
        return HttpResponse(json.dumps({'result': 'success'}))


class ProblemTagList(BaseBackstageMixin, ListView):
    template_name = 'backstage/problem/tags.jinja2'
    queryset = Tag.objects.all()
    context_object_name = 'tag_list'


class ProblemTagCreate(BaseBackstageMixin, APIView):
    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        Tag.objects.create(name=name)
        return Response()


class ProblemTagEdit(BaseBackstageMixin, APIView):
    def post(self, request, *args, **kwargs):
        pk, name = request.POST['pk'], request.POST['name']
        tag = Tag.objects.get(pk=pk)
        tag.name = name
        tag.save(update_fields=["name"])
        return Response()


class ProblemArchiveList(BaseBackstageMixin, ListView):
    template_name = 'backstage/problem/skill.jinja2'
    queryset = Skill.objects.all()
    context_object_name = 'skill_list'


class ProblemArchiveCreate(BaseBackstageMixin, APIView):
    def post(self, request, *args, **kwargs):
        name = request.POST['name']
        Skill.objects.create(name=name)
        return Response()


class ProblemArchiveEdit(BaseBackstageMixin, UpdateView):
    form_class = SkillEditForm
    template_name = 'backstage/problem/skill_edit.jinja2'
    queryset = Skill.objects.all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        return data

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.problem_list = ','.join(form.cleaned_data['problem_list'])
        instance.parent_id = form.cleaned_data['parent']
        instance.save()
        return redirect(reverse('backstage:archive'))
