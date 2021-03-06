# -*- coding: utf-8 -*-

# Python's Libraries
from __future__ import unicode_literals

# Django's Libraries
from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic.base import View
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView
# from django.views.generic import ListView
from django.urls import reverse_lazy

# Own's Libraries
from security.mixins import GroupLoginRequiredMixin

from .business import VoucherRequisitionBusiness as VoucherBusiness
from .business import BenefitRequisitionBusiness as BenefitBusiness
from .models import VoucherRequisition
from .models import BenefitRequisition
from .forms import VoucherRequisitionAddForm
from .forms import VoucherRequisitionEditForm
from .forms import BenefitRequisitionAddForm
from .forms import BenefitRequisitionEditForm


class VoucherListPending(GroupLoginRequiredMixin, View):
    template_name = "voucher/list_for_review.html"
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]

    def get(self, _request):
        query = _request.GET.get('q')
        requisitions = VoucherBusiness.get_Pending(
            query,
            _request.user.profile
        )
        requisitions_paginated = VoucherBusiness.get_Paginated(
            requisitions,
            _request.GET.get('page')
        )
        context = {
            'requisitions': requisitions_paginated
        }
        return render(_request, self.template_name, context)


class VoucherListAll(GroupLoginRequiredMixin, View):
    template_name = "voucher/list_for_review.html"
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]

    def get(self, _request):
        query = _request.GET.get('q')
        requisitions = VoucherBusiness.get_All(
            query,
            _request.user.profile
        )
        requisitions_paginated = VoucherBusiness.get_Paginated(
            requisitions,
            _request.GET.get('page')
        )
        context = {
            'requisitions': requisitions_paginated
        }
        return render(_request, self.template_name, context)


class VoucherListAdminPending(GroupLoginRequiredMixin, View):
    template_name = "voucher/list_for_edit.html"
    group = ['COMPROBANTES_ADM', ]

    def get(self, _request):
        query = _request.GET.get('q')
        requisitions = VoucherBusiness.get_Pending(query)
        requisitions_paginated = VoucherBusiness.get_Paginated(
            requisitions,
            _request.GET.get('page')
        )
        context = {
            'requisitions': requisitions_paginated
        }
        return render(_request, self.template_name, context)


class VoucherListAdminAll(GroupLoginRequiredMixin, View):
    template_name = "voucher/list_for_edit.html"
    group = ['COMPROBANTES_ADM', ]

    def get(self, _request):
        query = _request.GET.get('q')
        requisitions = VoucherBusiness.get_All(query)
        requisitions_paginated = VoucherBusiness.get_Paginated(
            requisitions,
            _request.GET.get('page')
        )
        context = {
            'requisitions': requisitions_paginated
        }
        return render(_request, self.template_name, context)


class VoucherAdd(GroupLoginRequiredMixin, CreateView):
    template_name = "voucher/add.html"
    model = VoucherRequisition
    form_class = VoucherRequisitionAddForm
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]
    success_url = reverse_lazy('payroll:voucher_add_success')

    def form_valid(self, form):
        form.instance.employee = self.request.user.profile
        form.instance.created_by = self.request.user.profile
        form.instance.updated_by = self.request.user.profile
        response = super(VoucherAdd, self).form_valid(form)

        if response.status_code == 302:
            self.request.user.email_user(
                "Esta chido",
                "Ejemplo de mensaje"
            )

        return response


class VoucherAddSuccess(GroupLoginRequiredMixin, TemplateView):
    template_name = "voucher/add_success.html"
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]


class VoucherCancel(GroupLoginRequiredMixin, View):
    template_name = "voucher/cancel.html"
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]

    def get(self, _request, _pk):
        req = get_object_or_404(VoucherRequisition, pk=_pk)
        context = {
            'req': req
        }
        return render(_request, self.template_name, context)

    def post(self, _request, _pk):
        req = get_object_or_404(VoucherRequisition, pk=_pk)
        req.updated_by = _request.user.profile
        req.status = "can"
        req.save()
        return redirect(reverse('payroll:voucher_list_all'))


