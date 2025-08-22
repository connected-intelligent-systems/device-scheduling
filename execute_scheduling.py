import json
import time
from datetime import timedelta

from problog import get_evaluatable
from problog.program import PrologString

from scheduling.python_functions.problog_functions_io import write_current_scheduling_parameters_as_predicates

abstract_scheduling = PrologString(open("scheduling/interfaces/abstract_scheduling.pl").read())
fine_grained_scheduling = PrologString(open("scheduling/interfaces/fine_grained_scheduling.pl").read())


def execute_scheduling():
    # capture start time
    start_time = time.time()

    write_current_scheduling_parameters_as_predicates("scheduling/io/current_scheduling_parameters.json",
                                              'scheduling/data/current_scheduling_parameters.pl')

    # decide kind of scheduling
    with open("scheduling/io/current_scheduling_parameters.json", 'r') as file:
        parameters = json.load(file)
        file.close()

    if parameters["abstract_scheduling"]:
        problog_code = abstract_scheduling
    else:
        problog_code = fine_grained_scheduling

    scheduling_results = get_evaluatable().create_from(problog_code).evaluate()
    print(scheduling_results)

    # compute computation time
    end_time = time.time()
    computation_time = timedelta(seconds=end_time - start_time)
    print(f"Execution time was {computation_time}.")


