from lxml import etree

from controls import StringControl, DateControl, TimeControl, DateTimeControl, \
    BooleanControl, AnyURIControl, EmailControl, DecimalControl

from utils import generate_xml_root

XS_TYPE_CONTROL = {
    'xf:string': StringControl,
    'xs:string': StringControl,
    'xf:date': DateControl,
    'xf:time': TimeControl,
    'xf:dateTime': DateTimeControl,
    'xf:boolean': BooleanControl,
    'xf:anyURI': AnyURIControl,
    'xf:email': EmailControl,
    'xf:decimal': DecimalControl
}

class Builder:

    def __init__(self, xml, lang='en'):
        self.xml = xml
        self.lang = lang

        self.xml_root = None
        self.set_xml_root()

        self.binds = {}
        self.set_binds()

        self.controls = {}
        self.set_controls()

    def set_xml_root(self):
        self.xml_root = generate_xml_root(self.xml)

    def set_binds(self):
        q_left = "//*[@id='fr-form-binds']//*[name()='xforms:bind']"
        q_right = "//*[@id='fr-form-binds']//*[name()='xf:bind']"

        query = "%s|%s" % (q_left, q_right)

        for e in self.xml_root.xpath(query):
            self.binds[e.get('id')] = Bind(self, e)

    def set_controls(self):
        query = "//*[name()='fr:body']//*[@bind]"

        for e in self.xml_root.xpath(query):
            bind = self.binds[e.get('bind')]
            self.controls[bind.name] = XS_TYPE_CONTROL[bind.xs_type](self, bind, e)

    # TODO
    def get_structure(self):
        """
        {
            CONTROL_NAME: {
                'xs_type': XS_TYPE,
                'bind': Bind,
                'control': Control,
                'parent': {
                    CONTROL_NAME: {
                        'xs_type': XS_TYPE,
                        'bind': Bind,
                        'control': Control,
                        'parent': None,
                    }
                }
            },
            ...
        }
        """


class Bind:

    def __init__(self, builder, element):
        self.builder = builder
        self.element = element
        self.id = element.get('id')
        self.name = element.get('name')
        self.xs_type = element.get('xs:type', 'xf:string')

        self.parent = None
        self.set_parent()

    def set_parent(self):
        parent_element = self.element.getparent()

        if etree.QName(parent_element).localname == 'bind' and \
           parent_element.get('id') != 'fr-form-binds':
            self.parent = Bind(self.builder, parent_element)
        else:
            self.parent = None
