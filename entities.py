"""Python interface to GenoLogics LIMS via its REST API.

Entities and their descriptors for the LIMS interface.

Per Kraulis, Science for Life Laboratory, Stockholm, Sweden.
Copyright (C) 2012 Per Kraulis
"""

import re
import codecs
import urlparse
import datetime
import time
from xml.etree import ElementTree


_NSMAP = dict(
    artgr='http://genologics.com/ri/artifactgroup',
    art='http://genologics.com/ri/artifact',
    cnf='http://genologics.com/ri/configuration',
    con='http://genologics.com/ri/container',
    ctp='http://genologics.com/ri/containertype',
    exc='http://genologics.com/ri/exception',
    file='http://genologics.com/ri/file',
    lab='http://genologics.com/ri/lab',
    perm='http://genologics.com/ri/permissions',
    prc='http://genologics.com/ri/process',
    prj='http://genologics.com/ri/project',
    prop='http://genologics.com/ri/property',
    prx='http://genologics.com/ri/processexecution',
    ptp='http://genologics.com/ri/processtype',
    res='http://genologics.com/ri/researcher',
    rgt='http://genologics.com/ri/reagent',
    ri='http://genologics.com/ri',
    rtp='http://genologics.com/ri/reagenttype',
    smp='http://genologics.com/ri/sample',
    udf='http://genologics.com/ri/userdefined',
    ver='http://genologics.com/ri/version')

for prefix, uri in _NSMAP.iteritems():
    ElementTree._namespace_map[uri] = prefix

_NSPATTERN = re.compile(r'(\{)(.+?)(\})')

def nsmap(tag):
    "Convert from normal XML-ish namespace tag to ElementTree variant."
    parts = tag.split(':')
    if len(parts) != 2:
        raise ValueError("no namespace specifier in tag")
    return "{%s}%s" % (_NSMAP[parts[0]], parts[1])


class BaseDescriptor(object):
    "Abstract base descriptor for an instance attribute."

    def __get__(self, instance, cls):
        raise NotImplementedError


class TagDescriptor(BaseDescriptor):
    """Abstract base descriptor for an instance attribute
    represented by an XML element.
    """

    def __init__(self, tag):
        self.tag = tag


class StringDescriptor(TagDescriptor):
    """An instance attribute containing a string value
    represented by an XML element.
    """

    def __set__(self, instance, value):
        node = instance.root.find(self.tag)
        if node is None:
            raise AttributeError("no element '%s' to set" % self.tag)
        else:
            node.text = value

    def __get__(self, instance, cls):
        instance.get()
        node = instance.root.find(self.tag)
        if node is None:
            return None
        else:
            return node.text


class StringAttributeDescriptor(TagDescriptor):
    """An instance attribute containing a string value
    represented by an XML attribute.
    """

    def __get__(self, instance, cls):
        instance.get()
        return instance.root.attrib[self.tag]


class StringListDescriptor(TagDescriptor):
    """An instance attribute containing a list of strings
    represented by multiple XML elements.
    """

    def __get__(self, instance, cls):
        instance.get()
        result = []
        for node in instance.root.findall(self.tag):
            result.append(node.text)
        return result


class StringDictionaryDescriptor(TagDescriptor):
    """An instance attribute containing a dictionary of string key/values
    represented by a hierarchical XML element.
    """

    def __get__(self, instance, cls):
        instance.get()
        result = dict()
        node = instance.root.find(self.tag)
        if node is not None:
            for node2 in node.getchildren():
                result[node2.tag] = node2.text
        return result


class IntegerDescriptor(StringDescriptor):
    """An instance attribute containing an integer value
    represented by an XMl element.
    """

    def __get__(self, instance, cls):
        instance.get()
        node = instance.root.find(self.tag)
        if node is None:
            return None
        else:
            return int(node.text)


