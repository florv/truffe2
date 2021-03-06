# -*- coding: utf-8 -*-

from django.db import models
from generic.models import GenericModel, GenericStateModel, GenericStateUnitValidable, FalseFK, GenericGroupsValidableModel, GenericGroupsModel, GenericContactableModel, GenericExternalUnitAllowed, GenericDelayValidable, GenericDelayValidableInfo, SearchableModel, ModelUsedAsLine, GenericModelWithLines
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.timezone import localtime
from django.core.urlresolvers import reverse


from rights.utils import UnitEditableModel, UnitExternalEditableModel


class _Room(GenericModel, GenericGroupsModel, UnitEditableModel, GenericDelayValidableInfo, SearchableModel):

    class MetaRightsUnit(UnitEditableModel.MetaRightsUnit):
        access = 'LOGISTIQUE'

    title = models.CharField(_('Titre'), max_length=255)
    description = models.TextField()
    unit = FalseFK('units.models.Unit')

    active = models.BooleanField(_('Actif'), help_text=_(u'Pour désactiver temporairement la posibilité de réserver.'), default=True)

    conditions = models.TextField(_(u'Conditions de réservation'), help_text=_(u'Si tu veux préciser les conditions de réservation pour la salle. Tu peux par exemple mettre un lien vers un contrat.'), blank=True)

    allow_externals = models.BooleanField(_(u'Autoriser les externes'), help_text=_(u'Permet aux externes (pas dans l\'AGEPoly) de réserver la salle.'), default=False)
    conditions_externals = models.TextField(_(u'Conditions de réservation pour les externes'), help_text=_(u'Si tu veux préciser des informations sur la réservation de la salle pour les externes. Remplace le champ \'Conditions\' pour les externe si rempli.'), blank=True)

    allow_calendar = models.BooleanField(_(u'Autoriser tout le monde à voir le calendrier'), help_text=_(u'Permet à tout le monde d\'afficher le calendrier des réservations de la salle'), default=True)
    allow_external_calendar = models.BooleanField(_(u'Autoriser les externes à voir le calendrier'), help_text=_(u'Permet aux externes d\'afficher le calendrier des réservations de la salle. Le calendrier doit être visible.'), default=True)

    class MetaData:
        list_display = [
            ('title', _('Titre')),
            ('active', _('Actif')),
            ('allow_externals', _('Autoriser les externes')),
        ]

        details_display = list_display + [
            ('description', _('Description')),
            ('conditions', _('Conditions')),
            ('conditions_externals', _('Conditions pour les externes')),
            ('max_days', _(u'Nombre maximum de jours de réservation')),
            ('max_days_externals', _(u'Nombre maximum de jours de réservation (externes)')),
            ('minimum_days_before', _(u'Nombre de jours minimum avant réservation')),
            ('minimum_days_before_externals', _(u'Nombre de jours minimum avant réservation (externes)')),
            ('maximum_days_before', _(u'Nombre de jours maximum avant réservation')),
            ('maximum_days_before_externals', _(u'Nombre de jours maximum avant réservation (externes)')),
        ]
        filter_fields = ('title', 'description', 'conditions', 'conditions_externals')

        base_title = _('Salle')
        list_title = _(u'Liste de toutes les salles réservables')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-hospital'

        default_sort = "[1, 'asc']"  # title

        menu_id = 'menu-logistics-room'

        yes_or_no_fields = ['active', 'allow_externals']
        html_fields = ('description', 'conditions', 'conditions_externals')

        has_unit = True

        help_list = _(u"""Les salles sont la liste des salles réservables, gérés par l'unité active.

N'importe quelle unité peut mettre à disposition des salles et est responsable de la modération des réservations.""")

    class MetaEdit:
        html_fields = ('description', 'conditions', 'conditions_externals')

    class MetaSearch(SearchableModel.MetaSearch):

        extra_text = u"room"

        fields = [
            'title',
            'description',
            'conditions',
        ]

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class _RoomReservation(GenericModel, GenericDelayValidable, GenericGroupsValidableModel, GenericGroupsModel, GenericContactableModel, GenericStateUnitValidable, GenericStateModel, GenericExternalUnitAllowed, UnitExternalEditableModel, SearchableModel):

    class MetaRightsUnit(UnitExternalEditableModel.MetaRightsUnit):
        access = 'LOGISTIQUE'
        moderation_access = 'LOGISTIQUE'

    room = FalseFK('logistics.models.Room', verbose_name=_('Salle'))

    title = models.CharField(_('Titre'), max_length=255)

    start_date = models.DateTimeField(_(u'Date de début'))
    end_date = models.DateTimeField(_(u'Date de fin'))

    reason = models.TextField(help_text=_(u'Explique pourquoi tu as besoin (manifestation par ex.)'))
    remarks = models.TextField(_('Remarques'), blank=True, null=True)

    class MetaData:

        list_display_base = [
            ('title', _('Titre')),
            ('get_unit_name', _(u'Nom de l\'unité')),
            ('start_date', _(u'Date début')),
            ('end_date', _('Date fin')),
            ('status', _('Statut')),
        ]

        list_display = [list_display_base[0]] + [('room', _(u'Salle')), ] + list_display_base[1:]
        list_display_related = [list_display_base[0]] + [('get_room_link', _(u'Salle')), ] + list_display_base[1:] + [('get_conflits_list', _(u'Conflits')), ]

        forced_widths = {
            '1': '15%',
            '4': '150px',
            '5': '150px',
            '6': '150px',
        }

        forced_widths_related = {
            '1': '15%',
            '4': '150px',
            '5': '150px',
            '6': '150px',
            '7': '80px',
        }

        details_display = list_display_base + [('get_room_infos', _('Salle')), ('reason', _('Raison')), ('remarks', _('Remarques')), ('get_conflits', _('Conflits'))]
        filter_fields = ('title', 'status', 'room__title')

        base_title = _(u'Réservation de salle')
        list_title = _(u'Liste de toutes les réservations de salles')
        list_related_title = _(u'Liste de toutes les réservations des salles de mon unité')
        calendar_title = _(u'Calendrier de mes réservations de salles')
        calendar_related_title = _(u'Calendrier des réservations des salles de mon unité')
        calendar_specific_title = _(u'Calendrier des réservations de la salle')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-hospital'

        safe_fields = ['get_unit_name', 'get_room_link', 'get_conflits_list']

        default_sort = "[4, 'desc']"  # end_date

        menu_id = 'menu-logistics-room-reservation'
        menu_id_related = 'menu-logistics-room-reservation-related'
        menu_id_calendar = 'menu-logistics-room-reservation-calendar'
        menu_id_calendar_related = 'menu-logistics-room-reservation-calendar-related'
        menu_id_directory = 'menu-logistics-room-reservation-directory'

        has_unit = True

        html_fields = ('get_room_infos', 'get_conflits')
        datetime_fields = ('start_date', 'end_date')

        related_name = _('Salle')

        help_list = _(u"""Les réservation de salles.

Les réservations sont soumises à modération par l'unité liée à la salle.

Tu peux gérer ici la liste de tes réservations pour l'unité active (ou une unité externe).""")

        help_list_related = _(u"""Les réservation des salles de l'unité.

Les réservations sont soumises à modération par l'unité liée à la salle.

Tu peux gérer ici la liste de réservation des salles de l'unité active.""")

        help_calendar_specific = _(u"""Les réservation d'un type de salle particulier.""")

        trans_sort = {'get_unit_name': 'unit__name', 'get_room_link': 'room__title'}
        not_sortable_columns = ['get_conflits_list', ]

    class MetaEdit:
        datetime_fields = ('start_date', 'end_date')

        only_if = {
            'remarks': lambda (obj, user): obj.status == '2_online' and obj.rights_can('VALIDATE', user),
            'room': lambda (obj, user): obj.status == '0_draft',
        }

    class MetaSearch(SearchableModel.MetaSearch):

        extra_text = u""

        fields = [
            'room',
            'title',
            'reason',
            'remarks',
        ]

    class Meta:
        abstract = True

    class MetaState(GenericStateUnitValidable.MetaState):
        unit_field = 'room.unit'
        linked_model = 'logistics.models.Room'

    def __unicode__(self):
        return self.title

    def genericFormExtraClean(self, data, form):
        """Check if select room is available"""

        from django import forms

        if 'room' in form.fields:

            if 'room' not in data or not data['room'].active or data['room'].deleted:
                raise forms.ValidationError(_('Salle non disponible'))

            if not self.unit and not data['room'].allow_externals:
                raise forms.ValidationError(_('Salle non disponible'))

        if 'start_date' in data and 'end_date' in data and data['start_date'] > data['end_date']:
            raise forms.ValidationError(_(u'La date de fin ne peut pas être avant la date de début !'))

    def get_room_infos(self):
        """Affiche les infos sur la salle pour une réservation"""

        tpl = mark_safe('<div style="margin-top: 5px;">%s, %s <span class="label label-info">%s</span></div>' % (escape(self.room.title), _(u'gérée par'), escape(self.room.unit.name),))

        return tpl

    def get_conflits(self):

        liste = self.room.roomreservation_set.exclude(pk=self.pk).exclude(deleted=True).filter(status__in=['1_asking', '2_online'], end_date__gt=self.start_date, start_date__lt=self.end_date)

        if not liste:
            return mark_safe('<span class="txt-color-green"><i class="fa fa-check"></i> %s</span>' % (unicode(_('Pas de conflits !')),))
        else:
            retour = '<span class="txt-color-red"><i class="fa fa-warning"></i> %s</span><ul>' % (unicode(_(u'Il y a d\'autres réservations en même temps !')),)

            for elem in liste:
                retour += u'<li><span class="label label-%s"><i class="%s"></i> %s</span> %s pour l\'unité %s  <span data-toggle="tooltip" data-placement="right" title="Du %s au %s"><i class="fa fa-clock-o"></i> </span></li>' % (elem.status_color(), elem.status_icon(), elem.get_status_display(), elem, elem.get_unit_name(), localtime(elem.start_date), localtime(elem.end_date),)

            retour += '</ul>'

            return retour

    def get_room_link(self):
        return '<a href="%s">%s</a>' % (reverse('logistics.views.room_show', args=(self.room.pk,)), self.room,)

    def get_conflits_list(self):

        liste = self.room.roomreservation_set.exclude(pk=self.pk).exclude(deleted=True).filter(status__in=['1_asking', '2_online'], end_date__gt=self.start_date, start_date__lt=self.end_date)

        if not liste:
            return '<span class="txt-color-green"><i class="fa fa-check"></i></span>'
        else:

            retour = ''

            for elem in liste:
                retour += u'%s, %s, pour %s du %s au %s, ' % (elem, elem.get_status_display(), elem.unit if elem.unit else elem.unit_blank_name, localtime(elem.start_date), localtime(elem.end_date),)

            return '<span class="txt-color-red" title="%s"><i class="fa fa-warning"></i></span><ul>' % (retour[:-2], )


