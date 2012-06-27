"""Python interface to GenoLogics LIMS via its REST API.

Usage example: Get some containers.

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

# Get the list of all containers.
containers = lims.get_containers()
print len(containers), 'containers in total'

for state in ['Empty', 'Reagent-Only', 'Discarded', 'Populated']:
    containers = lims.get_containers(state=state)
    print len(containers), state, 'containers'

containers = lims.get_containers(type='96 well plate')
print len(containers)

container = containers[2]
print container, container.occupied_wells

placements = container.get_placements()
for location, artifact in placements.iteritems():
    print location, artifact.name

containertype = container.type
print containertype, containertype.name, containertype.x_dimension, containertype.y_dimension
