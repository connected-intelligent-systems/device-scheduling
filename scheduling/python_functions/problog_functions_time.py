import datetime
import os
import re
from operator import index

import pandas as pd
from clearml.utilities.locks.utils import current_time

from numpy.ma.core import remainder
from problog.extern import problog_export, problog_export_nondet, problog_export_raw

from scheduling.python_functions.problog_functions_utils import reformat_problog_predicates


@problog_export('+str', '-int')
def get_stamp(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.timestamp()
    return B


@problog_export('+str', '-int')
def get_weekday(A):
    A = A.replace("'", "")
    dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    B = dt.weekday()
    return B


@problog_export('+str', '-int')
def get_hour(A):
    A = A.replace("'", "")
    try:
        dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.datetime.strptime(A, "%H:%M:%S")
    B = dt.hour
    return B


@problog_export('+str', '-int')
def get_minute(A):
    A = A.replace("'", "")
    try:
        dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.datetime.strptime(A, "%H:%M:%S")
    B = dt.minute
    return B


@problog_export('+str', '-int')
def get_second(A):
    A = A.replace("'", "")
    try:
        dt = datetime.datetime.strptime(A, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        dt = datetime.datetime.strptime(A, "%H:%M:%S")
    B = dt.second
    return B


def convert_time_strings_to_timedelta(time_strings: str| list[str]) ->  datetime.timedelta| tuple[datetime.timedelta]:
    """
    Converts time strings to timedelta objects.
    :param time_strings: The given time strings with format "%H:%M:%S".
    :return: The corresponding timedelta objects.
    """
    if isinstance(time_strings, str):
        time_strings = [time_strings]

    time_deltas = []

    for time_string in time_strings:
        dt = datetime.datetime.strptime(time_string, "%H:%M:%S")
        time_deltas.append(datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second))
    return tuple(time_deltas) if len(time_deltas) > 1 else time_deltas[0]


@problog_export('+str', '-int')
def compute_time_points(time_density: datetime.timedelta| str):
    """
    Computes the total timepoints per day, given a time_density.
    :param time_density: The time between two timepoints.
    :return: The total timepoints per day.
    """

    if type(time_density) is datetime.timedelta:
        time_density_seconds = time_density.total_seconds()
    else:
        time_density = reformat_problog_predicates([time_density])
        time_density_seconds = convert_time_strings_to_timedelta(time_density).total_seconds()

    time_day = 24 * 60 ** 2

    timepoints = int(time_day / time_density_seconds)
    return timepoints


# TODO list of start and end points of one day each (for one device)
@problog_export('+str', '+str', '+str', '-list')
def compute_time_mask(start_time, end_time, time_density):
    start_time, end_time, time_density = reformat_problog_predicates([start_time, end_time, time_density])

    time_day = 24 * 60 ** 2
    start_t = datetime.datetime.strptime(start_time, "%H:%M:%S")
    end_t = datetime.datetime.strptime(end_time, "%H:%M:%S")
    seconds_start = start_t.hour * 60 ** 2 + start_t.minute * 60 + start_t.second
    seconds_end = end_t.hour * 60 ** 2 + end_t.minute * 60 + end_t.second
    dt = datetime.datetime.strptime(time_density, "%H:%M:%S")
    time_density_seconds = datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second).total_seconds()

    timepoints_before_start = int(seconds_start / time_density_seconds)
    if (datetime.datetime.strptime("0:0:0", "%H:%M:%S")
            + timepoints_before_start * datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
            < start_t):
        timepoints_before_start += 1

    time_mask = [0] * timepoints_before_start
    last_time_point_before_start = (datetime.datetime.strptime("0:0:0", "%H:%M:%S")
                                    + (timepoints_before_start-1) * datetime.timedelta(hours=dt.hour,
                                                                                   minutes=dt.minute,
                                                                                   seconds=dt.second))

    time_between_start_and_end = (end_t - last_time_point_before_start)
    time_points_in_between = int(time_between_start_and_end.total_seconds() / time_density_seconds)

    if ((last_time_point_before_start
         + time_points_in_between * datetime.timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second))
            == end_t):
        time_points_in_between -= 1

    time_mask += [1] * time_points_in_between

    last_time_point_in_timeframe = (last_time_point_before_start
                                    + time_points_in_between * datetime.timedelta(hours=dt.hour,
                                                                                  minutes=dt.minute,
                                                                                  seconds=dt.second))

    time_until_end_of_day = (datetime.datetime.strptime("0:0:0", "%H:%M:%S")
                             - last_time_point_in_timeframe + datetime.timedelta(days=1))

    time_points_until_end_of_day = int(time_until_end_of_day.total_seconds() / time_density_seconds)

    if (last_time_point_in_timeframe + time_points_until_end_of_day * datetime.timedelta(hours=dt.hour,
                                                                                         minutes=dt.minute,
                                                                                         seconds=dt.second)
            == datetime.datetime.strptime("0:0:0", "%H:%M:%S") + datetime.timedelta(days=1)):
        time_points_until_end_of_day -= 1

    time_mask += [0] * time_points_until_end_of_day
    assert len(time_mask) == compute_time_points(time_density)
    return time_mask


