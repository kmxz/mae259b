# Utilities for command-line interface (when user runs runBeam.py or runCircle.py directly)
# It will time the execution, backup the code and save results to a JSON file in "data" directory

import datetime
import inspect
import json
from timeit import default_timer as timer


def cliRun(method):
    outputFileName = datetime.datetime.now().strftime('output-%m_%d-%H_%M_%S')
    userDefinedName = input("Specify output file name (or press enter to use %s.json): " % outputFileName)
    if len(userDefinedName.strip()) > 0:
        outputFileName = userDefinedName
    if not outputFileName.endswith('.json'):
        outputFileName += '.json'
    fp = open('data/' + outputFileName, "w")

    code = inspect.getsource(method)
    start_timer = timer()
    result = method()
    time_elapsed = timer() - start_timer
    print("Computation used %f seconds, speed ratio %f" % (time_elapsed, time_elapsed / result['frames'][-1]['time']))

    result['code'] = code
    json.dump(result, fp, separators = (',', ': '))

    fp.close()
    print("Result saved to " + outputFileName)