class _Supply(GenericModel, GenericGroupsModel, UnitEditableModel, GenericDelayValidableInfo, SearchableModel):

    class MetaRightsUnit(UnitEditableModel.MetaRightsUnit):
        access = 'LOGISTIQUE'

    title = models.CharField(_('Titre'), max_length=255)
    description = models.TextField()
    unit = FalseFK('units.models.Unit')

    quantity = models.PositiveIntegerField(_(u'Quantité'), help_text=_(u'Le nombre de fois que tu as l\'objet à disposition'), default=1)

    active = models.BooleanField(_('Actif'), help_text=_(u'Pour désactiver temporairement la posibilité de réserver.'), default=True)

    conditions = models.TextField(_(u'Conditions de réservation'), help_text=_(u'Si tu veux préciser les conditions de réservations pour le matériel. Tu peux par exemple mettre un lien vers un contrat.'), blank=True)

    allow_externals = models.BooleanField(_(u'Autoriser les externes'), help_text=_(u'Permet aux externes (pas dans l\'AGEPoly) de réserver le matériel.'), default=False)
    conditions_externals = models.TextField(_(u'Conditions de réservation pour les externes'), help_text=_(u'Si tu veux préciser des informations sur la réservation du matériel pour les externes. Remplace le champ \'Conditions\' pour les externe si rempli.'), blank=True)

    allow_calendar = models.BooleanField(_(u'Autoriser tout le monde à voir le calendrier'), help_text=_(u'Permet à tout le monde d\'afficher le calendrier des réservations du matériel'), default=True)
    allow_external_calendar = models.BooleanField(_(u'Autoriser les externes à voir le calendrier'), help_text=_(u'Permet aux externes d\'afficher le calendrier des réservations du matériel. Le calendrier doit être visible.'), default=True)

    class MetaData:
        list_display = [
            ('title', _('Titre')),
            ('active', _('Actif')),
            ('allow_externals', _('Autoriser les externes')),
        ]

        details_display = list_display + [
            ('quantity', _(u'Quantité')),
            ('description', _('Description')),
            ('conditions', _('Conditions')),
            ('conditions_externals', _('Conditions pour les externes')),
            ('max_days', _(u'Nombre maximum de jours de réservation')),
            ('max_days_externals', _(u'Nombre maximum de jours de réservation (externes)')),
            ('minimum_days_before', _(u'Nombre de jours minimum avant réservation')),
            ('minimum_days_before_externals', _(u'Nombre de jours minimum avant réservation (externes)')),
            ('maximum_days_before', _(u'Nombre de jours maximum avant réservation')),
            ('maximum_days_before_externals', _(u'Nombre de jours maximum avant réservation (externes)')),
        ]
        filter_fields = ('title', 'description', 'conditions', 'conditions_externals')

        base_title = _(u'Matériel')
        list_title = _(u'Liste de tout le matériel réservable')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-umbrella'

        default_sort = "[1, 'asc']"  # title

        menu_id = 'menu-logistics-supply'

        yes_or_no_fields = ['active', 'allow_externals']
        html_fields = ('description', 'conditions', 'conditions_externals')

        has_unit = True

        help_list = _(u"""La liste du matériel réservable, gérés par l'unité active.

N'importe quelle unité peut mettre à disposition du matériel et est responsable de la modération des réservations.""")

    class MetaEdit:
        html_fields = ('description', 'conditions', 'conditions_externals')

    class MetaSearch(SearchableModel.MetaSearch):

        extra_text = u""

        fields = [
            'title',
            'description',
            'conditions',
        ]

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.title