@problog_export('+list', '+str', '-list')
def compute_scheduled_time_intervals(schedules, time_density):
    """
    Computes the scheduled time intervals for a list of schedules.
    :param schedules: The schedules to compute the time intervals for.
    :param time_density: The time density of the schedules.
    :return: The list of scheduled time intervals.
    """

    time_density = reformat_problog_predicates([time_density])
    time_density_delta = convert_time_strings_to_timedelta(time_density)

    time_frames = []
    for schedule in schedules:
        assert len(schedule) == compute_time_points(time_density)
        start_time = (datetime.datetime.strptime("0:0:0", "%H:%M:%S")
                      + schedule.index(1) * time_density_delta).time()

        end_time = (datetime.datetime.strptime("0:0:0", "%H:%M:%S")
                      + (len(schedule) - schedule[::-1].index(1)) * time_density_delta).time()

        time_frames.append(str(start_time) + '-' + str(end_time))

    return time_frames


def compute_abstraction_factor(original_td: str, abstraction_td: str) -> float:
    """
    Computes the abstraction factor, indicating how many time points of the original time series
     the abstract time series consists of.
    :param original_td: The time density of the original time series.
    :param abstraction_td: The time density of the abstract time series.
    :return: The abstraction factor.
    """
    # clean both original and abstraction time density
    original_td, abstraction_td = reformat_problog_predicates([original_td, abstraction_td])
    original_td, abstraction_td = convert_time_strings_to_timedelta([original_td, abstraction_td])

    # computes the abstraction factor out of how many points of the original time density an time
    # point in the abstraction consists of
    return abstraction_td / original_td


