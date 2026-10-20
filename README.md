# CPU Scheduling Simulator

A desktop project for simulating five operating-system CPU scheduling algorithms with Python and Tkinter. It shows the execution order as a Gantt chart and calculates each process's completion, waiting, and turnaround times.

## Algorithms

- **FCFS (First Come, First Served):** executes available processes in arrival order.
- **SJF (Shortest Job First):** non-preemptive; among processes that have arrived, chooses the shortest burst time.
- **LJF (Longest Job First):** non-preemptive; among processes that have arrived, chooses the longest burst time.
- **Priority Scheduling:** non-preemptive; the smallest priority number means the highest priority.
- **Round Robin:** gives each ready process up to the entered time quantum, repeating until all processes finish.

If the CPU has no ready process, the simulator displays an **IDLE** block. Arrival times may be zero or greater; burst times and Round Robin time quantum must be greater than zero. Process IDs must be unique.

## Requirements

- Python 3.10 or newer
- Tkinter (usually included with Python on Windows and macOS; on Ubuntu/Debian install it with `sudo apt install python3-tk`)

No third-party Python packages are required.

## Run

Open a terminal in this folder and run:

```bash
python main.py
```

On some Linux installations, use:

```bash
python3 main.py
```

Click **Load sample** to add example processes, choose an algorithm, then click **Calculate**. For Round Robin, enter a positive time quantum first. You can also add your own processes, remove selected rows, or clear the list.

## Metrics

For each process:

- `Completion Time = time at which the process finishes`
- `Turnaround Time = Completion Time - Arrival Time`
- `Waiting Time = Turnaround Time - Burst Time`

The averages are the arithmetic mean of the individual process waiting and turnaround times. `First start` is the first time the process gets the CPU; it is distinct from completion time, particularly for Round Robin.

## Project files

- `main.py` — Tkinter interface and Gantt chart
- `scheduler.py` — scheduling algorithms and metric calculations

## Notes for the project presentation

Explain that SJF, LJF, FCFS, and Priority in this simulator are non-preemptive. Round Robin is time-sliced (preemptive). The simulator is an educational model and does not change the operating system's actual process scheduler. No login screen or password storage is included because those features are not needed to demonstrate CPU scheduling and would distract from the core project.
