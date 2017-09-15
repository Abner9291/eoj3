from django.conf.urls import url

import polygon.contest.views as v

urlpatterns = [
    url(r'^list/$', v.ContestList.as_view(), name='contest_list'),
    url(r'^create/$', v.ContestCreate.as_view(), name='contest_create'),
    url(r'^(?P<pk>\d+)/visible/$', v.ContestToggleVisible.as_view(), name='contest_toggle_visible'),
    url(r'^(?P<pk>\d+)/meta/$', v.ContestEdit.as_view(), name='contest_meta'),
    url(r'^(?P<pk>\d+)/access/$', v.ContestAccessManage.as_view(), name='contest_access_manage'),
    url(r'^(?P<pk>\d+)/problems/$', v.ContestProblemManage.as_view(), name='contest_problem_manage'),
    url(r'^(?P<pk>\d+)/problems/create/$', v.ContestProblemCreate.as_view(), name='contest_problem_create'),
    url(r'^(?P<pk>\d+)/problems/reorder/$', v.ContestProblemReorder.as_view(), name='contest_problem_reorder'),
    url(r'^(?P<pk>\d+)/problems/readjust/$', v.ContestProblemChangeWeight.as_view(),
        name='contest_problem_readjust_point'),
    url(r'^(?P<pk>\d+)/problems/delete/$', v.ContestProblemDelete.as_view(), name='contest_problem_delete'),
    url(r'^(?P<pk>\d+)/invitation/$', v.ContestInvitationList.as_view(), name='contest_invitation'),
    url(r'^(?P<pk>\d+)/invitation/create/$', v.ContestInvitationCreate.as_view(),
        name='contest_invitation_create'),
    url(r'^(?P<pk>\d+)/invitation/(?P<invitation_pk>\d+)/delete/$', v.ContestInvitationDelete.as_view(),
        name='contest_invitation_delete'),
    url(r'^(?P<pk>\d+)/invitation/(?P<invitation_pk>\d+)/assign/$', v.ContestInvitationAssign.as_view(),
        name='contest_invitation_assign'),
    url(r'^(?P<pk>\d+)/invitation/download/$', v.ContestInvitationCodeDownload.as_view(),
        name='contest_invitation_download'),
    url(r'^(?P<pk>\d+)/participants/$', v.ContestParticipantList.as_view(), name='contest_participant'),
    url(r'^(?P<pk>\d+)/participants/(?P<participant_pk>\d+)/change/$',
        v.ContestParticipantCommentUpdate.as_view(), name='contest_participant_change'),
    url(r'^(?P<pk>\d+)/participants/(?P<participant_pk>\d+)/star/$', v.ContestParticipantStarToggle.as_view(),
        name='contest_participant_star_toggle'),
    url(r'^(?P<pk>\d+)/participants/create/$', v.ContestParticipantCreate.as_view(),
        name='contest_participant_create'),
    url(r'^(?P<pk>\d+)/participants/download/$', v.ContestParticipantsNoteDownload.as_view(),
        name='contest_participant_download'),
    url(r'^(?P<pk>\d+)/status/$', v.ContestStatusBackend.as_view(), name='contest_status'),
    url(r'^(?P<pk>\d+)/rejudge/$', v.RejudgeContestProblemSubmission.as_view(), name='contest_rejudge'),

]
