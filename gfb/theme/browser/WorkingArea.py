from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from Products.LinguaPlone.browser.selector import TranslatableLanguageSelector

class WorkingArea(BrowserView, TranslatableLanguageSelector):
    """
    Working Area for normal users
    """
    
    template = ViewPageTemplateFile('templates/working_area.pt')

    def __init__(self, context, request, **args):
        super(WorkingArea, self).__init__(context, request)
        self.context = context
        self.tool = getToolByName(context, 'portal_languages', None)
        self.pwt = getToolByName(context, 'portal_workflow')
        portal_tool = getToolByName(context, 'portal_url', None)
        self.portal_url = None
        if portal_tool is not None:
            self.portal_url = portal_tool.getPortalObject().absolute_url()

    def __call__(self):
        return self.template()


    def setup(self):
        pm = getToolByName(self, 'portal_membership')
        pc = getToolByName(self, 'portal_catalog')
        
        try:
            self.userid = pm.getAuthenticatedMember().getUserId()
        except:
            self.userid = pm.getAuthenticatedMember().getUserName()
        f = pm.getMembersFolder()
        path = "/".join( f.getPhysicalPath() ) + '/' + self.userid
        self.RALinks = pc.searchResults(portal_type="RiskAssessmentLink", path=path)
        self.Provider = pc.searchResults(portal_type="Provider", path=path, Language='all')

        hf = pm.getHomeFolder()
        self.home_folder = hf
        self.home_folder_url = hf and hf.absolute_url() or ''
        

    def provider(self):
        return len(self.Provider)>0 and self.Provider[0].getObject() or None

    def providerReviewState(self):
        p = self.provider()
        return p and self.pwt.getInfoFor(p, 'review_state') or ''
        

    def create_provider_url(self):
        if not self.home_folder:
            return ''
        href="%s/createObject?type_name=Provider" % self.home_folder_url
        return href


    def home_url(self):
        return self.home_folder_url

    def myrals(self):
        objs = [x.getObject() for x in self.RALinks]
        return [dict(obj=obj, state=self.pwt.getInfoFor(obj, 'review_state')) for obj in objs]
        
    def provider_ok(self):
        return not not len(self.Provider)    