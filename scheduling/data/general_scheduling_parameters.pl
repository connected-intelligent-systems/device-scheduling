% Application consumption in Wh between actionable timepoints
app_cons(teststecker, [1000]).

% The time between two actionable timepoints
time_density('00:15:00').

% The time between two abstract timepoints
abstract_time_density('01:00:00').

% The time window length for rescheduling applications
rescheduling_time_window('06:00:00').

% Maximal tolerated costs for the scheduled time frame
cost_threshold(55).