@problog_export('+list', '+list', '+list', '+list', '+list', '+str', '+str', '+str', '-int')
def compute_time_abstraction_parameters(app_names,
                                        app_consumptions,
                                        solar_production,
                                        energy_costs,
                                        base_load,
                                        original_td,
                                        abstraction_td,
                                        filepath):
    """
    Computes the time abstraction parameters used in abstract scheduling and saves them to the file given by filepath.
    :param app_names: The names of the applications.
    :param app_consumptions: The consumptions of applications in original time density.
    :param solar_production: The solar production of applications in original time density.
    :param energy_costs: The energy costs of applications in original time density.
    :param base_load: The base load of the household in original time density.
    :param original_td: The original time density.
    :param abstraction_td: The abstraction time density.
    :param filepath: The filepath to the file, in which to save the time abstraction parameters.
    """

    original_td, abstraction_td, filepath = reformat_problog_predicates([original_td, abstraction_td,filepath])

    abstraction_factor = compute_abstraction_factor(original_td, abstraction_td)

    original_td, abstraction_td = convert_time_strings_to_timedelta([original_td, abstraction_td])

    # compute abstract parameters
    if original_td == abstraction_td:
        abstract_app_consumptions = app_consumptions
        abstract_solar_production = solar_production
        abstract_energy_costs = energy_costs
        abstract_base_load = base_load

    else:
        abstract_app_consumptions = []
        for app_cons in app_consumptions:
            # abstract_app_consumptions.append(compute_abstract_time_series(app_cons,
            #                                                               abstraction_factor))
            abstract_app_consumptions.append(resample_application_consumption(app_cons,
                                                                              original_td,
                                                                              abstraction_td))

        original_data_dict = {"solar_production": solar_production, "energy_costs": energy_costs,
                              "base_load": base_load}
        abstract_data_df = resample_time_series(original_data_dict,
                                                original_td,
                                                abstraction_td)

        abstract_solar_production = list(abstract_data_df["solar_production"])
        abstract_energy_costs = list(abstract_data_df["energy_costs"])
        abstract_base_load = list(abstract_data_df["base_load"])

    assert len(abstract_solar_production) == compute_time_points(abstraction_td)
    assert len(abstract_energy_costs) == compute_time_points(abstraction_td)
    assert len(abstract_base_load) == compute_time_points(abstraction_td)

    # write results to file
    if not os.path.exists(filepath):
        mode = 'x'
    else:
        mode = 'w'

    with open(filepath, mode) as f:
        for i in range(len(abstract_app_consumptions)):
            f.writelines(["abstract_app_cons(" + str(app_names[i]) + ", " + str(abstract_app_consumptions[i]) + ").\n"])

        f.writelines(["abstract_prod(" + str(abstract_solar_production) + ").\n"])
        f.writelines(["abstract_costs(" + str(abstract_energy_costs) + ").\n"])
        f.writelines(["abstract_load(" + str(abstract_base_load) + ").\n"])

        f.close()

    return 0


def resample_application_consumption(original_consumption: list,
                                     original_td: datetime.timedelta,
                                     abstraction_td: datetime.timedelta) -> list:
    """
    Resamples the consumption of an application.
    :param original_consumption: The original consumption of an application.
    :param original_td: The original time density of an application.
    :param abstraction_td: The abstraction time density of an application.
    :return: The resampled consumption of an application in abstract time density.
    """


    start_t = datetime.datetime.strptime("00:00:00", "%H:%M:%S")

    time_series_index = pd.date_range(start = start_t,
                                      # end=start_t+ datetime.timedelta(hours=24),
                                      periods=len(original_consumption),
                                      freq=original_td)

    time_series_dataframe = pd.DataFrame(original_consumption,
                               index=time_series_index,
                               columns=["application_consumption"])

    abstract_data_df = time_series_dataframe.resample(abstraction_td).mean().ffill()
    return list(abstract_data_df["application_consumption"])



