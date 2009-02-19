from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase, PersonalBarViewlet, PathBarViewlet, GlobalSectionsViewlet, SearchBoxViewlet
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from webcouturier.dropdownmenu.browser.dropdown import DropdownMenuViewlet
from plone.app.portlets.portlets.navigation import Assignment

# Overwrite PersonalBarViewlet
class PersonalBarViewletGFB(PersonalBarViewlet):
    render = ViewPageTemplateFile('personal_bar_gfb.pt')


class EditHelp(ViewletBase):
    render = ViewPageTemplateFile('editing_help.pt')
    
class SiteTitleViewlet(ViewletBase):
    render = ViewPageTemplateFile('templates/site_title.pt')
    
    
class PathBarViewletGFB(PathBarViewlet):
    render = ViewPageTemplateFile('templates/path_bar.pt')

class GlobalSectionsViewletGFB(DropdownMenuViewlet, GlobalSectionsViewlet, SearchBoxViewlet):
    render = ViewPageTemplateFile('templates/sections.pt')

    def update(self):
        # from viewletbase                
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        self.site_url = self.portal_state.portal_url()

        # from dropdownmenu
        super(DropdownMenuViewlet, self).update()
        self.properties = getToolByName(self.context, 'portal_properties').navtree_properties
        self.data = Assignment()


        # from globalsections
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        actions = context_state.actions()
        portal_tabs_view = getMultiAdapter((self.context, self.request),
                                           name='portal_tabs_view')
        self.portal_tabs = portal_tabs_view.topLevelTabs(actions=actions)

        selectedTabs = self.context.restrictedTraverse('selectedTabs')
        self.selected_tabs = selectedTabs('index_html',
                                          self.context,
                                          self.portal_tabs)
        self.selected_portal_tab = self.selected_tabs['portal']


        # from searchbox
        props = getToolByName(self.context, 'portal_properties')
        livesearch = props.site_properties.getProperty('enable_livesearch', False)
        if livesearch:
            self.search_input_id = "searchGadget"
        else:
            self.search_input_id = ""

        folder = context_state.folder()
        self.folder_path = '/'.join(folder.getPhysicalPath())
        
class FooterActions(common.ViewletBase):
    
    _template = ViewPageTemplateFile('templates/footer_actions.pt')
    
    
    
    def _footer_render_details_cachekey(fun, self):
        """
        Generates a key based on:
    
        * Current URL
        * Negotiated language
        * Anonymous user flag
        
        """
        context = aq_inner(self.context)
    
        anonymous = getToolByName(context, 'portal_membership').isAnonymousUser()
    
        key= "".join((
            '/'.join(aq_inner(self.context).getPhysicalPath()),
            get_language(aq_inner(self.context), self.request),
            str(anonymous),
            ))
        return key    
    
    
    @ram.cache(_footer_render_details_cachekey) 
    def render(self):
        return xhtml_compress(self._template())

    def update(self):
        context_state = getMultiAdapter((self.context, self.request),
                                        name=u'plone_context_state')
        portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')    
                                            
        self.portal = portal_state.portal() 
        self.site_url = portal_state.portal_url()                                   
                                        
        self.portal_actionicons = aq_base(getToolByName(self.context, 'portal_actionicons'))
                                                
        self.footer_actions = context_state.actions().get('footer_actions', None)        
        
        plone_utils = getToolByName(self.context, 'plone_utils')
        self.getIconFor = plone_utils.getIconFor

    def icon(self, action):
        return self.getIconFor('plone', action['id'], None)        
        


#class SearchBoxViewletGFB(SearchBoxViewlet):
#    render = ViewPageTemplateFile('templates/searchbox.pt')
