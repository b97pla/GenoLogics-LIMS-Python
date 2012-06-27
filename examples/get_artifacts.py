"""Python interface to GenoLogics LIMS via its REST API.

Usage example: Get artifacts and artifact info.

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

# Get the list of all artifacts.
## artifacts = lims.get_artifacts()
## print len(artifacts), 'total artifacts'

## artifacts = lims.get_artifacts(qc_flag='UNKNOWN')
## print len(artifacts), 'QC UNKNOWN artifacts'
## artifacts = lims.get_artifacts(qc_flag='PASSED')
## print len(artifacts), 'QC PASSED artifacts'
## artifacts = lims.get_artifacts(qc_flag='FAILED')
## print len(artifacts), 'QC FAILED artifacts'

## artifacts = lims.get_artifacts(working_flag=True)
## print len(artifacts), 'Working-flag True artifacts'

name = 'GRU54A236'
name = 'jgr33'
artifacts = lims.get_artifacts(sample_name=name)
print len(artifacts), 'Sample name', name, 'artifacts'

artifacts = lims.get_batch(artifacts)
for artifact in artifacts:
    print artifact, artifact.name, artifact.state, artifact.working_flag, artifact.samples

artifacts = lims.get_artifacts(qc_flag='PASSED')
print len(artifacts), 'QC PASSED artifacts'
artifacts = lims.get_batch(artifacts)
for artifact in artifacts:
    print artifact, artifact.name, artifact.state, artifact.working_flag, artifact.samples
