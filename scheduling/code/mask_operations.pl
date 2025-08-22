%-------------------------------File Description-------------------------------
% This file contains all functions regarding the computation of masks.
%------------------------------------------------------------------------------


%------------------------------Mask Utils--------------------------------------

% Applies the values [V|VR] to a mask [M|MR] and returns the resulting list [R|RR].
apply_values_to_mask([], [], []).
apply_values_to_mask([M|MR], [V|VR], [R|RR]) :- M = 0, R is M, apply_values_to_mask(MR, [V|VR], RR).
apply_values_to_mask([M|MR], [], [R|RR]) :- M = 0, R is M, apply_values_to_mask(MR, [], RR).
apply_values_to_mask([M|MR], [V|VR], [R|RR]) :- M = 1, R is V, apply_values_to_mask(MR, VR, RR).


% TODO maybe also allow unfinished mask applications at the end
% Applies the values in list VL to the mask M and saves the resulting list in R.
% Allows for multiple occurrences of consecutive 1s in length of VL.
apply_values_to_mask_multiple_occ(M, VL, R) :- apply_values_to_mask_multiple_occ(M, VL, 0, R).


% Applies the values in list VL to a mask [M|MR] and returns the resulting list [R|RR].
% The next value to use is tracked with the pointer VP.
% The mask must have segments of consecutive 1s in length of the value list.
% Multiple occurrences of such segments are possible.
apply_values_to_mask_multiple_occ([], _, 0, []).

apply_values_to_mask_multiple_occ([M|MR], VL, VP, [R|RR]) :- M = 0, VP = 0, R is M,
 apply_values_to_mask_multiple_occ(MR, VL, VP, RR).

apply_values_to_mask_multiple_occ([M|MR], VL, VP, [R|RR]) :- M = 1, nth0(VP, VL, V),  R is V, length(VL, L),
 NVP is (VP + 1) mod L, apply_values_to_mask_multiple_occ(MR, VL, NVP, RR).

% Returns a mask [R|RR] consisting of the combined mask of the masks [A|AA] and [B|BB].
combine_masks([], [], []).
combine_masks([A|AA], [B|BB], [R|RR]):- X is A + B, X >= 1, R is 1, sum_list_elementwise(AA, BB, RR).
combine_masks([A|AA], [B|BB], [R|RR]):- X is A + B, X = 0, R is 0, sum_list_elementwise(AA, BB, RR).


% Returns the first element S and last element E of the mask M.
get_first_and_last_element_of_mask(M, S, E) :- get_first_and_last_element_of_mask(M, 0, -1, -1, S, E).


% Returns the first element S and last element E of the mask [M|MT] using the helper variables HS and HE and
% the index variable I.
get_first_and_last_element_of_mask([], I, HS, HE, HS, HE).

get_first_and_last_element_of_mask([M|MT], I, HS, HE, S, E) :- M = 0, NI is I + 1,
 get_first_and_last_element_of_mask(MT, NI, HS, HE, S, E).

get_first_and_last_element_of_mask([M|MT], I, HS, HE, S, E) :- M = 1, HS = -1, NI is I + 1,
 get_first_and_last_element_of_mask(MT, NI, I, I, S, E).

get_first_and_last_element_of_mask([M|MT], I, HS, HE, S, E) :- M = 1, HS > 0, NI is I + 1,
  get_first_and_last_element_of_mask(MT, NI, HS, I, S, E).


% Returns lists of start points [S|ST] and end points [E|ET] given the masks [M|MT].
get_first_and_last_element_of_masks([], [], []).
get_first_and_last_element_of_masks([M|MT], [S|ST], [E|ET]) :- get_first_and_last_element_of_mask(M, S, E),
 get_first_and_last_element_of_masks(MT, ST, ET).



%------------------------------------Day-Time-Dependent Scheduling---------------------------------

%.........Mask Computation.............

% Returns the list of all allowed scheduling periods SP of a weekday Weekday.
scheduling_periods_weekday(Weekday, SP) :- findall((ST,ET), allowed_times(Weekday,ST,ET),SP).


% Returns the list of all allowed scheduling periods SP of an application App at a weekday Weekday.
scheduling_periods_weekday(Weekday, App, SP) :- findall((ST,ET), allowed_times_app(Weekday, App, ST,ET),SP).