@problog_export('+list', '+list','-list')
def compute_abstract_time_series(original_time_series: list, abstraction_factor: float | list[str]) -> list:
    """
    Computes the abstract time series for a given original time series.
    :param original_time_series: The original time series.
    :param abstraction_factor: The factor, how many time points of the original time series are represented
     by the abstract time series.
     When the function is called directly as problog predicate, the abstraction_factor is given as list of
     the original time density and abstraction time density.
    :return: The abstract time series.
    """
    # compute abstraction factor if given in tuple form
    if type(abstraction_factor) == list:
        if len(abstraction_factor) != 2:
            raise ValueError("The abstraction factor must be a list with two elements.")

        abstraction_factor = compute_abstraction_factor(abstraction_factor[0],
                                                        abstraction_factor[1])

    # How much of an abstraction time point is left to fill
    remaining_abstraction_factor = abstraction_factor
    abstract_time_series = [0]
    abstraction_time_point_index = 0

    for i in range(len(original_time_series)):
        original_time_point = original_time_series[i]

        if remaining_abstraction_factor >= 1:
            # add the whole slot to the abstraction slot
            abstract_time_series[abstraction_time_point_index] += original_time_point
            remaining_abstraction_factor -= 1

        elif remaining_abstraction_factor > 0:
            # add the remaining consumption to the current abstraction slot
            original_time_point_diff = remaining_abstraction_factor * original_time_point
            abstract_time_series[abstraction_time_point_index] += original_time_point_diff

            # reset remainder of abstraction slot
            remaining_abstraction_factor = abstraction_factor
            abstraction_time_point_index += 1

            # compute how much and how much percent of the original_time_point remains
            original_time_point_remainder = original_time_point - original_time_point_diff
            original_time_point_remainder_factor = original_time_point_remainder / original_time_point

            # add the remainder of the current original_time_point to abstraction slots
            while original_time_point_remainder > 0:
                if remaining_abstraction_factor >= original_time_point_remainder_factor:
                    # add the whole remaining cons slot to the abstraction slot
                    abstract_time_series.append(original_time_point_remainder)
                    remaining_abstraction_factor -= original_time_point_remainder_factor
                    original_time_point_remainder = 0

                else:
                    # add part of the remaining cons slot as new abstraction slot
                    original_time_point_diff = remaining_abstraction_factor * original_time_point
                    abstract_time_series.append(original_time_point_diff)

                    # compute how much and how much percent of the original time point remains
                    original_time_point_remainder = original_time_point_remainder - original_time_point_diff
                    original_time_point_remainder_factor = original_time_point_remainder / original_time_point

                    # compute new abstraction slot parameters
                    remaining_abstraction_factor = abstraction_factor
                    abstraction_time_point_index += 1

        if remaining_abstraction_factor == 0:
            # prepare for new abstract time point
            abstraction_time_point_index += 1
            remaining_abstraction_factor = abstraction_factor

            if i != len(original_time_series) - 1:
                abstract_time_series.append(0)

    return abstract_time_series


@problog_export('+list', '+str', '+str' ,'-list')
def change_schedule_time_density(schedule_data: list,
                                 original_td: str,
                                 new_td: str):
    """
    Changes the time density of a schedule.
    :param schedule_data: The schedule for which the time density has to be changed.
    :param original_td: The original time density of the schedule.
    :param new_td: The new time density of the schedule.
    :return: The schedule with the new time density.
    """
    original_td, new_td = reformat_problog_predicates([original_td, new_td])
    original_td, new_td = convert_time_strings_to_timedelta([original_td, new_td])

    original_data_dict = {"schedule": schedule_data}

    changed_schedule_df = resample_time_series(original_data_dict,
                                               original_td,
                                               new_td)
    changed_schedule = list(changed_schedule_df["schedule"])

    assert len(changed_schedule) == compute_time_points(new_td)
    return changed_schedule


def compute_time_series_dataframe(time_density: datetime.timedelta | str,
                                  data: dict[str, list],
                                  downsample: bool) -> pd.DataFrame:
    """
    Computes a time series as data frame with the given time density between indices.
    :param time_density: The time between indices of the time series.
    :param data: The data of the data frame.
    :param downsample: Whether to downsample the time density.
    :return: The time series as data frame.
    """
    if not isinstance(time_density, datetime.timedelta):
        time_density_delta = convert_time_strings_to_timedelta(time_density)
    else:
        time_density_delta = time_density

    start_t = datetime.datetime.strptime("00:00:00", "%H:%M:%S")

    time_series_index = pd.date_range(start = start_t,
                                      # end=start_t+ datetime.timedelta(hours=24),
                                      periods=compute_time_points(time_density) + int(downsample),
                                      freq=time_density_delta)

    time_series = pd.DataFrame(data, index=time_series_index, columns=list(data.keys()))
    return time_series


