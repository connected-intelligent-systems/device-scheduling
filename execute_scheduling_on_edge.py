from clearml import Task

task = Task.create(project_name='ForeSightNEXT/FSN_Edge_Scheduling',
                   repo='https://github.com/JaMueDFKI/device_scheduling',
                   # task_name='Scheduling_on_Edge 96 tp day-time-dependent Test ' + str(0),
                   # task_name='Possible Device Schedules Test ' + str(0),
                   task_name="Abstract Scheduling on Edge",
                   script='execute_scheduling.py',
                   requirements_file='requirements_2.txt',
                   add_task_init_call=True,
                   docker='python:3.9',
                   docker_args='-e CLEARML_AGENT_GIT_USER=oauth2 -e CLEARML_AGENT_GIT_PASS=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')

# Task.enqueue(task=task, queue_name='default')
Task.enqueue(task=task, queue_name='rpi5')
