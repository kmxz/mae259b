import datetime
import inspect
import json


def cliRun(method):
    outputFileName = datetime.datetime.now().strftime('output-%m_%d-%H_%M_%S')
    userDefinedName = input("Specify output file name (or press enter to use %s.json): " % outputFileName)
    if len(userDefinedName.strip()) > 0:
        outputFileName = userDefinedName
    if not outputFileName.endswith('.json'):
        outputFileName += '.json'
    fp = open('data/' + outputFileName, "w")

    code = inspect.getsource(method)
    result = method()
    result['code'] = code
    json.dump(result, fp, separators = (',', ': '))

    fp.close()
    print("Result saved to " + outputFileName)