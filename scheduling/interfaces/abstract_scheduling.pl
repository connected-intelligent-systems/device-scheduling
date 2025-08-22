:- use_module('scheduling/code/scheduling_main.pl').

% Executes the abstract scheduling given the current weekday Weekday and the apps to schedule Apps
% and returns the apps which got scheduled ScheduledApps with the scheduled time frames ScheduledTimeFrames
% and the resulting saved money MoneySaved.
abstract_scheduling(ScheduledApps, ScheduledTimeFrames, MoneySaved) :-
 get_current_time(Date, Time, Weekday),
 appliances_to_schedule(Apps),
 compute_abstract_parameters(Apps),
 save_weekday_dependent_abstract_app_schedules(Weekday, Apps),
 schedule_abstract_apps_weekday_time_intervals(Weekday, Apps, ScheduledApps, ScheduledTimeFrames, MoneySaved),
 write_schedule_results_to_json('scheduling/io/scheduling_results.json', Date, ScheduledApps, ScheduledTimeFrames, _).

query(abstract_scheduling(ScheduledApps, ScheduledTimeFrames, MoneySaved)).