from scheduling.python_functions.problog_functions_io import write_general_scheduling_parameters_as_predicates, \
    write_schedulable_time_frames_as_predicates


def set_general_scheduling_parameters():
    write_general_scheduling_parameters_as_predicates(
        "scheduling/io/general_scheduling_parameters.json",
        "scheduling/data/general_scheduling_parameters.problog")

    write_schedulable_time_frames_as_predicates(
        "scheduling/io/schedulable_time_frames.json",
        "scheduling/data/schedulable_time_frames.problog")