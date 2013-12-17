from django.contrib import messages

from django.contrib.auth.models import Permission
from django.db.models.deletion import Collector

from django.views.generic.edit import UpdateView, CreateView, DeleteView

from .mixins import AuthMixin, ModelInfoMixin, RedirectMixin

class CreateView(AuthMixin, ModelInfoMixin, RedirectMixin, CreateView):
    def get_template_names(self):
        names = super(CreateView, self).get_template_names()
        names.append("%s/object_create.html" % self.model._meta.app_label)
        names.append("%s/object_form.html" % self.model._meta.app_label)
        return names

    def form_valid(self, form):
        response = super(CreateView, self).form_valid(form)
        messages.success(self.request, "Created object %s (of type %s, of id %s) in the database." % (self.object, self.object.__class__.__name__, self.object.id))
        return response

class UpdateView(AuthMixin, ModelInfoMixin, RedirectMixin, UpdateView):
    def get_template_names(self):
        names = super(UpdateView, self).get_template_names()
        names.append("%s/object_update.html" % self.model._meta.app_label)
        names.append("%s/object_form.html" % self.model._meta.app_label)
        return names

    def form_valid(self, form):
        response = super(UpdateView, self).form_valid(form)
        messages.info(self.request, "Updated object %s (of type %s, of id %s)." % (self.object, self.object.__class__.__name__, self.object.id))
        return response

class DeleteView(AuthMixin, ModelInfoMixin, RedirectMixin, DeleteView):
    collector_limit = 50
    def get_template_names(self):
        names = super(DeleteView, self).get_template_names()
        names.append("%s/object_delete.html" % self.model._meta.app_label)
        return names
    def redirect_fallback(self):
        url = self.object.__class__.get_list_url()
        assert url
        return url
    def get_context_data(self, *args, **kwargs):
        context = super(DeleteView, self).get_context_data(*args, **kwargs)

        collector = Collector(using='default')
        collector.collect([self.object,])
        
        related = collector.instances_with_model()
        context['related'] = []
        context['related_not_shown'] = 0

        i = 0
        for model, instance in related:
            if i < self.collector_limit:
                context['related'].append((model, instance))
            else:
                context['related_not_shown'] += 1
            i += 1
        
        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        copy = self.object
        messages.warning(request, "Deleted object %s (of type %s, of id %s) from the database." % (copy, copy.__class__.__name__, copy.id))
        return super(DeleteView, self).delete(request, *args, **kwargs)
