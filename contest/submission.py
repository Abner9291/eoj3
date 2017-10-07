from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404, HttpResponseRedirect, reverse, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.edit import FormView
from django.views.generic import View, TemplateView
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction

from problem.views import StatusList, ProblemSubmissionAPI
from problem.tasks import create_submission, judge_submission_on_problem
from account.permissions import is_volunteer
from .models import Contest, ContestProblem
from .views import BaseContestMixin, time_formatter
from .tasks import judge_submission_on_contest
from utils.permission import is_contest_manager, is_case_download_available
from submission.models import Submission, SubmissionStatus
from submission.views import render_submission
from utils.permission import get_permission_for_submission
from submission.forms import ContestSubmitForm
from dispatcher.tasks import submit_code_for_contest
from utils.language import LANG_CHOICE

import json


class ContestSubmit(BaseContestMixin, TemplateView):
    template_name = 'contest/submit.jinja2'

    def test_func(self):
        return super(ContestSubmit, self).test_func() and self.user.is_authenticated

    def get_context_data(self, **kwargs):
        data = super(ContestSubmit, self).get_context_data(**kwargs)
        data['lang_choices'] = list(filter(lambda k: k[0] in self.contest.supported_language_list, LANG_CHOICE))
        data['default_problem'] = self.request.GET.get('problem', '')
        return data

    def post(self, request, cid):
        try:
            if self.contest.status != 0:
                raise ValueError("Contest is not running.")
            lang = request.POST.get('lang', '')
            if lang not in self.contest.supported_language_list:
                raise ValueError("Invalid language.")
            try:
                problem = self.contest.contestproblem_set.get(identifier=request.POST.get('problem', '')).problem_id
            except ContestProblem.DoesNotExist:
                raise ValueError("Invalid problem.")
            submission = create_submission(problem, self.user, request.POST.get('code', ''), lang,
                                           contest=self.contest)
            contest_participant, _ = self.contest.contestparticipant_set.get_or_create(user=self.user)
            if contest_participant.is_disabled:
                raise ValueError("You have quitted the contest.")
            judge_submission_on_contest(submission)
            return JsonResponse({"url": reverse('contest:submission_api',
                                                kwargs={'cid': self.contest.id, 'sid': submission.id})})
        except Exception as e:
            return HttpResponseBadRequest(str(e).encode())


class ContestSubmissionAPI(BaseContestMixin, View):

    def get(self, request, cid, sid):
        if not request.user.is_authenticated:
            raise PermissionDenied
        submission = get_object_or_404(Submission, contest_id=cid, author=request.user, pk=sid)
        if self.contest.case_public and submission.is_judged and \
                is_case_download_available(self.request.user, submission.problem_id, submission.contest_id):
            submission.allow_case_download = True
        return HttpResponse(
            render_submission(submission, permission=get_permission_for_submission(request.user, submission),
                              hide_problem=True))


class ContestSubmissionView(BaseContestMixin, TemplateView):
    template_name = 'submission.jinja2'

    def get_context_data(self, **kwargs):
        data = super(ContestSubmissionView, self).get_context_data(**kwargs)
        data['submission'] = submission = get_object_or_404(Submission, contest_id=self.kwargs.get('cid'),
                                                                        pk=self.kwargs.get('sid'))
        submission.contest_problem = self.contest.get_contest_problem(submission.problem_id)
        if self.contest.case_public and submission.is_judged and \
                is_case_download_available(self.request.user, submission.problem_id, submission.contest_id):
            submission.allow_case_download = True
        authorized = False
        if self.request.user.is_authenticated:  # Check author or managers (no share)
            if is_contest_manager(self.request.user,
                                  self.contest) or self.request.user == submission.author:
                authorized = True
            if not authorized and self.contest.allow_code_share > 0:  # start to share
                if self.contest.status > 0 and self.contest.allow_code_share >= 2:
                    authorized = True
                if self.request.user.submission_set.filter(problem_id=submission.problem_id,
                                                           status=SubmissionStatus.ACCEPTED).exists() and (
                                self.contest.status > 0 or self.contest.allow_code_share >= 3):
                    authorized = True
        if authorized:
            data['submission_block'] = render_submission(submission,
                                                         permission=get_permission_for_submission(self.request.user, submission),
                                                         show_percent=(self.contest.scoring_method == 'oi'))
        else:
            raise PermissionDenied
        return data


class ContestMyPastSubmissions(BaseContestMixin, TemplateView):
    template_name = 'components/past_submissions.jinja2'

    def get_context_data(self, **kwargs):
        data = super(ContestMyPastSubmissions, self).get_context_data(**kwargs)
        data['submission_list'] = self.contest.submission_set.only("problem_id", "id", "status", "status_private",
                                                                   "status_private", "create_time", "contest_id",
                                                                   "author_id", "author__username",
                                                                   "author__nickname", "author__magic"). \
            filter(author_id=self.request.user.pk)[:20]
        self.contest.add_contest_problem_to_submissions(data['submission_list'])
        data['view_more'] = True
        return data


class ContestStatus(BaseContestMixin, StatusList):
    template_name = 'contest/status.jinja2'
    contest_submission_visible = True

    def get_selected_from(self):
        return self.contest.submission_set.all()

    def reinterpret_problem_identifier(self, value):
        return self.contest.contestproblem_set.get(identifier=value).problem_id

    def get_context_data(self, **kwargs):
        data = super(ContestStatus, self).get_context_data(**kwargs)
        self.contest.add_contest_problem_to_submissions(data['submission_list'])
        return data


class ContestMyStatus(ContestStatus):
    template_name = 'contest/my_status.jinja2'

    def test_func(self):
        return super().test_func() and self.user.is_authenticated

    def get_selected_from(self):
        if not self.user.is_authenticated:
            raise PermissionDenied
        return self.contest.submission_set.filter(author=self.user).all()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(hide_users=True)
        return data


class ContestBalloon(BaseContestMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponse()


def balloon_switch(request, pk):
    if not is_volunteer(request.user):
        raise PermissionDenied("You don't have the access.")
    with transaction.atomic():
        submission = Submission.objects.select_for_update().get(pk=pk)
        submission.addon_info = True
        submission.save(update_fields=['addon_info'])
    return HttpResponse(json.dumps({"result": "success"}))
