import json
import os
import time
from datetime import datetime, timedelta

from problog.program import PrologString
from problog.core import ProbLog
from problog import get_evaluatable

p = PrologString(open("scheduling/code/test_suite.pl").read())


def dump_results_to_json(file_path, results):
    s_dict = dict()
    for key in results.keys():
        s_dict[str(key)] = results[key]

    if not os.path.exists(file_path):
        mode = 'x'
    else:
        mode = 'w'
    with open(file_path, mode) as f:
        # j = json.dumps(s_dict, indent=4)
        json.dump(s_dict, f, indent=4)
        # f.write(j)
        f.close()


if __name__ == '__main__':
    start_time = time.time()
    e = get_evaluatable().create_from(p).evaluate()
    # print(e)
    dump_results_to_json("./scheduling_results.json", e)
    print(e)
    end_time = time.time()
    computation_time = timedelta(seconds=end_time - start_time)
    print(f"Execution time was {computation_time}.")
