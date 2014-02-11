import datetime, time
from django.shortcuts import render

from django.http import HttpResponseRedirect
from django.contrib import messages
from django.views.generic import View
from django.contrib.auth import login, authenticate, logout
from django.core.urlresolvers import reverse


class LoginView(View):
    fallback_redirect_to = "home"
    template_name = "auth/login_required.html"

    def redirect(self, request):
        if hasattr(request.POST,'next'):
            return HttpResponseRedirect(request.POST['next'])
        else:
            raise Exception("test")
            return HttpResponseRedirect(reverse(self.fallback_redirect_to))

    def get(self, request):
        return render(request,
                      self.template_name,
                      {'login_form_present' : True})

    def post(self, request):
        time.sleep(1)
        user = authenticate(username = request.POST['username'], password = request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                # success
                messages.success(request, "Login successful ! User %s connected at %s" % (user.username, datetime.datetime.now()))
                return self.redirect(request)
            else:
                # disabled account
                messages.error(request, "This account (%s) is disabled." % user.username)
                return self.redirect(request)
        else:
            # invalid login
            time.sleep(1)
            messages.error(request, "Invalid credentials. Please try again.")
            return self.redirect(request)


class LogoutView(View):
    redirect_to = None
    fallback_redirect_to = "home"
    def get(self, request):
        logout(request)
        messages.success(request, "You have been logged out.")

        time.sleep(1)

        if self.redirect_to:
            return HttpResponseRedirect(reverse(self.redirect_to))
        else:
            return HttpResponseRedirect(getattr(request.META,'HTTP_REFERER', reverse(self.fallback_redirect_to)))
