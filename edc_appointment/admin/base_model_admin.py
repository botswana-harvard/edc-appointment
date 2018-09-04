from django.core.urlresolvers import reverse
from django.contrib import admin
from edc_base.modeladmin.mixins import (
    ModelAdminRedirectMixin, ModelAdminFormInstructionsMixin, ModelAdminFormAutoNumberMixin,
    ModelAdminAuditFieldsMixin)


class BaseModelAdmin(ModelAdminRedirectMixin, ModelAdminFormInstructionsMixin, ModelAdminFormAutoNumberMixin,
                     ModelAdminAuditFieldsMixin, admin.ModelAdmin):

    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'
    querystring_name = 'next'

    def redirect_url(self, request, obj, post_url_continue=None):
        url_name = request.GET.get(self.querystring_name)
        dashboard_type = request.GET.get('dashboard_type')
        dashboard_model = request.GET.get('dashboard_model')
        dashboard_id = request.GET.get('dashboard_id')
        show = request.GET.get('show')
        instruction = request.GET.get('instruction')
        return reverse(url_name, kwargs={
            'dashboard_type': dashboard_type,
            'dashboard_model': dashboard_model,
            'dashboard_id': dashboard_id,
            'show': show,
            'instruction': instruction})