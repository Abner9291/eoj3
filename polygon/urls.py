from django.conf.urls import url, include

import polygon.views as v

urlpatterns = [
    url(r'^$', v.home_view, name='home'),
    url(r'^register/$', v.register_view, name='register'),
    url(r'^rejudge/(?P<sid>\d+)/$', v.RejudgeSubmission.as_view(), name='rejudge_submission'),
    url(r'^problem/', include('polygon.problem.urls')),
    url(r'^contest/', include('polygon.contest.urls')),
    url(r'^runs/$', v.RunsList.as_view(), name='runs'),
    url(r'^runs/message/(?P<pk>\d+)/$', v.RunMessageView.as_view(), name='run_message'),
]
