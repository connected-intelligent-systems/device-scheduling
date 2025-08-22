# device_scheduling

This project aims to schedule devices during a day depending on dynamical energy pricing,
the estimated solar production and base load. The devices, which should be scheduled at
the specific day are first scheduled using an abstract scheduling. This decides a rough time
frame for each device, in which the scheduling is likely to be optimal. This scheduling will
then be later refined to compute a more precise scheduling for each device in which running
this device should be optimal based on the approximated time series and the allowed scheduling
time frames.