class UdfDictionary(object):
    "Dictionary-like container of UDFs, optionally within a UDT."

    def __init__(self, instance, udt=False):
        self.instance = instance
        self._udt = udt
        self._update_elems()
        self._prepare_lookup()

    def get_udt(self):
        if self._udt == True:
            return None
        else:
            return self._udt

    def set_udt(self, name):
        assert isinstance(name, basestring)
        if not self._udt:
            raise AttributeError('cannot set name for a UDF dictionary')
        self._udt = name
        elem = self.instance.root.find(nsmap('udf:type'))
        assert elem is not None
        elem.set('name', name)

    udt = property(get_udt, set_udt)

    def _update_elems(self):
        self._elems = []
        if self._udt:
            elem = self.instance.root.find(nsmap('udf:type'))
            if elem is not None:
                self._udt = elem.attrib['name']
                self._elems = elem.findall(nsmap('udf:field'))
        else:
            tag = nsmap('udf:field')
            for elem in self.instance.root.getchildren():
                if elem.tag == tag:
                    self._elems.append(elem)

    def _prepare_lookup(self):
        self._lookup = dict()
        for elem in self._elems:
            type = elem.attrib['type'].lower()
            value = elem.text
            if not value:
                value = None
            elif type == 'numeric':
                try:
                    value = int(value)
                except ValueError:
                    value = float(value)
            elif type == 'boolean':
                value = value == 'true'
            elif type == 'date':
                value = datetime.date(*time.strptime(value, "%Y-%m-%d")[:3])
            self._lookup[elem.attrib['name']] = value

    def __getitem__(self, key):
        return self._lookup[key]

    def __setitem__(self, key, value):
        self._lookup[key] = value
        for node in self._elems:
            if node.attrib['name'] != key: continue
            type = node.attrib['type'].lower()
            if value is None:
                pass
            elif type == 'string':
                if not isinstance(value, basestring):
                    raise TypeError('String UDF requires str or unicode value')
            elif type == 'text':
                if not isinstance(value, basestring):
                    raise TypeError('Text UDF requires str or unicode value')
            elif type == 'numeric':
                if not isinstance(value, (int, float)):
                    raise TypeError('Numeric UDF requires int or float value')
                value = str(value)
            elif type == 'boolean':
                if not isinstance(value, bool):
                    raise TypeError('Boolean UDF requires bool value')
                value = value and 'True' or 'False'
            elif type == 'date':
                if not isinstance(value, datetime.date): # Too restrictive?
                    raise TypeError('Date UDF requires datetime.date value')
                value = str(value)
            else:
                raise NotImplemented("UDF type '%s'" % type)
            if not isinstance(value, unicode):
                value = unicode(value, 'UTF-8')
            node.text = value
            break
        else:                           # Create new entry; heuristics for type
            if isinstance(value, basestring):
                type = '\n' in value and 'Text' or 'String'
            elif isinstance(value, (int, float)):
                type = 'Numeric'
            elif isinstance(value, bool):
                type = 'Boolean'
                value = value and 'True' or 'False'
            elif isinstance(value, datetime.date):
                type = 'Date'
                value = str(value)
            else:
                raise NotImplementedError("Cannot handle value of type '%s'"
                                          " for UDF" % type(value))
            if self._udt:
                root = self._instance.root.find(nsmap('udf:type'))
            else:
                root = self._instance.root
            elem = ElementTree.SubElement(root,
                                          nsmap('udf:field'),
                                          type=type,
                                          name=key)
            if not isinstance(value, unicode):
                value = unicode(value, 'UTF-8')
            elem.text = value

    def __delitem__(self, key):
        del self._lookup[key]
        for node in self._elems:
            if node.attrib['name'] == key:
                self._instance.root.remove(node)
                break

    def items(self):
        return self._lookup.items()

    def clear(self):
        for elem in self._elems:
            self.instance.root.remove(elem)
        self._update_elems()


class UdfDictionaryDescriptor(BaseDescriptor):
    """An instance attribute containing a dictionary of UDF values
    represented by multiple XML elements.
    """

    def __get__(self, instance, cls):
        instance.get()
        return UdfDictionary(instance)


class UdtDictionaryDescriptor(UdfDictionaryDescriptor):
    """An instance attribute containing a dictionary of UDF values
    in a UDT represented by multiple XML elements.
    """

    def __get__(self, instance, cls):
        instance.get()
        return UdfDictionary(instance, udt=True)


class PlacementDictionaryDescriptor(TagDescriptor):
    """An instance attribute containing a dictionary of locations
    keys and artifact values represented by multiple XML elements.
    """

    def __get__(self, instance, cls):
        instance.get()
        result = dict()
        for node in instance.root.findall(self.tag):
            value = node.find('value').text
            id = node.attrib['limsid']
            result[value] = instance.lims._get_instance(Artifact, id)
        return result


