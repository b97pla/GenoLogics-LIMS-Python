"""Python interface to GenoLogics LIMS via its REST API.

Usage example: Get labs and lab info.

NOTE: You need to set the BASEURI, USERNAME AND PASSWORD.

Per Kraulis, Science for Life Laboratory, Stockholm, Sweden.
"""

import codecs
from genologics.lims import Lims

# Login parameters for connecting to a LIMS instance.
# NOTE: Modify according to your setup.
from genologics.site_cloud import BASEURI, USERNAME, PASSWORD

# Create the LIMS interface instance, and check the connection and version.
lims = Lims(BASEURI, USERNAME, PASSWORD)
lims.check_version()

# Get the list of all projects.
labs = lims.get_labs(name='SciLifeLab')
print len(labs), 'labs in total'
for lab in labs:
    print lab, lab.name, lab.shipping_address.items()
    for key, value in lab.udf.items():
        if isinstance(value, unicode):
            value = codecs.encode(value, 'UTF-8')
        print ' ', key, '=', value
    udt = lab.udt
    if udt:
        print 'UDT:', udt.udt
        for key, value in udt.items():
            if isinstance(value, unicode):
                value = codecs.encode(value, 'UTF-8')
            print ' ', key, '=', value
