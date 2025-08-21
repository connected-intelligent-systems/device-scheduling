import json

from flask import request, app, Flask

from execute_scheduling import execute_scheduling
from set_general_scheduling_parameters import set_general_scheduling_parameters

app = Flask(__name__)


@app.route('/run_scheduling', methods=['POST'])
def run_scheduling():
    # get current scheduling parameters
    input = request.get_json()

    with open("scheduling/io/current_scheduling_parameters.json", "w") as input_file:
        json.dump(input, input_file, indent=4)
        input_file.close()

    execute_scheduling()

    with open("scheduling/io/scheduling_results.json", "r") as output_file:
        output = json.load(output_file)
        output_file.close()

    return output


@app.route('/import_scheduling_parameters', methods=['POST'])
def import_scheduling_parameters():
    # get general scheduling parameters and split into schedulable application time frames and other parameters
    input = request.get_json()

    with open("scheduling/io/schedulable_time_frames.json", "w") as input_file:
        json.dump(input["schedulable_time_frames"], input_file, indent=4)
        input_file.close()

    with open("scheduling/io/general_scheduling_parameters.json", "w") as input_file:
        json.dump(input["general_scheduling_parameters"], input_file, indent=4)
        input_file.close()

    set_general_scheduling_parameters()
    return "Successful"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=True)