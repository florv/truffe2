# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render, redirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.http import Http404, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.utils.encoding import smart_str
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import connections
from django.core.paginator import InvalidPage, EmptyPage, Paginator, PageNotAnInteger
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now
from django.db.models import Q

import json


def ecrans(request):
    """View to display the ecran page"""

    return render(request, 'communication/ecrans.html', {})


def random_slide(request):
    """Return the URL to a random slide"""

    from communication.models import AgepSlide

    slide = AgepSlide.objects.filter(status='2_online').exclude(deleted=True).filter(Q(start_date=None) | Q(start_date__lt=now())).filter(Q(end_date=None) | Q(end_date__gt=now())).order_by('?').all()[0]

    return HttpResponse(slide.picture.url)


def website_news(request):
    """Return data to display on website"""

    from communication.models import WebsiteNews

    retour = []

    for news in WebsiteNews.objects.filter(status='2_online').exclude(deleted=True).filter(Q(start_date=None) | Q(start_date__lt=now())).filter(Q(end_date=None) | Q(end_date__gt=now())).order_by('?'):
        if not request.GET.get('only') or request.GET.get('only')[5:] == str(news.pk):
            retour.append({'id': 'T2V1N{}'.format(news.pk), 'title_fr': news.title, 'title_en': news.title_en or news.title, 'content_fr': news.content, 'content_en': news.content_en or news.content, 'url': news.url, 'unit': news.unit.__unicode__(), 'date': str(news.start_date or news.last_log().when)})

    return HttpResponse(json.dumps(retour), content_type='application/json')


@login_required
def logo_public_list(request):
    from units.models import Unit

    units = Unit.objects.order_by('name')

    # La page va charger en ajax les logos pour chaque unité [car il faut
    # tester les droits sur chaque logo et ça peut être lourd]

    return render(request, 'communication/logo_public_list.html', {'units': units})


@login_required
def logo_public_load(request):
    from units.models import Unit

    unit = get_object_or_404(Unit, pk=request.GET.get('pk'))

    logos = []

    for logo in unit.logo_set.filter(deleted=False):
        if logo.files.count() and logo.rights_can('SHOW', request.user):
            logos.append(logo)

    return render(request, 'communication/logo_public_load.html', {'logos': logos, 'unit': unit})