class SupplyReservationLine(ModelUsedAsLine):

    supply_reservation = models.ForeignKey('SupplyReservation', related_name='lines')
    supply = models.ForeignKey('Supply', related_name='reservations')
    quantity = models.IntegerField(_(u'Quantité'), default=1)

    def __unicode__(self):
        try:
            return u'{}{}'.format(u'{} * '.format(self.quantity) if self.quantity > 1 else u'', self.supply or u'')
        except:
            return u'?'


class _SupplyReservation(GenericModel, GenericModelWithLines, GenericDelayValidable, GenericGroupsValidableModel, GenericGroupsModel, GenericContactableModel, GenericStateUnitValidable, GenericStateModel, GenericExternalUnitAllowed, UnitExternalEditableModel, SearchableModel):

    class MetaRightsUnit(UnitExternalEditableModel.MetaRightsUnit):
        access = 'LOGISTIQUE'
        moderation_access = 'LOGISTIQUE'

    title = models.CharField(_('Titre'), max_length=255)

    start_date = models.DateTimeField(_(u'Date de début'))
    end_date = models.DateTimeField(_(u'Date de fin'))

    reason = models.TextField(help_text=_(u'Explique pourquoi tu as besoin (manifestation par ex.)'))
    remarks = models.TextField(_('Remarques'), blank=True, null=True)

    class MetaData:

        list_display_base = [
            ('title', _('Titre')),
            ('get_unit_name', _(u'Nom de l\'unité')),
            ('start_date', _(u'Date début')),
            ('end_date', _('Date fin')),
            ('status', _('Statut')),
        ]

        list_display = [list_display_base[0]] + [('get_supplies', _(u'Matériel')), ] + list_display_base[1:]
        list_display_related = [list_display_base[0]] + [('get_supply_link', _(u'Matériel')), ] + list_display_base[1:] + [('get_conflits_list', _(u'Conflits')), ]

        forced_widths = {
            '1': '15%',
            '4': '150px',
            '5': '150px',
            '6': '150px',
        }

        forced_widths_related = {
            '1': '15%',
            '4': '150px',
            '5': '150px',
            '6': '150px',
            '7': '80px',
        }

        details_display = list_display_base + [('get_supply_infos', _(u'Matériel')), ('reason', _('Raison')), ('remarks', _('Remarques')), ('get_conflits', _('Conflits'))]
        filter_fields = ('title', 'status', 'lines__supply__title')

        base_title = _(u'Réservation de matériel')
        list_title = _(u'Liste de toutes les réservations de matériel')
        list_related_title = _(u'Liste de toutes les réservations du matériel de mon unité')
        calendar_title = _(u'Calendrier de mes réservations de matériel')
        calendar_related_title = _(u'Calendrier des réservations du matériel de mon unité')
        calendar_specific_title = _(u'Calendrier des réservations du matériel')
        base_icon = 'fa fa-list'
        elem_icon = 'fa fa-umbrella'

        safe_fields = ['get_unit_name', 'get_supply_link', 'get_conflits_list']

        default_sort = "[4, 'desc']"  # end_date

        menu_id = 'menu-logistics-supply-reservation'
        menu_id_related = 'menu-logistics-supply-reservation-related'
        menu_id_calendar = 'menu-logistics-supply-reservation-calendar'
        menu_id_calendar_related = 'menu-logistics-supply-reservation-calendar-related'
        menu_id_directory = 'menu-logistics-supply-reservation-directory'

        has_unit = True

        html_fields = ('get_supply_infos', 'get_conflits')
        datetime_fields = ('start_date', 'end_date')

        related_name = _(u'Matériel')

        help_list = _(u"""Les réservation de matériel.

Les réservations sont soumises à modération par l'unité liée au matériel.

Tu peux gérer ici la liste de tes réservations pour l'unité active (ou une unité externe).""")

        help_list_related = _(u"""Les réservation du matériel de l'unité.

Les réservations sont soumises à modération par l'unité liée au matériel.

Tu peux gérer ici la liste de réservation du matériel de l'unité active.""")

        help_calendar_specific = _(u"""Les réservation d'un type de matériel particulier.""")

        trans_sort = {'get_unit_name': 'unit__name', 'get_supply_link': 'lines__supply__title'}
        not_sortable_columns = ['get_conflits_list', 'get_supplies', 'supply']

    class MetaEdit:
        datetime_fields = ('start_date', 'end_date')

        only_if = {
            'remarks': lambda (obj, user): obj.status == '2_online' and obj.rights_can('VALIDATE', user),
            'lines': lambda (obj, user): obj.status == '0_draft',
        }

    class MetaSearch(SearchableModel.MetaSearch):

        extra_text = u""

        fields = [
            'title',
            'reason',
            'remarks',
            'get_linked_object',
        ]

    class Meta:
        abstract = True

    class MetaState(GenericStateUnitValidable.MetaState):
        unit_field = 'hidden_unit'
        filter_unit_field = 'lines.supply.unit'
        linked_model = 'logistics.models.Supply'

    def generic_set_dummy_unit(self, unit):
        self.hidden_unit = unit

    def get_linked_object(self):
        return [r.supply for r in self.lines.all()]

    class MetaLines:

        lines_objects = [
            {
                'title': _(u'Matériel'),
                'class': 'logistics.models.SupplyReservationLine',
                'form': 'logistics.forms2.SupplyReservationLineForm',
                'related_name': 'lines',
                'field': 'supply_reservation',
                'sortable': True,
                'show_list': [
                ]
            },
        ]

    def __init__(self, *args, **kwargs):
        super(_SupplyReservation, self).__init__(*args, **kwargs)

        if self.pk:

            sr = self.lines.first()

            if sr:
                self.hidden_unit = sr.supply.unit

    def __unicode__(self):
        return self.title

    def genericFormExtraCleanWithLines(self, data, form, lines):
        """Check if selected supplies are available"""
        from django import forms

        if not lines:
            return

        supply_in_list = []
        supply_unit = None

        for supply_form in lines[0]['forms']:

            data = supply_form['form'].cleaned_data

            if 'supply' not in data or not data['supply'].active or data['supply'].deleted:
                raise forms.ValidationError(_(u'Matériel non disponible'))

            if not self.unit and not data['supply'].allow_externals:
                raise forms.ValidationError(_(u'Matériel non disponible ({}), il est réservé aux commissions. Est-ce que tu es bien en train de faire la réservation depuis la bonne unité?'.format(data['supply'])))

            if data['quantity'] < 1:
                raise forms.ValidationError(_(u'La quantité pour le matériel {} doit être positive et non nulle'.format(data['supply'])))
            if data['quantity'] > data['supply'].quantity:
                raise forms.ValidationError(_(u'La quantité pour le matériel {} doit être inférieure à {}'.format(data['supply'], data['supply'].quantity)))

            if data['supply'] in supply_in_list:
                raise forms.ValidationError(_(u'Le matériel {} est présent plusieurs fois dans la liste'.format(data['supply'])))
            else:
                supply_in_list.append(data['supply'])

            if not supply_unit:
                supply_unit = data['supply'].unit
            elif data['supply'].unit != supply_unit:
                raise forms.ValidationError(_(u'Le matériel {} appartient à l\'unité {} alors que d\'autres éléments appartiennent à l\'unité {}. Il faut faire plusieurs réservations si le matériel appartient à des unités différentes.'.format(data['supply'], data['supply'].unit, supply_unit)))

        if not supply_unit:
            raise forms.ValidationError(_(u'Il faut réserver du matériel !'))

    def genericFormExtraClean(self, data, form):

        from django import forms

        if 'start_date' in data and 'end_date' in data and data['start_date'] > data['end_date']:
            raise forms.ValidationError(_(u'La date de fin ne peut pas être avant la date de début !'))

    def get_supply_link(self):
        line_link_list = '<ul class="supply-items">'

        for line in self.lines.order_by('order'):
            line_link_list += '<li><span>'
            line_link_list += u'<a href="{}">{}{}</a>'.format(reverse('logistics.views.supply_show', args=(line.supply.pk,)), u'{} * '.format(line.quantity), line.supply)
            line_link_list += '</span></li>'

        line_link_list += '</ul>'
        return u'{}'.format(line_link_list)

    def get_supplies(self):
        return u' '.join([u'{}{}'.format(u'{} * '.format(line.quantity) if line.quantity > 1 else '', line.supply.title) for line in self.lines.order_by('order')])

    def get_supply_infos(self):
        """Affiche les infos sur le matériel pour une réserversation"""

        matos = ""

        for line in self.lines.order_by('order'):
            unit = escape(line.supply.unit.name)
            matos = u"{}{}{}{}".format(matos, u", " if matos else u"", u"{} * ".format(line.quantity) if line.quantity > 1 else u"", escape(line.supply.title))

        tpl = mark_safe(u'<div style="margin-top: 5px;">{}, {} <span class="label label-info">{}</span></div>'.format(matos, _(u'géré par'), unit))

        return tpl

    def get_conflits(self):

        from logistics.models import SupplyReservation

        liste_reservation = SupplyReservation.objects.exclude(pk=self.pk).exclude(deleted=True).filter(status__in=['1_asking', '2_online'], end_date__gt=self.start_date, start_date__lt=self.end_date)

        conflicts = []

        for other_reservation in liste_reservation:
            for supplyline in other_reservation.lines.all():
                try:
                    myline = self.lines.get(supply=supplyline.supply)

                    if myline.quantity + supplyline.quantity > supplyline.supply.quantity:
                        conflicts.append((other_reservation, supplyline.supply))
                except:
                    pass

        if not conflicts:
            return mark_safe('<span class="txt-color-green"><i class="fa fa-check"></i> {}</span>'.format(unicode(_('Pas de conflits !'))))

        retour = u'<span class="txt-color-red"><i class="fa fa-warning"></i> {}</span><ul>'.format(unicode(_(u'Il y a d\'autres réservations en même temps !')))

        for other_reservation, supply in conflicts:
            retour += u'<li><span class="label label-{}"><i class="{}"></i> {}</span> {} pour l\'unité {}, pas assez de "{}" <span data-toggle="tooltip" data-placement="right" title="Du {} au {}"><i class="fa fa-clock-o"></i> </span></li>'.format(other_reservation.status_color(), other_reservation.status_icon(), other_reservation.get_status_display(), other_reservation, other_reservation.get_unit_name(), supply, localtime(other_reservation.start_date), localtime(other_reservation.end_date))

        retour += '</ul>'

        return retour

    def get_conflits_list(self):
        from logistics.models import SupplyReservation

        liste_reservation = SupplyReservation.objects.exclude(pk=self.pk).exclude(deleted=True).filter(status__in=['1_asking', '2_online'], end_date__gt=self.start_date, start_date__lt=self.end_date)

        conflicts = []

        for other_reservation in liste_reservation:
            for supplyline in other_reservation.lines.all():
                try:
                    myline = self.lines.get(supply=supplyline.supply)

                    if myline.quantity + supplyline.quantity > supplyline.supply.quantity:
                        conflicts.append((other_reservation, supplyline.supply))
                except:
                    pass

        if not conflicts:
            return '<span class="txt-color-green"><i class="fa fa-check"></i></span>'

        retour = u''

        for other_reservation, supply in conflicts:
            retour += u'{}, {}, pour {}, pas assez de {} du {} au {}, '.format(other_reservation, other_reservation.get_status_display(), other_reservation.unit if other_reservation.unit else other_reservation.unit_blank_name, supply, localtime(other_reservation.start_date), localtime(other_reservation.end_date),)

        return u'<span class="txt-color-red" title="{}"><i class="fa fa-warning"></i></span><ul>'.format(retour[:-2])
