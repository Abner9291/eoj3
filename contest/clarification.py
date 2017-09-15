from django.core.exceptions import PermissionDenied
from django.shortcuts import reverse, redirect, get_object_or_404
from django.views.generic import View
from notifications.signals import notify

from utils.permission import has_permission_for_contest_management
from .models import ContestClarification
from .views import BaseContestMixin


class ContestClarificationView(BaseContestMixin, View):

    def post(self, request, cid):
        if self.contest.status != 0:
            raise PermissionDenied
        text = request.POST["text"]
        if not text:
            raise PermissionDenied
        if has_permission_for_contest_management(request.user, self.contest):
            ContestClarification.objects.create(contest=self.contest, important=True, author=request.user, answer=text)
            notify.send(sender=request.user,
                        recipient=list(map(lambda x: x.user, self.contest.contestparticipant_set.select_related("user").all())),
                        verb="posted a notification in",
                        level="warning",
                        target=self.contest)
        else:
            ContestClarification.objects.create(contest=self.contest, author=request.user, text=text)
            notify.send(sender=request.user,
                        recipient=self.contest.managers.all(),
                        verb="asked a question in",
                        level="warning",
                        target=self.contest)
        return redirect(reverse("contest:dashboard", kwargs={"cid": self.contest.pk}))


class ContestClarificationAnswer(BaseContestMixin, View):

    def post(self, request, cid, pk):
        if has_permission_for_contest_management(request.user, self.contest):
            clarification = get_object_or_404(ContestClarification, contest_id=cid, pk=pk)
            clarification.answer = request.POST["text"]
            clarification.save(update_fields=["answer"])
            notify.send(sender=request.user,
                        recipient=[clarification.author],
                        verb="answered a question in",
                        level="warning",
                        target=self.contest)
            return redirect(reverse("contest:dashboard", kwargs={"cid": self.contest.pk}))
        raise PermissionDenied
