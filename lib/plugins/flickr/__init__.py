try:
    import simplejson as json
except:
    import json

from ..base import PhotoList, PhotoSourceUI, SourceWebIcon, Photo
from api import *
from authdialog import *

def info():
    return ['Flickr', FlickrPhotoList, PhotoSourceFlickrUI, PluginFlickrDialog]

class FlickrPhotoList(PhotoList):

    def prepare(self):
        self.photos = []

        factory = FlickrFactoryAPI()
        api_list = factory.api
        if not self.target in api_list:
            print "flickr: %s is invalid target." % self.target
            return

        print factory.api

        #self.api = api_list[self.target]()
        self.api = factory.create(self.target)
        print self.api

        if self.api.nsid_conversion:
            nsid_url = self.api.get_url_for_nsid_lookup(self.argument)
            # print self.target, self.argument

            if nsid_url is None: 
                print "flickr: invalid nsid API url."
                return
            self._get_url_with_twisted(nsid_url, self._nsid_cb)
        else:
            self._get_url_for(self.argument)

    def _nsid_cb(self, data):
        d = json.loads(data)
        argument = self.api.parse_nsid(d)
        if argument is None:
            print "flickr: can not find, ", self.argument
            return

        self._get_url_for(argument)

    def _get_url_for(self, argument):
        url = self.api.get_url(argument) 
        if not url: return

        self._get_url_with_twisted(url)
        self._start_timer()

    def _prepare_cb(self, data):
        d = json.loads(data)

        self.total = len(d['photos']['photo'])
        for s in d['photos']['photo']:
            if s['media'] == 'video': continue

            url = "http://farm%s.static.flickr.com/%s/%s_" % (
                s['farm'], s['server'], s['id'])

            if s.has_key('originalsecret') and False:
                url += "%s_o.%s" % (s['originalsecret'], s['originalformat'])
            else:
                url += "%s.jpg" % s['secret']

            page_url = "http://www.flickr.com/photos/%s/%s" % (
                s['owner'], s['id'])

            data = {'url'        : url,
                    'owner_name' : s['ownername'],
                    'owner'      : s['owner'],
                    'id'         : s['id'],
                    'title'      : s['title'],
                    'page_url'   : page_url,
                    'icon'       : FlickrIcon}

            photo = Photo()
            photo.update(data)
            self.photos.append(photo)

class PhotoSourceFlickrUI(PhotoSourceUI):

    def _build_target_widget(self):
        super(PhotoSourceFlickrUI, self)._build_target_widget()
 
        self._widget_cb(self.target_widget)
        self.target_widget.connect('changed', self._widget_cb)

    def _widget_cb(self, widget):
        target = widget.get_active_text()
        api = FlickrFactoryAPI().create(target)
        state, label = api.set_entry_label()

        self._set_argument_sensitive(label, state)
        tip = api.tooltip() if state else ""
        self._set_argument_tooltip(tip)

        self._set_sensitive_ok_button(self.gui.get_widget('entry1'), not state)

    def _label(self):
        keys = FlickrFactoryAPI().api.keys()
        keys.sort()
        return [ api for api in keys ]

class FlickrIcon(SourceWebIcon):

    def __init__(self):
        self.icon_name = 'flickr.ico'
        self.icon_url = 'http://www.flickr.com/favicon.ico'