def resample_time_series(time_series_dict: dict[str, list],
                         original_td: datetime.timedelta,
                         new_td: datetime.timedelta) -> pd.DataFrame:
    """
    Resamples time series data.
    :param time_series_dict: The time series data.
    :param original_td: The original time density of the time series.
    :param new_td: The new time density of the time series.
    :return: The resampled time series dataframe.
    """
    downsample = new_td / original_td < 1

    if downsample:
        # add one bonus value for new day to the time series to generate values up to the new day.
        for key in time_series_dict.keys():
            time_series_dict[key].append(0)

    time_series_dataframe = compute_time_series_dataframe(original_td, time_series_dict,
                                                       downsample)
    time_series_types = time_series_dataframe.dtypes
    abstract_data_df = time_series_dataframe.resample(new_td).mean().ffill()

    if downsample:
        # drop bonus value again
        abstract_data_df = abstract_data_df.head(-1)

    int_cast_dict = dict()
    for column in abstract_data_df.columns:
        if time_series_types[column] == int:
            int_cast_dict[column] = int

    return abstract_data_df.astype(int_cast_dict)


# @problog_export('+list', '+str', '+str', '+str', '-list')
# def compute_rescheduling_mask(planned_schedule: list,
#                               reschedule_time_density: str,
#                               relative_rescheduling_start: str,
#                               rescheduling_window: str) -> list:
#     """
#     Computes the rescheduling period for a scheduled application.
#     :param schedule_time_frame: The time frame the application was scheduled for.
#     :param relative_rescheduling_start: The amount of time before the scheduled time frame at which the rescheduling
#      should start.
#     :param rescheduling_window: The time window after the rescheduling start time, in which the rescheduling
#      should take place.
#     :return: The rescheduling period given as list of the start-time and end-time ([start-time, end-time]).
#     """
#     schedule_time_frame = compute_scheduled_time_intervals([planned_schedule], reschedule_time_density)[0]
#     schedule_time_frame, relative_rescheduling_start, rescheduling_window =\
#         reformat_problog_predicates([schedule_time_frame, relative_rescheduling_start, rescheduling_window])
#     schedule_start, schedule_end = schedule_time_frame.split("-")
#
#     (schedule_start_delta,
#      relative_rescheduling_start_delta,
#      rescheduling_window_delta) = convert_time_strings_to_timedelta([schedule_start,
#                                                                      relative_rescheduling_start,
#                                                                      rescheduling_window])
#
#     start_time = schedule_start_delta - relative_rescheduling_start_delta
#     if start_time.days < 0:
#         start_time = datetime.timedelta(hours=0, minutes=0, seconds=0)
#
#     end_time = start_time + rescheduling_window_delta
#     if end_time.days > 0:
#         end_time = datetime.timedelta(hours=23, minutes=59, seconds=59)
#
#     return compute_time_mask(str(start_time), str(end_time), reschedule_time_density)


@problog_export('+str', '+str', '+str', '-list')
def compute_rescheduling_mask(current_time: str,
                              reschedule_time_density: str,
                              rescheduling_window: str) -> list:
    """
    Computes the rescheduling period time mask for a scheduled application.
    :param current_time: The current time of execution.
    :param reschedule_time_density: The time density of the rescheduling.
    :param rescheduling_window: The length of the rescheduling window.
    :return:
    """
    current_time, rescheduling_window =\
        reformat_problog_predicates([current_time, rescheduling_window])

    (current_time_delta,
     rescheduling_window_delta) = convert_time_strings_to_timedelta([current_time,
                                                                     rescheduling_window])

    end_time = current_time_delta + rescheduling_window_delta
    if end_time.days > 0:
        end_time = datetime.timedelta(hours=23, minutes=59, seconds=59)

    return compute_time_mask(str(current_time_delta),
                             str(end_time),
                             reschedule_time_density)


