"""Python interface to GenoLogics LIMS via its REST API.

Example usage: Set the name and a UDF of a sample.

NOTE: You need to set the BASEURI, USERNAME AND PASSWORD.

Per Kraulis, Science for Life Laboratory, Stockholm, Sweden.
"""

from genologics.lims import Lims

# Login parameters for connecting to a LIMS instance.
# NOTE: Modify according to your setup.
from genologics.site_cloud import BASEURI, USERNAME, PASSWORD

# Create the LIMS interface instance, and check the connection and version.
lims = Lims(BASEURI, USERNAME, PASSWORD)
lims.check_version()

# Get the sample with the given LIMS identifier, and output its current name.
sample = lims.get_sample('JGR58A21')
print sample, sample.name

# Set the value of one of the UDFs
sample.udf['Emmas field 2'] = 8
for key, value in sample.udf.items():
    print ' ', key, '=', value

sample.put()
print 'Updated sample', sample