class ExternalidListDescriptor(BaseDescriptor):

    def __get__(self, instance, cls):
        instance.get()
        result = []
        for node in instance.root.findall(nsmap('ri:externalid')):
            result.append((node.attrib.get('id'), node.attrib.get('uri')))
        return result


class StateDescriptor(BaseDescriptor):
    "An instance attribute for Artifact state extracted from the URI."

    def __get__(self, instance, cls):
        instance.get()
        uri = instance.root.attrib['uri']
        parts = urlparse.urlparse(uri)
        params = urlparse.parse_qs(parts.query)
        try:
            return params['state'][0]
        except (KeyError, IndexError):
            return None

    def __set__(self, instance, value):
        instance.get()
        elem = instance.root
        uri = elem.attrib['uri']
        parts = list(urlparse.urlparse(uri))
        if value is None:
            parts[4] = ''
        else:
            parts[4] = "state=%s" % value
        elem.attrib['uri'] = urlparse.urlunsplit(parts)


class EntityDescriptor(TagDescriptor):
    "An instance attribute referencing another entity instance."

    def __init__(self, tag, klass):
        super(EntityDescriptor, self).__init__(tag)
        self.klass = klass

    def __get__(self, instance, cls):
        instance.get()
        node = instance.root.find(self.tag)
        uri = node.attrib['uri']
        parts = urlparse.urlparse(uri)
        id = parts.path.split('/')[-1]
        return instance.lims._get_instance(self.klass, id)


class EntityListDescriptor(EntityDescriptor):
    """An instance attribute containing a list of entity instances
    represented by multiple XML elements.
    """

    def __get__(self, instance, cls):
        instance.get()
        result = []
        for node in instance.root.findall(self.tag):
            uri = node.attrib['uri']
            parts = urlparse.urlparse(uri)
            id = parts.path.split('/')[-1]
            result.append(instance.lims._get_instance(self.klass, id))
        return result


class DimensionDescriptor(TagDescriptor):
    """An instance attribute containing a dictionary specifying
    the properties of a dimension of a container type.
    """

    def __get__(self, instance, cls):
        instance.get()
        node = instance.root.find(self.tag)
        return dict(is_alpha = node.find('is-alpha').text.lower() == 'true',
                    offset = int(node.find('offset').text),
                    size = int(node.find('size').text))


class LocationDescriptor(TagDescriptor):
    """An instance attribute containing a tuple (container, value)
    specifying the location of an analyte in a container.
    """

    def __get__(self, instance, cls):
        instance.get()
        node = instance.root.find(self.tag)
        id = node.find('container').attrib['limsid']
        container = instance.lims._get_instance(Container, id)
        value = node.find('value').text
        return container, value


class Entity(object):
    "Base class for the entities in the LIMS database."

    _TAG = None
    _URI = None

    def __init__(self, lims, id=None):
        self.lims = lims
        self.id = id
        self.root = None
        if self.id:
            lims.cache[self.key] = self

    def __unicode__(self):
        return self.get_key(self.id)

    def __str__(self):
        return codecs.encode(unicode(self), 'UTF-8')

    @property
    def key(self):
        return self.get_key(self.id)

    @classmethod
    def get_key(cls, id):
        return u"%s %s" % (cls.__name__, id)

    @property
    def uri(self):
        assert self.id
        return self.lims.uri(self._URI, self.id)

    def get(self, force=False):
        if not force and self.root is not None: return
        self.root = self.lims.get(self.uri)
        self.parse()

    def parse(self):
        pass

    def put(self):
        assert self.uri
        data = self.lims.tostring(ElementTree.ElementTree(self.root))
        self.lims.put(self.uri, data)


class Lab(Entity):
    "Lab; container of researchers."

    _URI = 'labs'

    name             = StringDescriptor('name')
    billing_address  = StringDictionaryDescriptor('billing-address')
    shipping_address = StringDictionaryDescriptor('shipping-address')
    udf              = UdfDictionaryDescriptor()
    udt              = UdtDictionaryDescriptor()
    externalids      = ExternalidListDescriptor()
    website          = StringDescriptor('website')