class VoucherView(GroupLoginRequiredMixin, DetailView):
    model = VoucherRequisition
    template_name = "voucher/view.html"
    group = ['COMPROBANTES_ADM', 'COMPROBANTES_USR', ]
    context_object_name = "rq"

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['object'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        context.update(kwargs)
        return super(VoucherView, self).get_context_data(**context)


class VoucherEdit(GroupLoginRequiredMixin, UpdateView):
    model = VoucherRequisition
    template_name = "voucher/edit.html"
    group = ['COMPROBANTES_ADM', ]
    form_class = VoucherRequisitionEditForm
    success_url = reverse_lazy('payroll:voucher_list_admin_pending')

    def form_valid(self, form):
        form.instance.updated_by = self.request.user.profile
        return super(VoucherEdit, self).form_valid(form)

    # def get_context_data(self, **kwargs):
    #     context = {}
    #     if self.object:
    #         context['object'] = self.object
    #         context_object_name = self.get_context_object_name(self.object)
    #         if context_object_name:
    #             context[context_object_name] = self.object
    #
    #
    #     context.update(kwargs)
    #     return super(VoucherEdit, self).get_context_data(**context)


class BenefitList(GroupLoginRequiredMixin, View):
    template_name = "benefit_list.html"
    group = ['PRESTACIONES_ADM', 'PRESTACIONES_USR', ]

    def get(self, _request, status):
        query = _request.GET.get('q')
        if status=='pending':
            requisitions = BenefitBusiness.get_Pendings(query, _request.user.profile)
        else:
            requisitions = BenefitBusiness.get_All(query, _request.user.profile)

        requisitions_paginated = BenefitBusiness.get_Paginated(requisitions,_request.GET.get('page'))

        context = {
            'status' : status,
            'requisitions': requisitions_paginated
        }

        return render(_request, self.template_name, context)

class BenefitListAdmin(GroupLoginRequiredMixin, View):
    template_name = "benefit_list_admin.html"
    group = ['PRESTACIONES_ADM', ]

    def get(self, _request, status):
        query = _request.GET.get('q')
        if status=='pending':
            requisitions = BenefitBusiness.get_Pendings(query)
        else:
            requisitions = BenefitBusiness.get_All(query)

        requisitions_paginated = BenefitBusiness.get_Paginated(requisitions,_request.GET.get('page'))

        context = {
            'status' : status,
            'requisitions': requisitions_paginated
        }

        return render(_request, self.template_name, context)

class BenefitAdd(CreateView):
    template_name = "benefit_add.html"
    model = BenefitRequisition
    form_class = BenefitRequisitionAddForm
    success_url = reverse_lazy('payroll:benefit_add_success')

    def form_valid(self, form):
        form.instance.employee = self.request.user.profile
        form.instance.created_by = self.request.user.profile
        form.instance.updated_by = self.request.user.profile
        response = super(BenefitAdd, self).form_valid(form)

        if response.status_code == 302:
            self.request.user.email_user(
                "Esta chido",
                "Ejemplo de mensaje"
            ) #TODO: INTEGRAR EMAIL DE NUEVA SOLICITUD
        return response


class BenefitAddSuccess(View):
    template_name = "benefit_add_success.html"

    def get(self, _request):
        return render(_request, self.template_name, {})


class BenefitEdit(View):
    template_name = "benefit_edit.html"
    group = ['PRESTACIONES_ADM', 'PRESTACIONES_USR', ]

    def get(self, request, pk):
        benefit = get_object_or_404(BenefitRequisition, pk=pk)
        is_admin_form = (request.user.groups.filter(
            name='PRESTACIONES_ADM').exists() or request.user.is_superuser) and benefit.created_by.user != request.user
        is_cancelled = benefit.status == 'can'
        form = BenefitRequisitionEditForm(instance=benefit, is_admin_form=is_admin_form, is_cancelled=is_cancelled)
        context = {
            'rq': benefit,
            'form': form
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        benefit = get_object_or_404(BenefitRequisition, pk=pk)
        form = BenefitRequisitionEditForm(data=request.POST, instance=benefit)

        if form.is_valid():
            form.save()
            request.user.email_user(
                "Esta chido",
                "Ejemplo de mensaje"
            )  # TODO: INTEGRAR MENSAJE DE EMAIL DE ACTUALIZACION
            return redirect('payroll:benefit_list_all')
        else:
            return redirect(reverse('payroll:benefit_edit'), pk=pk)


class BenefitCancel(GroupLoginRequiredMixin, View):
    template_name = "benefit_cancel.html"
    group = ['PRESTACIONES_ADM', 'PRESTACIONES_USR', ]

    def get(self, _request, pk):
        req = get_object_or_404(BenefitRequisition, pk=pk)
        context = {
            'req': req
        }
        return render(_request, self.template_name, context)

    def post(self, _request, pk):
        req = get_object_or_404(BenefitRequisition, pk=pk)
        req.updated_by = _request.user.profile
        req.status = "can"
        req.save()
        _request.user.email_user(
            "Esta chido",
            "Ejemplo de mensaje"
        ) # TODO: INTEGRAR MENSAJE DE EMAIL DE CANCELACION
        return redirect(reverse('payroll:benefit_list_all'))
