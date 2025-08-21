%-------------------------------File Description-------------------------------
% Computes values to assess the schedule quality.
%------------------------------------------------------------------------------


%------------------------------------Utility Calculation--------------------------------------

% Computes the energy consumption of an appliance App based on its activations Act
% and returns the total energy consumption of that device in ConsApp.
consumption_of_app(App, Act, ConsApp):- app_cons(App, C), apply_values_to_mask_multiple_occ(Act,C,ConsApp).

abstract_consumption_of_app(App, Act, ConsApp):- abstract_app_cons(App, C),
 apply_values_to_mask_multiple_occ(Act,C,ConsApp).


%consumption_of_app(App, Act, ConsApp):- app_cons(App, C), apply_values_to_mask(Act,C,ConsApp).
%consumption_of_app(App, Act, ConsApp):- app_cons(App, C), mult_list_const(Act, C, ConsApp). %, sum_list(S1, ConsApp).

% TODO if result positive at a timestep at the end, maybe add residual Prod to next timestep (if possible)

% Computes the energy balance of a scheduling in the chosen timeframe when the list of applications [App | Apps] is
% scheduled at activation times [Act | Activations] with the energy production Prod occurring in this timeframe.
energy_balance([App | Apps], [Act | Activations], Prod, Abs, Balance):- \+ Apps = [], Abs = 0,
 consumption_of_app(App, Act, ConsApp),
 calc_diff(Prod, ConsApp, ResidualProd), energy_balance(Apps, Activations, ResidualProd, Abs, Balance).

energy_balance([App | Apps], [Act | Activations], Prod, Abs, Balance):- Apps = [], Abs = 0,
 consumption_of_app(App, Act, CostApp), calc_diff(Prod, CostApp, Balance).

energy_balance([App | Apps], [Act | Activations], Prod, Abs, Balance):- \+ Apps = [], Abs = 1,
 abstract_consumption_of_app(App, Act, ConsApp),
 calc_diff(Prod, ConsApp, ResidualProd), energy_balance(Apps, Activations, ResidualProd, Abs, Balance).

energy_balance([App | Apps], [Act | Activations], Prod, Abs, Balance):- Apps = [], Abs = 1,
 abstract_consumption_of_app(App, Act, CostApp), calc_diff(Prod, CostApp, Balance).


% Computes utility for apps
% Computes the money saved MoneySaved, according to the cost-threshold, when the applications Apps get
% activated at the activation times Activations with the energy production Prod.
saved_money(Apps, Activations, Costs, Prod, MoneySaved):- energy_balance(Apps, Activations, Prod, 0, Balance),
 mult_lists_elementwise(Balance, Costs, EnergyCostsTimepoints), sum_list(EnergyCostsTimepoints, EnergyCostsTotal),
 KWEnergyCostsTotal is EnergyCostsTotal / 1000, cost_threshold(Tr), MoneySaved is KWEnergyCostsTotal + Tr.


% Computes utility for an app
% Computes the money saved MoneySaved, according to the cost-threshold, when the application App gets
% activated at the scheduled activation time Activation with the energy production Prod and returns
% the energy balance Balance after the device scheduling either for discrete Abs=0 or abstract Abs=1 values.
saved_money_app(App, Activation, Prod, Costs, Abs, MoneySaved, Balance):-
 energy_balance([App], [Activation], Prod, Abs, Balance), mult_lists_elementwise(Balance, Costs, EnergyCostsTimepoints),
 sum_list(EnergyCostsTimepoints, EnergyCostsTotal), KWEnergyCostsTotal is EnergyCostsTotal / 1000,
 cost_threshold(Tr), MoneySaved is KWEnergyCostsTotal + Tr.




%-------------------------------------------Evaluation----------------------------------------------

%find_best_scheduling() al(A), timepoints(T), get_possible_device_schedules(A, T, SP), member(activation, SP).

%utility(activation, MoneySaved) :- al(A), prod(P), saved_money(A, activation, P, MoneySaved).
%utility(activation, 1) :- al(A), timepoints(T), get_possible_device_schedules(A, T, SP), member(activation, SP).