class Researcher(Entity):
    "Person; client scientist or lab personnel. Associated with a lab."

    _URI = 'researchers'

    first_name  = StringDescriptor('first-name')
    last_name   = StringDescriptor('last-name')
    phone       = StringDescriptor('phone')
    fax         = StringDescriptor('fax')
    email       = StringDescriptor('email')
    lab         = EntityDescriptor('lab', Lab)
    udf         = UdfDictionaryDescriptor()
    udt         = UdtDictionaryDescriptor()
    externalids = ExternalidListDescriptor()
    # credentials XXX
    initials   = StringDescriptor('initials')

    @property
    def name(self):
        return u"%s %s" % (self.first_name, self.last_name)


class Project(Entity):
    "Project concerning a number of samples; associated with a researcher."

    _URI = 'projects'

    name          = StringDescriptor('name')
    open_date     = StringDescriptor('open-date')
    close_date    = StringDescriptor('close-date')
    invoice_date  = StringDescriptor('invoice-date')
    researcher    = EntityDescriptor('researcher', Researcher)
    # notes XXX
    udf           = UdfDictionaryDescriptor()
    udt           = UdtDictionaryDescriptor()
    externalids   = ExternalidListDescriptor()
    # files XXX
    # permissions XXX


class Sample(Entity):
    "Customer's sample to be analyzed; associated with a project."

    _URI = 'samples'

    name           = StringDescriptor('name')
    date_received  = StringDescriptor('date-received')
    date_completed = StringDescriptor('date-completed')
    project        = EntityDescriptor('project', Project)
    submitter      = EntityDescriptor('submitter', Researcher)
    # artifact: defined below
    # biosource XXX
    udf            = UdfDictionaryDescriptor()
    udt            = UdtDictionaryDescriptor()
    externalids    = ExternalidListDescriptor()


class Containertype(Entity):
    "Type of container for analyte artifacts."

    _TAG = 'container-type'
    _URI = 'containertypes'

    name              = StringAttributeDescriptor('name')
    calibrant_wells   = StringListDescriptor('calibrant-well')
    unavailable_wells = StringListDescriptor('unavailable-well')
    x_dimension       = DimensionDescriptor('x-dimension')
    y_dimension       = DimensionDescriptor('y-dimension')


class Container(Entity):
    "Container for analyte artifacts."

    _URI = 'containers'

    name           = StringDescriptor('name')
    type           = EntityDescriptor('type', Containertype)
    occupied_wells = IntegerDescriptor('occupied-wells')
    placements     = PlacementDictionaryDescriptor('placement')
    udf            = UdfDictionaryDescriptor()
    udt            = UdtDictionaryDescriptor()
    state          = StringDescriptor('state')

    def get_placements(self):
        """Get the dictionary of locations and artifacts
        using the more efficient batch call."""
        result = self.placements.copy()
        self.lims.get_batch(result.values())
        return result


class Processtype(Entity):

    _TAG = 'process-type'
    _URI = 'processtypes'

    name              = StringAttributeDescriptor('name')
    # XXX


class Process(Entity):
    "Process (instance of Processtype) executed producing ouputs from inputs."

    _URI = 'processes'

    type          = EntityDescriptor('type', Processtype)
    date_run      = StringDescriptor('date-run')
    technician    = EntityDescriptor('technician', Researcher)
    protocol_name = StringDescriptor('protocol-name')
    # input_output_maps XXX
    # instrument XXX
    udf            = UdfDictionaryDescriptor()
    udt            = UdtDictionaryDescriptor()
    # process_parameters XXX


class Artifact(Entity):
    "Any process input or output; analyte or file."

    _URI = 'artifacts'

    state          = StateDescriptor()
    name           = StringDescriptor('name')
    type           = StringDescriptor('type')
    output_type    = StringDescriptor('output-type')
    parent_process = EntityDescriptor('parent-process', Process)
    volume         = StringDescriptor('volume')
    concentration  = StringDescriptor('concentration')
    qc_flag        = StringDescriptor('qc-flag')
    location       = LocationDescriptor('location')
    working_flag   = StringDescriptor('working-flag')
    samples        = EntityListDescriptor('sample', Sample)
    # reagent_labels XXX
    # artifact_flags XXX
    udf              = UdfDictionaryDescriptor()
    # files XXX
    # artifact_groups XXX
    

Sample.artifact = EntityDescriptor('artifact', Artifact)
