# -*- coding: utf-8 -*-
from zope.interface import implements
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode, isDefaultPage
from Products.ZCatalog.interfaces import ICatalogBrain
from Products.Five import BrowserView
from gfb.theme.browser.interfaces import IGFB, IHomeFolder
from slc.linkcollection.interfaces import ILinkList
from zope.component import getMultiAdapter
import Acquisition


class GFB(BrowserView):
    implements(IGFB)

    def cropHTMLText(self, text, length, ellipsis=u'...'):
        """ first strip html, then crop """
        context = Acquisition.aq_inner(self.context)
        portal_transforms = getToolByName(context, 'portal_transforms')
        if isinstance(text, unicode):
            text = text.encode('utf-8')
        try:
            text = portal_transforms.convert('html_to_text', text).getData()
            text = text.decode('utf-8')
        except:
            return text
        return context.restrictedTraverse('@@plone').cropText(
            text, length, ellipsis)

    def mail_wf_change(self, state_change, **kwargs):
        """Sends an email about a workflow change to someone."""
        context = self.context
        host = getToolByName(context, 'MailHost')

        portal = getToolByName(context, 'portal_url').getPortalObject()

        send_from_address = portal.getProperty('email_from_address')
        send_to_address = portal.portal_properties.site_properties.getProperty(
            'document_reviewer_address', send_from_address)

        obj = state_change.object
        user = obj.portal_membership.getAuthenticatedMember()
        title = safe_unicode(obj.Title())
        username = safe_unicode(user.getProperty('fullname'))
        folder_title = self.get_container_of_original(obj, manual=True)

        subject = u'GFB: Artikel "{0}" aus Rubrik "{1}" von Nutzer "{2}" zur ' \
            u'Veröffentlichung eingereicht'.format(title, folder_title, username)
        message = (
            u'''Der Artikel "%(title)s" aus Rubrik "%(rubrik)s" wurde von '''
            u'''Nutzer "%(name)s" zur Veröffentlichung eingereicht.'''
            u'''\n\nDie Adresse lautet: %(url)s''' % dict(
                title=title,
                rubrik=folder_title,
                name=username,
                url=safe_unicode(obj.absolute_url())))

        encoding = portal.getProperty('email_charset')
        msg_type = kwargs.get('msg_type', 'text/plain')
        if 'envelope_from' in kwargs:
            envelope_from = kwargs['envelope_from']
        else:
            envelope_from = send_from_address

        host.send(
            message, mto=send_to_address, mfrom=envelope_from,
            subject=subject, msg_type=msg_type, charset=encoding
        )

    def show_submit_action(self, obj):
        """ whether to show the WF tab 'Submit' """
        pwt = getToolByName(obj, 'portal_workflow')
        if pwt.getInfoFor(obj, 'review_state', '') != 'private':
            return False
        iterate_control = getMultiAdapter(
            (obj, self.request), name='iterate_control')
        if not iterate_control.cancel_allowed():
            return False
        if 'edit' in self.request.get('PATH_INFO', '').split('/')[-1]:
            return False
        diff_view = getMultiAdapter(
            (obj, self.request), name='iterate_diff')
        diffs = diff_view.diffs()
        if diffs.same:
            return False
        return True

    def show_retract_action(self, obj):
        """ whether to show the WF tab 'Retract' """
        pwt = getToolByName(obj, 'portal_workflow')
        if pwt.getInfoFor(obj, 'review_state', '') != 'pending':
            return False
        iterate_control = getMultiAdapter(
            (obj, self.request), name='iterate_control')
        if not iterate_control.cancel_allowed():
            return False
        if 'edit' in self.request.get('PATH_INFO', '').split('/')[-1]:
            return False
        diff_view = getMultiAdapter(
            (obj, self.request), name='iterate_diff')
        diffs = diff_view.diffs()
        if diffs.same:
            return False
        return True

    def show_checkout_action(self, obj):
        """ whether to show the action Tab 'Create Working Copy'"""
        iterate_control = getMultiAdapter(
            (obj, self.request), name='iterate_control')
        if iterate_control.checkout_allowed():
            if isDefaultPage(obj, self.request):
                urls = ILinkList(self.context).urls
                if not urls:
                    return True
            else:
                return True
        return False

    def show_cancel_checkout_action(self, obj):
        """ whether to show the action Tab 'Cancel Checkout'"""
        iterate_control = getMultiAdapter(
            (obj, self.request), name='iterate_control')
        if not iterate_control.cancel_allowed():
            return False
        if 'edit' in self.request.get('PATH_INFO', '').split('/')[-1]:
            return False
        diff_view = getMultiAdapter((obj, self.request), name='iterate_diff')
        diffs = diff_view.diffs()
        if diffs.same:
            return False
        return True

    def get_container_of_original(self, obj, manual=False):
        """ If the obj is a working copy, return the container of the
        original"""
        if IHomeFolder.providedBy(self.context) or manual:
            if ICatalogBrain.providedBy(obj):
                obj = obj.getObject()
            iterate_control = getMultiAdapter(
                (obj, self.request), name='iterate_control')
            original = iterate_control.get_original(obj)
            if original:
                return safe_unicode(Acquisition.aq_parent(original).Title())
        return ""
