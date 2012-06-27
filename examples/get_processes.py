"""Python interface to GenoLogics LIMS via its REST API.

Usage example: Get some processes.

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

# Get the list of all processes.
processes = lims.get_processes()
print len(processes), 'processes in total'

process = processes[0]

print process, process.type, process.type.name
for process in lims.get_processes(type=process.type.name):
    print process

name = '1a. Fragment DNA (TruSeq DNA) 3.0'
print name
for process in lims.get_processes(type=name):
    print process