@problog_export('-str', '-str', '-str')
def get_current_time():
    """
    Returns the current time as date, time and weekday string.
    :return: The current time as date, time and weekday string.
    """
    current_time = datetime.datetime.now()
    date = current_time.date().strftime("%d.%m.%Y")
    time = current_time.time().strftime("%H:%M:%S")
    weekday_number = current_time.weekday()

    match weekday_number:
        case 0 : weekday = 'monday'
        case 1 : weekday = 'tuesday'
        case 2 : weekday = 'wednesday'
        case 3 : weekday = 'thursday'
        case 4 : weekday = 'friday'
        case 5 : weekday = 'saturday'
        case 6 : weekday = 'sunday'

    return date, time, weekday


if __name__ == '__main__':
    # timestamp = "2025-03-20 13:23:35"
    # timestamp = "13:23:35"
    # t = get_stamp(timestamp)
    # w = get_weekday(timestamp)
    # h = get_hour(timestamp)
    # m = get_minute(timestamp)
    # s = get_second(timestamp)
    # print(f"Timestamp: {timestamp} \n"
    #       f"Time: {t} \n"
    #       f"Weekday: {w} \n"
          # f"Hour: {h} \n"
          # f"Minute: {m} \n"
          # f"Second: {s}")
    # print(datetime.datetime.strptime("15:45:45", "%H:%M:%S")-datetime.datetime.strptime("13:52:32", "%H:%M:%S"))
    # print((datetime.datetime.strptime("0:0:0", "%H:%M:%S") + 5 * datetime.timedelta(hours=0,minutes=15,seconds=0)).time())
    # print(datetime.datetime.strptime("0:0:0", "%H:%M:%S") + 96 * datetime.timedelta(hours=0, minutes=15, seconds=0))
    # f = datetime.datetime.strptime("0:0:0", "%H:%M:%S") - datetime.datetime.strptime("22:35:15", "%H:%M:%S")
    # print(f)
    # print(compute_time_mask("1:0:0", "5:0:0", "0:15:0"))
    # time_points = compute_time_points("00:15:00")
    # print(f"Number timepoints: {time_points}")

    # Test time frame computation from schedules
    # a_schedule = [0]*15 + [1,1,1] + [0]*6
    # b_schedule = [0]*13 + [1,1] + [0]*9
    # c_schedule = [0]*11 + [1] + [0]*12
    # schedules = [a_schedule, b_schedule, c_schedule]
    # print(compute_scheduled_time_intervals(schedules, "1:00:00"))

    # print(compute_abstract_time_series([100,200,300],0.5))
    # print(compute_time_series_dataframe("01:00:00", [0]*24))

    # resampled_time_series = (compute_time_series_dataframe("00:15:00",[877, 154, 431, 10, 562, 461, 842, 64, 417, 447, 164, 850, 859, 564, 338, 825, 55, 974, 244, 640, 342, 948, 322, 775, 62, 440, 35, 366, 517, 509, 785, 960, 338, 436, 913, 665, 814, 51, 138, 221, 612, 390, 847, 110, 819, 198, 370, 562, 162, 234, 342, 31, 683, 313, 69, 56, 661, 195, 771, 429, 47, 780, 184, 58, 526, 819, 777, 178, 666, 292, 230, 406, 27, 985, 25, 868, 162, 966, 673, 513, 987, 630, 53, 867, 180, 83, 336, 578, 861, 928, 161, 329, 877, 368, 248, 66])
    #                          .resample(datetime.timedelta(hours=1,minutes=0)).mean().ffill())
    # print(resampled_time_series)

    # data = {"solar_production":[877, 154, 431, 10, 562, 461, 842, 64, 417, 447, 164, 850, 859, 564, 338, 825, 55, 974, 244, 640, 342, 948, 322, 775, 62, 440, 35, 366, 517, 509, 785, 960, 338, 436, 913, 665, 814, 51, 138, 221, 612, 390, 847, 110, 819, 198, 370, 562, 162, 234, 342, 31, 683, 313, 69, 56, 661, 195, 771, 429, 47, 780, 184, 58, 526, 819, 777, 178, 666, 292, 230, 406, 27, 985, 25, 868, 162, 966, 673, 513, 987, 630, 53, 867, 180, 83, 336, 578, 861, 928, 161, 329, 877, 368, 248, 66],
    #         "energy_costs":[90, 299, 842, 443, 371, 397, 984, 966, 349, 175, 258, 947, 303, 666, 286, 768, 573, 358, 608, 516, 28, 685, 243, 92, 441, 664, 580, 45, 77, 571, 613, 617, 947, 850, 256, 850, 434, 585, 545, 473, 628, 411, 972, 91, 485, 664, 594, 540, 175, 614, 610, 215, 245, 627, 914, 71, 315, 542, 137, 350, 684, 491, 383, 494, 642, 519, 182, 13, 489, 651, 639, 550, 142, 111, 344, 130, 698, 291, 849, 986, 923, 748, 519, 170, 711, 498, 398, 197, 283, 993, 163, 840, 533, 318, 696, 656],
    #         "base_load":[131, 58, 240, 171, 240, 220, 369, 451, 550, 964, 674, 911, 800, 127, 679, 718, 478, 193, 315, 823, 522, 849, 374, 78, 680, 37, 923, 804, 285, 519, 576, 687, 688, 828, 104, 348, 835, 610, 843, 277, 479, 326, 867, 162, 83, 633, 556, 465, 972, 888, 884, 949, 560, 916, 737, 423, 585, 476, 107, 526, 218, 840, 283, 504, 548, 567, 384, 356, 838, 723, 600, 643, 314, 707, 649, 112, 426, 424, 925, 975, 924, 588, 335, 597, 414, 581, 712, 716, 901, 33, 93, 352, 243, 304, 603, 922]
    #         }
    # time_data = compute_time_series_dataframe("00:15:00", data, False)
    # print(time_data)
    #
    # abstract_data = {"abstract_solar_production":[368.0, 482.25, 469.5, 646.5, 478.25, 596.75, 225.75, 692.75, 588.0, 306.0, 489.75, 487.25, 192.25, 280.25, 514.0, 267.25, 575.0, 398.5, 476.25, 578.5, 634.25, 294.25, 569.75, 389.75],
    #                  "abstract_energy_costs":[418.5, 679.5, 432.25, 505.75, 513.75, 262.0, 432.5, 469.5, 725.75, 509.25, 525.5, 570.75, 403.5, 464.25, 336.0, 513.0, 339.0, 582.25, 181.75, 706.0, 590.0, 451.0, 569.75, 550.75],
    #                  "abstract_base_load":[150.0, 320.0, 774.75, 581.0, 452.25, 455.75, 611.0, 516.75, 492.0, 641.25, 458.5, 434.25, 923.25, 659.0, 423.5, 461.25, 463.75, 701.0, 445.5, 687.5, 611.0, 605.75, 344.75, 518.0]
    #                  }
    # abstract_time_data = compute_time_series_dataframe("01:00:00", abstract_data, False)
    # print(abstract_time_data)
    #
    # compute_time_abstraction_parameters(["a1","a2","a3"],
    #                                     [[10],[10],[10]],
    #                                     [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,15],
    #                                     [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10],
    #                                     [10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10,10],
    #                                     '01:00:00', '00:15:00',"")

    # resampled_application = resample_application_consumption([100,200,312,500,231,345],
    #                                                          datetime.timedelta(minutes=15),
    #                                                          datetime.timedelta(hours=1))
    # print(resampled_application)

    print(compute_rescheduling_mask('14:00:00', '01:00:00', '06:00:00'))

    # tdf =compute_time_series_dataframe('04:00:00',
    #                               {"a": [0,1,0,1,0,0], 'b': [0.0,2.0,0.3,1.2,0.3,0.4]}, False)
    # print(tdf.resample(datetime.timedelta(hours=1)).mean().ffill().dtypes)
    # print(datetime.timedelta(hours=0, minutes=20, seconds=0)/ datetime.timedelta(hours=0, minutes=15, seconds=0))
