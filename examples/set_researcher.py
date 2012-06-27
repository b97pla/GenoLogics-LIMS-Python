"""Python interface to GenoLogics LIMS via its REST API.

Example usage: Set an externalid for a researcher.

XXX Don't understand how this works? The URI was set, but only in parts,
and it couldn't be retrieved at the /v1/external/perka address?

NOTE: You need to set the BASEURI, USERNAME AND PASSWORD.

Per Kraulis, Science for Life Laboratory, Stockholm, Sweden.
"""

from xml.etree import ElementTree

from genologics.lims import *

# Login parameters for connecting to a LIMS instance.
# NOTE: Modify according to your setup.
from genologics.site_cloud import BASEURI, USERNAME, PASSWORD

# Create the LIMS interface instance, and check the connection and version.
lims = Lims(BASEURI, USERNAME, PASSWORD)
lims.check_version()

researchers = lims.get_researchers(username='pkraulis')
researcher = researchers[0]
print researcher, researcher.name, researcher.externalids

## ElementTree.SubElement(researcher.root,
##                        nsmap('ri:externalid'),
##                        id='perka',
##                        uri='http://gmail.com/')
## researcher.put()
