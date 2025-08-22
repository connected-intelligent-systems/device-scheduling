% Application-specific time frames in which application scheduling is allowed.

allowed_times_app(monday, a1, '13:00:00', '14:30:00').
allowed_times_app(monday, a1, '17:00:00', '19:30:00').
allowed_times_app(monday, a2, '15:00:00', '17:00:00').
allowed_times_app(monday, a3, '14:00:00', '15:30:00').

allowed_times_app(tuesday, a1, '09:00:00', '13:00:00').
allowed_times_app(tuesday, a2, '10:00:00', '12:00:00').
allowed_times_app(tuesday, a3, '12:00:00', '15:00:00').

allowed_times_app(wednesday, a1, '10:00:00', '15:00:00').
allowed_times_app(wednesday, a2, '14:00:00', '18:00:00').
allowed_times_app(wednesday, a3, '17:00:00', '21:00:00').

allowed_times_app(thursday, a1, '18:00:00', '21:00:00').
allowed_times_app(thursday, a2, '16:00:00', '19:00:00').
allowed_times_app(thursday, a3, '15:00:00', '23:00:00').

allowed_times_app(friday, a1, '10:00:00', '22:00:00').
allowed_times_app(friday, a2, '15:00:00', '18:00:00').
allowed_times_app(friday, a3, '17:00:00', '18:00:00').

allowed_times_app(saturday, a1, '09:30:00', '20:30:00').
allowed_times_app(saturday, a2, '12:00:00', '17:00:00').
allowed_times_app(saturday, a3, '10:00:00', '19:00:00').

allowed_times_app(sunday, a1, '10:30:00', '23:00:00').
allowed_times_app(sunday, a2, '12:00:00', '15:00:00').
allowed_times_app(sunday, a3, '14:00:00', '23:00:00').

