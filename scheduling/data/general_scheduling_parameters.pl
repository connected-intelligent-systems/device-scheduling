% Application consumption in Wh between actionable timepoints
app_cons(a1, [800, 1000, 200]).
app_cons(a2, [1500, 500]).
app_cons(a3, [200]).

% The time between two actionable timepoints
time_density('00:15:00').

% The time between two abstract timepoints
abstract_time_density('01:00:00').

% The time window length for rescheduling applications
rescheduling_time_window('06:00:00').

% Maximal tolerated costs for the scheduled time frame
cost_threshold(55).