% Computes the mask SM containing all allowed scheduling_periods,
% given the list of all start and end points [(ST,ET)|SPR] of such periods and the time density used .
compute_scheduling_period_mask([], TD, []).

compute_scheduling_period_mask([(ST,ET)|SPR], TD, SM) :- compute_scheduling_period_mask(SPR, TD, MR),
 MR = [], compute_time_mask(ST, ET, TD, SM).

compute_scheduling_period_mask([(ST,ET)|SPR], TD, SM) :- compute_scheduling_period_mask(SPR, TD, MR),
 \+ MR = [], compute_time_mask(ST, ET, TD, M), combine_masks(M,MR,SM).


% Compute the scheduling period mask for a weekday Weekday with time density TD.
compute_scheduling_period_mask_weekday(Weekday, TD, SPM) :- scheduling_periods_weekday(Weekday, SP),
 compute_scheduling_period_mask(SP, TD, SPM).


% Compute the scheduling period mask for an application App at a weekday Weekday with time density TD.
compute_scheduling_period_mask_weekday(Weekday, App, TD, SPM) :- scheduling_periods_weekday(Weekday, App, SP),
 compute_scheduling_period_mask(SP, TD, SPM).



%..........Fine-grained Scheduling Mask Computation...............

% Returns the list of all planned schedules SP of a weekday Weekday.
planned_schedules_weekday(Weekday, App, SP) :- findall((S), planned_schedule(Weekday, App, S), SP).


% Computes the rescheduling mask RM at the start time ST for the app App at weekday Weekday with
% rescheduling time density RTD.
%compute_reschedule_mask(Weekday, App, RTD, RM) :- planned_schedules_weekday(Weekday, App, [SP]),
% planned_schedule_density(Weekday, App, STD), change_schedule_time_density(SP, STD, RTD, RSP),
% relative_rescheduling_start_point(RRS), rescheduling_time_window(RTW),
% compute_rescheduling_mask(RSP, RTD, RRS, RTW, RM).

% Computes the rescheduling mask RM at the current time CT at weekday Weekday with rescheduling time density RTD.
compute_reschedule_mask(CT, RTD, RM) :- rescheduling_time_window(RTW),
 compute_rescheduling_mask(CT, RTD, RTW, RM).


% Computes the reschedule masks RAMS for the applications Apps given the weekday Weekday, the
% rescheduling time density RTD and the current time CT.
compute_reschedule_application_masks(Weekday, CT, Apps, RTD, RAMS) :-
 compute_reschedule_mask(CT, RTD, RM),
 compute_reschedule_application_masks_apps(Weekday, Apps, RTD, RM, RAMS).

% Computes the reschedule masks [RAM|RAMS] for the applications [App|Apps] given the weekday Weekday, the
% rescheduling time density RTD and the rescheduling mask RM.
compute_reschedule_application_masks_apps(Weekday, [], RTD, RM, []).

compute_reschedule_application_masks_apps(Weekday, [App|Apps], RTD, RM, [PA|RAMS]) :-
 planned_schedules_weekday(Weekday, App, [SP]), planned_schedule_density(Weekday, App, STD),
 change_schedule_time_density(SP, STD, RTD, RSP), mult_lists_elementwise(RSP, RM, PA),
 sum_list(PA, SPA), SPA = 0, compute_reschedule_application_masks_apps(Weekday, Apps, RTD, RM, RAMS).

compute_reschedule_application_masks_apps(Weekday, [App|Apps], RTD, RM, [RAM|RAMS]) :-
 planned_schedules_weekday(Weekday, App, [SP]), planned_schedule_density(Weekday, App, STD),
 change_schedule_time_density(SP, STD, RTD, RSP), mult_lists_elementwise(RSP, RM, PA),
 sum_list(PA, SPA), SPA > 0, scheduling_periods_weekday(Weekday, App, SPW),
 compute_scheduling_period_mask(SPW, RTD, SPM), mult_lists_elementwise(SPM, PA, RAM),
 compute_reschedule_application_masks_apps(Weekday, Apps, RTD, RM, RAMS).

