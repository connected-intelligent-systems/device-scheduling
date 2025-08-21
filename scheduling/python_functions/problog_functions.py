import os
import re
from typing import overload

from problog.extern import problog_export
import numpy as np
import itertools as it

from scheduling.python_functions.problog_functions_utils import reformat_problog_predicates


# TODO extend to multiple activations
@problog_export('+list', '+int', '-list')
def get_device_activation_permutations(device_activation_times, number_of_timepoints):
    """
    Returns the permutations of the device activation for all possible timepoints.
    :param device_activation_times: A list with the number of consecutive timepoints of activation for each device.
    :param number_of_timepoints: The number of timepoints to permutate the device activation for.
    :return: The permutations of device activation timepoints for all possible timepoints.
    """
    device_activation_permutations = []
    timepoint_matrix_shape = (number_of_timepoints, number_of_timepoints)
    for device_activation_time in device_activation_times:
        # get quadratic matrix with timepoints
        activation_permutations = np.zeros(shape=timepoint_matrix_shape, dtype=int)
        # add diagonals for each consecutive device activation timepoint
        for i in range(device_activation_time):
            activation_permutations += np.eye(*timepoint_matrix_shape, k=i, dtype=int)
        # transform array to list
        activation_permutations = activation_permutations.tolist()
        # remove permutations without full device execution
        if device_activation_time > 1:
            del activation_permutations[-(device_activation_time - 1):]
        # add device timepoint permutations to result
        device_activation_permutations += [activation_permutations]

    return device_activation_permutations


@problog_export('+list', '+int', '+list', '+list', '-list')
def get_device_activation_permutations_scheduling_period(device_activation_times,
                                                         number_of_timepoints,
                                                         start_points,
                                                         end_points):
    """
    Returns the permutations of the device activation for all possible timepoints in the scheduling periods.
    :param start_points: The time point at which to start permutation for each device.
    :param end_points: The time point at which to end permutation for each device.
    :param device_activation_times: A list with the number of consecutive timepoints of activation for each device.
    :param number_of_timepoints: The number of timepoints to permutate the device activation for.
    :return: The permutations of device activation timepoints for all possible timepoints.
    """
    device_activation_permutations = []
    for device_index in range(len(device_activation_times)):
        if start_points[device_index] == -1:
            # if device cannot be scheduled in time_frame, add null schedule for that device
            device_activation_permutations += [[[0] * number_of_timepoints]]
        else:

            schedule_matrix_shape = (end_points[device_index] - start_points[device_index] + 1,
                                     end_points[device_index] - start_points[device_index] + 1)

            # get quadratic matrix with possible schedule time points
            activation_permutations = np.zeros(shape=schedule_matrix_shape, dtype=int)
            # add diagonals for each consecutive device activation timepoint
            for i in range(device_activation_times[device_index]):
                activation_permutations += np.eye(*schedule_matrix_shape, k=i, dtype=int)

            # remove permutations without full device execution
            if device_activation_times[device_index] > 1:
                activation_permutations = np.delete(activation_permutations,
                                                    slice(-(device_activation_times[device_index] - 1),
                                                          device_activation_times[device_index] + 1),
                                                    0)

            # append the amount of time points before the start_point and after the end_point to the matrix
            before_start_matrix = np.zeros(shape=(activation_permutations.shape[0], start_points[device_index]),
                                           dtype=int)
            after_end_matrix = np.zeros(shape=(activation_permutations.shape[0],
                                               number_of_timepoints - end_points[device_index] - 1), dtype=int)

            activation_permutations = np.concatenate((before_start_matrix,
                                                      activation_permutations,
                                                      after_end_matrix),
                                                     axis=1)

            # transform array to list
            activation_permutations = activation_permutations.tolist()
            # add device timepoint permutations to result
            device_activation_permutations += [activation_permutations]

    return device_activation_permutations


@problog_export('+list', '-list')
def get_activation_tuples(activation_possibilities):
    """
    Returns the cartesian product for all device activation possibilities.
    :param activation_possibilities: The activation possibilities given as list with
      activation possibilities for each device.
    :return: The cartesian product for all device activation possibilities as a list of tuples.
    """
    tuple_list = list(it.product(*tuple(activation_possibilities[p] for p in range(len(activation_possibilities)))))
    return [list(t) for t in tuple_list]


@problog_export('+str', '+str', '+list', '-int')
def save_list_elements_as_predicates(file, pred_name, prob_list):
    file_name, pred = reformat_problog_predicates([file, pred_name])

    if not os.path.exists(file_name):
        mode = 'x'
    else:
        mode = 'w'

    with open(file_name, mode) as f:
        for element in prob_list:
            f.writelines([pred + "(" + str(element) + ").\n"])
        f.close()
    return 0


@problog_export('+str', '+str', '+list', '+list', '-int')
def save_app_schedules_as_predicates(file, pred_name, app_list, schedule_list):
    file_name, pred = reformat_problog_predicates([file, pred_name])

    if not os.path.exists(file_name):
        mode = 'x'
    else:
        mode = 'w'

    with open(file_name, mode) as f:
        for i in range(len(app_list)):
            for schedule in schedule_list[i]:
                f.writelines([pred + "(" + str(app_list[i]) + ", " + str(schedule) + ").\n"])

        f.close()
    return 0


