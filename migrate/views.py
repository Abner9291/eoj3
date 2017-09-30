import threading
from hashlib import sha1

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.db import transaction
from django.shortcuts import render

from account.models import User
from account.payment import reward_problem_ac
from migrate.forms import MigrateForm
from problem.statistics import get_problem_difficulty
from submission.models import Submission, SubmissionStatus
from .models import OldUser


def verify_old_user(user, pwd):
    return OldUser.objects.filter(username=user,
                                  password='*' + sha1(sha1(pwd.encode()).digest()).hexdigest().upper()).exists()


@login_required
def migrate_view(request):
    if request.method == 'POST':
        form = MigrateForm(request.POST)
        if form.is_valid():
            result = form.cleaned_data

            is_new = result.get('is_new') == 'new'
            username = result.get('username')
            password = result.get('password')
            try:
                if not is_new:
                    if verify_old_user(username, password):
                        username_registered = username + '#old'
                        user = User.objects.get(username=username_registered, is_active=True)
                    else:
                        raise User.DoesNotExist
                else:
                    user = User.objects.get(username=username, is_active=True)
                    if not user.check_password(password) or user.pk == request.user.pk:
                        raise User.DoesNotExist
                MigrationThread(user, request.user).start()
                messages.success(request, 'It could take a few minutes for the changes to take effect.')
            except User.DoesNotExist:
                form.add_error("password", "Invalid username or password")
    else:
        form = MigrateForm()

    return render(request, 'account/migrate.jinja2', {'form': form})


class MigrationThread(threading.Thread):
    def __init__(self, old_user, new_user):
        super().__init__()
        self.old_user = old_user
        self.new_user = new_user

    def run(self):
        with transaction.atomic():
            for submission in Submission.objects.filter(author=self.old_user).order_by("create_time").all():
                if submission.contest_id:
                    # Clone one
                    s = Submission.objects.create(lang=submission.lang,
                                                  code=submission.code,
                                                  problem_id=submission.problem_id,
                                                  author=self.new_user,
                                                  judge_end_time=submission.judge_end_time,
                                                  status=submission.status,
                                                  status_private=submission.status,
                                                  status_percent=submission.status_percent,
                                                  status_detail=submission.status_detail,
                                                  status_time=submission.status_time / 1000)
                    s.create_time = submission.create_time
                    s.save(update_fields=["create_time"])
                else:
                    s = submission
                    s.author = self.new_user
                    s.save(update_fields=["author_id"])

                if s.status == SubmissionStatus.ACCEPTED and not \
                        Submission.objects.filter(author_id=s.author_id, problem_id=s.problem_id, contest__isnull=True,
                                                  status=SubmissionStatus.ACCEPTED, rewarded=True).exists():
                    reward_problem_ac(self.new_user, get_problem_difficulty(s.problem_id), s.problem_id)
                    s.rewarded = True
                    s.save(update_fields=["rewarded"])

            self.old_user.is_active = False
            self.old_user.save(update_fields=['is_active'])

