from django.urls import path

from authencations.views import SignUpView, LoginView, CheckRefreshTokenView, LogoutView
from ai_voice.views import VoiceApiView
from subscriptions.views import PackageListView
from faq.views import FAQView

urlpatterns = [
    # authentication   
    path('signup', SignUpView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('check-refresh-token', CheckRefreshTokenView.as_view(), name='check-refresh-token'),
    # ai voice
    path('ai-voice', VoiceApiView.as_view(), name='ai-voice'),
    # subscription
    path('packages', PackageListView.as_view(), name='packages'),
    # faq
    path('faq', FAQView.as_view(), name='faq'),
]