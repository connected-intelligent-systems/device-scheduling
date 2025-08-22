%-------------------------------File Description-------------------------------
% This file executes the fine-grained scheduling.
%------------------------------------------------------------------------------

:- use_module('scheduling/code/scheduling_main.pl').

% Executes the fine-grained scheduling given the current weekday Weekday, the current time Time and
% the apps to schedule Apps and returns the apps which got scheduled ScheduledApps
% with the scheduled time frames ScheduledTimeFrames and the resulting saved money MoneySaved.
fine_grained_scheduling(Time, Apps, ScheduledApps, ScheduledTimeFrames, MoneySaved) :-
 get_current_time(Date, Time, Weekday),
 appliances_to_schedule(Apps),
 save_fine_grained_app_schedules(Weekday, Time, Apps),
 schedule_apps_weekday_time_intervals(Weekday, Apps, ScheduledApps, ScheduledTimeFrames, MoneySaved),
 write_scheduling_results_to_json('scheduling/io/scheduling_results.json', Date, ScheduledApps, ScheduledTimeFrames, _).

query(fine_grained_scheduling(Time, Apps, ScheduledApps, ScheduledTimeFrames, MoneySaved)).