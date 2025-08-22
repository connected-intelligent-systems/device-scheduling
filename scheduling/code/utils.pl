%---List Utils---

% Returns a list [R|RR] consisting of sums between the elements of
% the first list [A|AA] and the second list [B|BB].
sum_list_elementwise([], [], []).
sum_list_elementwise([A|AA], [B|BB], [R|RR]):- R is A + B, sum_list_elementwise(AA, BB, RR).


% Returns a list [R|RR] consisting of differences between the elements of
% the first list [P|PP] and the second list [C|CC].
calc_diff([], [], []).
calc_diff([P|PP], [C|CC], [R|RR]):- calc_diff(PP, CC, RR), R is P - C.


% Multiplies all list elements of a list [H|T] with a constant Const and returns the resulting list [R|RR].
mult_list_const([], _, []).
mult_list_const([H|T], Const, [R|RR]):- mult_list_const(T, Const, RR), R is H * Const.


% Multiplies a list [H|HH] and [M|MM] elementwise and returns the resulting list [R|RR].
% The lists must have the same length.
mult_lists_elementwise([], [], []).
mult_lists_elementwise([H|HH], [M|MM], [R|RR]):- mult_lists_elementwise(HH, MM, RR), R is (H * M).


%mult_list([], [], []).
%mult_list([H|T], MultList, [R|RR]):- nth0(0, T, H2), H2 = 0, R is 0, mult_list(T, MultList, RR).
%mult_list([H|T], MultList, [R|RR]):- nth0(0, T, H2), H2 = 1, R is 0, mult_list_now(MultList, T , RR).

%mult_list_now([],[],[]).
%mult_list_now([Mult | MultList], [H|T], [R|RR]) :- H = 1, R is 10, mult_list_now(MultList, T, RR). %R is H * Mult.
%mult_list_now([Mult | MultList], [H|T], [R|RR]) :- H = 0, R is 0, mult_list_now(MultList, T, RR). %R is H * Mult.


% Returns the maximal element M of a list [H|T] with only positive values.
max_element_list([], 0).
max_element_list([H|T], M) :- max_element_list(T, TM), H > TM, M is H.
max_element_list([H|T], M) :- max_element_list(T, TM), H  =< TM, M is TM.


% Inserts the element E into a sorted list [H|T] and returns the resulting list R.
insert_element_into_sorted_list([], E, [E]).
insert_element_into_sorted_list([H|T], E, [E|[H|T]]) :- E> H.
insert_element_into_sorted_list([H|T], E, [H|RR]) :- E =< H, insert_element_into_sorted_list(T, E, RR).




%---File Utils---

% Writes list elements of list L as predicates with predicate name P to a file F.
write_to_file(F, P, L) :- save_list_elements_as_predicates(F, P,L,_).


% Gets all predicates X with predicate name P, which are saved in file F.
get_predicates(F, P, X) :- use_module(F), call(P, X).


% Writes all predicates
write_and_get(F,P,L,X) :- write_to_file(F, P,L), get_predicates(F, P, X).