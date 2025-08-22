import json
import os

from problog.extern import problog_export

from scheduling.python_functions.problog_functions_utils import reformat_problog_predicates


def write_schedulable_time_frames_as_predicates(schedulable_time_frames_json, problog_file):
    """
    Write the schedulable time frames of each application included in the schedulable_time_frames_json file
     as predicates into the given problog file.
    :param schedulable_time_frames_json: The filepath to the json file
     containing the schedulable time frames of each application to be used for the next scheduling.
    :param problog_file: The filepath to the problog file to write the schedulable time frames of each application
     as predicates to.
    """

    # read json file
    with open(schedulable_time_frames_json, 'r') as file:
        application_schedulable_times = json.load(file)
        file.close()

    # compute all allowed_times tuples
    weekday_schedule_dict = dict()
    for weekday in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        weekday_schedule_dict[weekday] = []

    for application in application_schedulable_times.keys():
        for weekday in application_schedulable_times[application].keys():
            for time_frame in application_schedulable_times[application][weekday]:
                weekday_schedule_dict[weekday].append((weekday, application, time_frame["start"], time_frame["end"]))

    # write allowed_times tuples in the problog file
    with open(problog_file, 'w') as file:
        lines = ["% Application-specific time frames in which application scheduling is allowed.\n",
                 "\n"]

        for weekday in weekday_schedule_dict.keys():
            for allowed_times_tuple in weekday_schedule_dict[weekday]:
                lines.append("allowed_times_app(" + allowed_times_tuple[0] + ", " + allowed_times_tuple[1] +
                             ", \'" + allowed_times_tuple[2] + "\', " + "\'" + allowed_times_tuple[3] + "\'" + ").\n")

            lines.append("\n")

        file.writelines(lines)

        file.close()


def write_general_scheduling_parameters_as_predicates(scheduling_parameters_json, problog_file):
    """
    Write the general scheduling parameters of each application included in the scheduling_parameters_json file.
    :param scheduling_parameters_json: The filepath to the json file  containing the general parameters
     used for the scheduling.
    :param problog_file: The filepath to the problog file to write the scheduling parameters as predicates to.
    """

    # read json file
    with open(scheduling_parameters_json, 'r') as file:
        general_scheduling_parameters = json.load(file)
        file.close()

    with open(problog_file, 'w') as file:
        lines = ["% Application consumption in Wh between actionable timepoints\n"]

        application_consumptions = general_scheduling_parameters["application_consumptions"]

        for application in application_consumptions.keys():
            lines.append("app_cons(" + application + ", " + str(application_consumptions[application]) + ").\n")

        lines.extend(["\n",
                      "% The time between two actionable timepoints\n",
                      "time_density(\'" + general_scheduling_parameters["scheduling_time_density"] + "\').\n",
                      "\n",
                      "% The time between two abstract timepoints\n",
                      "abstract_time_density(\'" + general_scheduling_parameters["abstract_scheduling_time_density"]+ "\').\n",
                      "\n",
                      "% The time window length for rescheduling applications\n",
                      "rescheduling_time_window(\'" + general_scheduling_parameters["rescheduling_time_window"] + "\').\n",
                      "\n",
                      "% Maximal tolerated costs for the scheduled time frame\n",
                      "cost_threshold(" + str(general_scheduling_parameters["cost_threshold"]) + ")."])

        file.writelines(lines)

        file.close()


def write_current_scheduling_parameters_as_predicates(scheduling_parameters_json, problog_file):
    """
    Write the current scheduling parameters included in the scheduling_parameters_json
     as predicates into the given problog file.
    :param scheduling_parameters_json: The filepath to the json file
     containing the parameters to be used for the next scheduling.
    :param problog_file: The filepath to the problog file to write the scheduling parameters as predicates to.
    """

    # read json file
    with open(scheduling_parameters_json, 'r') as file:
        parameters = json.load(file)
        file.close()

    with open(problog_file, 'w') as file:
        file.writelines([
            "% Forecasted energy production (solar modules, etc.)\n",
            "prod(" + str(parameters["pv-forecast"]) + ").\n",
            "\n",
            "% Forecasted base-load\n",
            "load(" + str(parameters["load-forecast"]) + ").\n",
            "\n",
            "% Forecasted energy costs (costs per kWh)\n",
            "costs(" + str(parameters["energy-price-forecast"]) + ").\n",
            "\n",
            "% Appliances used in the next scheduling\n",
            "appliances_to_schedule(" + str(parameters["devices_to_schedule"]).replace("\'","") + ")."
        ])

        file.close()


@problog_export('+str', '+str', '+list', '+list', '-int')
def write_scheduling_results_to_json(output_file: str,
                                     date: str,
                                     scheduled_appliances: list[str],
                                     scheduled_times: list[str]):
    """
    Writes the scheduling results to the given output file in JSON format.
    :param output_file: The filepath to the output file.
    :param date: The date of the scheduling results.
    :param scheduled_appliances: The scheduled appliances.
    :param scheduled_times: The schedule time frames of each appliance.
    :return: 0 if successful.
    """
    # fill the scheduled applications dictionary for the file
    scheduled_appliances_dict = dict()
    for a in range(len(scheduled_appliances)):
        start_time, end_time = scheduled_times[a].split("-")

        time_frame = dict()
        time_frame["start"] = date + " " + start_time
        time_frame["end"] = date + " " + end_time

        scheduled_appliances_dict[str(scheduled_appliances[a])] = time_frame

    # write scheduling results to results file
    file_name = reformat_problog_predicates([output_file])
    if not os.path.exists(file_name):
        mode = 'x'
    else:
        mode = 'w'

    with open(file_name, mode) as file:
        json.dump(scheduled_appliances_dict, file, indent=4)
        file.close()

    return 0


if __name__ == "__main__":
    # write_scheduling_parameters_as_predicates('../io/current_scheduling_parameters.json',
    #                                           'test.pl')

    # write_schedulable_time_frames_as_predicates('../io/schedulable_time_frames.json',
    #                                             'test.pl')

    write_general_scheduling_parameters_as_predicates(
        '../io/general_scheduling_parameters.json',
        'test.pl'
    )