@problog_export('+str', '+str', '+list', '+list', '+list', '-int')
def save_weekday_dependent_app_schedules_as_predicates(file, pred_name, app_list, weekdays, weekday_schedules_list):
    file_name, pred = reformat_problog_predicates([file, pred_name])

    if not os.path.exists(file_name):
        mode = 'x'
    else:
        mode = 'w'

    # weekday = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    with open(file_name, mode) as f:
        for w in range(len(weekdays)):
            schedule_list = weekday_schedules_list[w]
            for i in range(len(app_list)):
                if len(schedule_list[i]) > 0:
                    # only write to file if at least one possible schedule exists
                    if type(schedule_list[i][0]) == list:
                        for schedule in schedule_list[i]:
                            f.writelines([pred + "(" + str(weekdays[w]) + ", " + str(app_list[i]) + ", " + str(
                                schedule) + ").\n"])
                    else:
                        f.writelines([pred + "(" + str(weekdays[w]) + ", " + str(app_list[i]) + ", " + str(
                            schedule_list[i]) + ").\n"])
        f.close()
    return 0


@problog_export('+str', '+list', '+list', '+list', '+list', '-int')
def switch_weekday_dependent_app_schedules(file,
                                           app_list,
                                           weekdays,
                                           weekday_schedules_list,
                                           weekday_schedule_time_density):

    file_name = reformat_problog_predicates([file])

    if not os.path.exists(file_name):
        save_weekday_dependent_app_schedules_as_predicates(file,
                                                           "planned_schedule",
                                                           app_list,
                                                           weekdays,
                                                           weekday_schedules_list)

        predicates = [["planned_schedule_density" for i in range(app_list)] for j in range(weekdays)]

        save_predicates_in_file(file,
                                True,
                                predicates,
                                weekday_schedule_time_density)

    else:
        for w in range(len(weekdays)):
            schedule_list = weekday_schedules_list[w]
            with open(file_name, "r") as f:
                predicates = f.readlines()

            for a in range(len(app_list)):
                for p in range(len(predicates)):
                    # replace schedule and time density with new ones
                    if re.search(str(weekdays[w]) + ", " + str(app_list[a]) + ", \[", predicates[p]) is not None:
                        predicates[p] = ("planned_schedule(" + str(weekdays[w]) + ", "
                                         + str(app_list[a]) + ", " + str(weekday_schedules_list[w][a]) + ").\n")

                    elif re.search(str(weekdays[w]) + ", " + str(app_list[a]), predicates[p]) is not None:
                        predicates[p] = ("planned_schedule_density(" + str(weekdays[w]) + ", " + str(app_list[a]) + ", "
                                         + str(weekday_schedule_time_density[w][a][2]) + ").\n")

            with open(file_name, "w") as f:
                f.writelines(predicates)

            f.close()

    return 0


@problog_export('+str', '+int', '+list', '+list', '-int')
def save_predicates_in_file(file, append_to_file, pred_names, predicate_parameters):
    """
    Saves the list of given predicates to a file.
    :param file: The file to write the predicates to.
    :param append_to_file: Whether the predicates should be appended to the file.
    :param pred_names: The names of the predicates to save to the file.
    :param predicate_parameters: The parameters of the predicates.
    """
    append_to_file = bool(append_to_file)

    # cleans the problog parameters
    file_name = reformat_problog_predicates([file])
    pred_names = [str(pred_name) for pred_name in pred_names]
    predicate_names = reformat_problog_predicates(pred_names)

    # clean_parameters = []
    # for pred_parameter_list in predicate_parameters:
    #     str_parameters = [str(predicate_parameter) for predicate_parameter in pred_parameter_list]
    #     clean_parameters.append(list(reformat_problog_predicates(str_parameters)))

    # choose the file writing mode
    if append_to_file:
        mode = 'a'
    else:
        if not os.path.exists(file_name):
            mode = 'x'
        else:
            mode = 'w'

    # write into file
    with open(file_name, mode) as f:
        for i in range(len(predicate_names)):
            predicate = predicate_names[i] + "("

            # write predicate parameters to file
            # for j in range(len(clean_parameters[i])):
            #     predicate += str(clean_parameters[i][j])
            #     if j != len(clean_parameters[i]) - 1:
            #         predicate += ", "

            for j in range(len(predicate_parameters[i])):
                predicate += str(predicate_parameters[i][j])
                if j != len(predicate_parameters[i]) - 1:
                    predicate += ", "

            predicate += ").\n"
            # write predicate to file
            f.writelines([predicate])
        f.close()

    return 0


if __name__ == '__main__':
    device_permutations = get_device_activation_permutations([1, 2, 3], 5)
    print(device_permutations)
    device_permutations_start_stop = get_device_activation_permutations_scheduling_period(
        [1, 2, 3],
        5,
        [1, 0, 2],
        [3, 2, 4]
    )
    print(device_permutations_start_stop)
    # print(get_activation_tuples(device_permutations))
