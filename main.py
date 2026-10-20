"""CPU Scheduling Simulator - graphical interface built with Tkinter."""

import tkinter as tk
from tkinter import messagebox, ttk

from scheduler import Process, ScheduleResult, schedule


BG = "#f4f7fb"
CARD = "#ffffff"
INK = "#172033"
MUTED = "#61708a"
BLUE = "#2855d9"


class SchedulingApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("CPU Scheduling Simulator")
        self.root.geometry("1080x760")
        self.root.minsize(880, 650)
        self.root.configure(bg=BG)
        self.processes: list[Process] = []
        self.result: ScheduleResult | None = None
        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD)
        style.configure("TLabel", background=BG, foreground=INK, font=("Arial", 10))
        style.configure("Card.TLabel", background=CARD, foreground=INK, font=("Arial", 10))
        style.configure("Title.TLabel", background=BG, foreground=INK,
                        font=("Arial", 22, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Arial", 10))
        style.configure("Metric.TLabel", background=CARD, foreground=BLUE,
                        font=("Arial", 17, "bold"))
        style.configure("MetricName.TLabel", background=CARD, foreground=MUTED,
                        font=("Arial", 9))
        style.configure("Treeview", rowheight=27, font=("Arial", 9),
                        background=CARD, fieldbackground=CARD)
        style.configure("Treeview.Heading", font=("Arial", 9, "bold"))
        style.configure("Primary.TButton", font=("Arial", 10, "bold"), padding=(12, 7))
        style.configure("TButton", padding=(9, 6))

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, padding=(22, 18))
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="CPU Scheduling Simulator", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer,
                  text="Compare process scheduling algorithms and view waiting/turnaround times.",
                  style="Sub.TLabel").pack(anchor="w", pady=(3, 14))

        input_card = ttk.Frame(outer, style="Card.TFrame", padding=14)
        input_card.pack(fill="x", pady=(0, 12))
        ttk.Label(input_card, text="Add a process", style="Card.TLabel",
                  font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 10))

        self.pid_var = tk.StringVar()
        self.arrival_var = tk.StringVar(value="0")
        self.burst_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="1")
        fields = [("Process ID", self.pid_var, 12), ("Arrival time", self.arrival_var, 12),
                  ("Burst time", self.burst_var, 12), ("Priority", self.priority_var, 10)]
        for col, (label, variable, width) in enumerate(fields):
            ttk.Label(input_card, text=label, style="Card.TLabel").grid(row=1, column=col * 2,
                                                                         sticky="w", padx=(0, 6))
            entry = ttk.Entry(input_card, textvariable=variable, width=width)
            entry.grid(row=2, column=col * 2, sticky="ew", padx=(0, 14))
            if label == "Process ID":
                entry.bind("<Return>", lambda _event: self.add_process())
        ttk.Button(input_card, text="Add process", style="Primary.TButton",
                   command=self.add_process).grid(row=2, column=8, padx=(2, 0))
        ttk.Label(input_card, text="Priority: lower number means higher priority. Priority is used only by Priority Scheduling.",
                  style="Card.TLabel", foreground=MUTED).grid(row=3, column=0, columnspan=9,
                                                                sticky="w", pady=(9, 0))
        for col in range(9):
            input_card.grid_columnconfigure(col, weight=1 if col % 2 == 0 else 0)

        middle = ttk.Frame(outer)
        middle.pack(fill="both", expand=True)
        process_card = ttk.Frame(middle, style="Card.TFrame", padding=12)
        process_card.pack(side="left", fill="both", expand=True, padx=(0, 8))
        ttk.Label(process_card, text="Processes", style="Card.TLabel",
                  font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))
        process_columns = ("pid", "arrival", "burst", "priority")
        self.process_tree = ttk.Treeview(process_card, columns=process_columns, show="headings", height=8)
        for key, label, width in [("pid", "PID", 100), ("arrival", "Arrival", 100),
                                  ("burst", "Burst", 100), ("priority", "Priority", 100)]:
            self.process_tree.heading(key, text=label)
            self.process_tree.column(key, width=width, anchor="center")
        self.process_tree.pack(fill="both", expand=True)
        process_buttons = ttk.Frame(process_card, style="Card.TFrame")
        process_buttons.pack(fill="x", pady=(8, 0))
        ttk.Button(process_buttons, text="Remove selected", command=self.remove_selected).pack(side="left")
        ttk.Button(process_buttons, text="Load sample", command=self.load_sample).pack(side="left", padx=6)
        ttk.Button(process_buttons, text="Clear all", command=self.clear_all).pack(side="right")

        settings = ttk.Frame(middle, style="Card.TFrame", padding=14)
        settings.pack(side="right", fill="y", padx=(8, 0))
        ttk.Label(settings, text="Run simulation", style="Card.TLabel",
                  font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 10))
        ttk.Label(settings, text="Algorithm", style="Card.TLabel").pack(anchor="w")
        self.algorithm_var = tk.StringVar(value="FCFS")
        self.algorithm_box = ttk.Combobox(settings, textvariable=self.algorithm_var,
                                          values=("FCFS", "SJF", "LJF", "Priority", "Round Robin"),
                                          state="readonly", width=20)
        self.algorithm_box.pack(fill="x", pady=(4, 10))
        self.algorithm_box.bind("<<ComboboxSelected>>", self._algorithm_changed)
        ttk.Label(settings, text="Time quantum (Round Robin)", style="Card.TLabel").pack(anchor="w")
        self.quantum_var = tk.StringVar(value="2")
        self.quantum_entry = ttk.Entry(settings, textvariable=self.quantum_var, width=22)
        self.quantum_entry.pack(fill="x", pady=(4, 12))
        ttk.Button(settings, text="Calculate", style="Primary.TButton",
                   command=self.calculate).pack(fill="x")
        ttk.Label(settings, text="FCFS: arrival order\nSJF: shortest burst first\nLJF: longest burst first\nPriority: lowest number first\nRound Robin: time-sliced",
                  style="Card.TLabel", foreground=MUTED, justify="left").pack(anchor="w", pady=(16, 0))

        results_card = ttk.Frame(outer, style="Card.TFrame", padding=12)
        results_card.pack(fill="both", expand=True, pady=(12, 0))
        ttk.Label(results_card, text="Results", style="Card.TLabel",
                  font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 8))

        metrics = ttk.Frame(results_card, style="Card.TFrame")
        metrics.pack(fill="x", pady=(0, 10))
        self.avg_wait_label = self._metric(metrics, "Average waiting time", "—", 0)
        self.avg_turn_label = self._metric(metrics, "Average turnaround time", "—", 1)
        self.makespan_label = self._metric(metrics, "Total completion time", "—", 2)

        result_columns = ("pid", "arrival", "burst", "priority", "start", "completion", "waiting", "turnaround")
        self.result_tree = ttk.Treeview(results_card, columns=result_columns, show="headings", height=5)
        headings = [("pid", "PID"), ("arrival", "Arrival"), ("burst", "Burst"),
                    ("priority", "Priority"), ("start", "First start"),
                    ("completion", "Completion"), ("waiting", "Waiting"),
                    ("turnaround", "Turnaround")]
        for key, label in headings:
            self.result_tree.heading(key, text=label)
            self.result_tree.column(key, width=90, anchor="center")
        self.result_tree.pack(fill="x")
        ttk.Label(results_card, text="Gantt chart", style="Card.TLabel",
                  font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 3))
        self.gantt_canvas = tk.Canvas(results_card, height=88, bg=CARD, highlightthickness=0)
        self.gantt_canvas.pack(fill="x")
        self.gantt_canvas.bind("<Configure>", lambda _event: self._draw_gantt())
        self.status_var = tk.StringVar(value="Add processes, choose an algorithm, then select Calculate.")
        ttk.Label(outer, textvariable=self.status_var, style="Sub.TLabel").pack(anchor="w", pady=(7, 0))
        self._algorithm_changed()

    def _metric(self, parent: ttk.Frame, title: str, value: str, column: int) -> ttk.Label:
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(10, 5))
        frame.grid(row=0, column=column, sticky="ew", padx=(0 if column == 0 else 7, 0))
        parent.grid_columnconfigure(column, weight=1)
        ttk.Label(frame, text=title, style="MetricName.TLabel").pack(anchor="w")
        label = ttk.Label(frame, text=value, style="Metric.TLabel")
        label.pack(anchor="w", pady=(2, 0))
        return label

    def _algorithm_changed(self, _event: object = None) -> None:
        state = "normal" if self.algorithm_var.get() == "Round Robin" else "disabled"
        self.quantum_entry.configure(state=state)

    def add_process(self) -> None:
        pid = self.pid_var.get().strip()
        if not pid:
            messagebox.showerror("Invalid input", "Enter a process ID, such as P1.", parent=self.root)
            return
        if any(p.pid == pid for p in self.processes):
            messagebox.showerror("Invalid input", "Each process ID must be unique.", parent=self.root)
            return
        try:
            arrival = int(self.arrival_var.get().strip())
            burst = int(self.burst_var.get().strip())
            priority = int(self.priority_var.get().strip())
            if arrival < 0:
                raise ValueError("Arrival time cannot be negative.")
            if burst <= 0:
                raise ValueError("Burst time must be greater than zero.")
        except ValueError as exc:
            messagebox.showerror("Invalid input", str(exc) or "Arrival, burst, and priority must be whole numbers.", parent=self.root)
            return
        process = Process(pid, arrival, burst, priority, len(self.processes))
        self.processes.append(process)
        self.process_tree.insert("", "end", iid=pid,
                                 values=(pid, arrival, burst, priority))
        self.pid_var.set("")
        self.burst_var.set("")
        self.pid_var.set(f"P{len(self.processes) + 1}")
        self.status_var.set(f"Added {pid}. {len(self.processes)} process(es) ready.")

    def remove_selected(self) -> None:
        selected = self.process_tree.selection()
        if not selected:
            self.status_var.set("Select a process to remove.")
            return
        remove_ids = set(selected)
        self.processes = [p for p in self.processes if p.pid not in remove_ids]
        for iid in selected:
            self.process_tree.delete(iid)
        self._renumber_order()
        self.status_var.set("Selected process(es) removed.")

    def _renumber_order(self) -> None:
        self.processes = [Process(p.pid, p.arrival, p.burst, p.priority, i)
                          for i, p in enumerate(self.processes)]

    def load_sample(self) -> None:
        self.clear_all(update_message=False)
        examples = [("P1", 0, 5, 2), ("P2", 1, 3, 1), ("P3", 2, 8, 3), ("P4", 3, 6, 2)]
        for i, (pid, arrival, burst, priority) in enumerate(examples):
            process = Process(pid, arrival, burst, priority, i)
            self.processes.append(process)
            self.process_tree.insert("", "end", iid=pid,
                                     values=(pid, arrival, burst, priority))
        self.pid_var.set("P5")
        self.status_var.set("Sample processes loaded. Choose an algorithm and calculate.")

    def clear_all(self, update_message: bool = True) -> None:
        self.processes.clear()
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self.result = None
        self.avg_wait_label.configure(text="—")
        self.avg_turn_label.configure(text="—")
        self.makespan_label.configure(text="—")
        self.gantt_canvas.delete("all")
        self.pid_var.set("P1")
        self.arrival_var.set("0")
        self.burst_var.set("")
        self.priority_var.set("1")
        if update_message:
            self.status_var.set("All processes and results cleared.")

    def calculate(self) -> None:
        quantum = None
        if self.algorithm_var.get() == "Round Robin":
            try:
                quantum = int(self.quantum_var.get().strip())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Invalid input", "Time quantum must be a whole number greater than zero.", parent=self.root)
                return
        try:
            self.result = schedule(self.processes, self.algorithm_var.get(), quantum)
        except ValueError as exc:
            messagebox.showerror("Cannot calculate", str(exc), parent=self.root)
            return

        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        for row in self.result.rows:
            self.result_tree.insert("", "end", values=(row.pid, row.arrival, row.burst,
                                  row.priority, row.start, row.completion,
                                  row.waiting, row.turnaround))
        self.avg_wait_label.configure(text=f"{self.result.average_waiting:.2f}")
        self.avg_turn_label.configure(text=f"{self.result.average_turnaround:.2f}")
        self.makespan_label.configure(text=str(self.result.makespan))
        self._draw_gantt()
        self.status_var.set(f"{self.result.algorithm} simulation completed successfully.")

    def _draw_gantt(self) -> None:
        canvas = self.gantt_canvas
        canvas.delete("all")
        if not self.result or not self.result.gantt:
            return
        width = max(canvas.winfo_width(), 500)
        left, right = 18, width - 18
        total_time = max(self.result.makespan, 1)
        unit = (right - left) / total_time
        y1, y2 = 17, 54
        colors = ["#dce7ff", "#dcf5e8", "#ffedcf", "#f2ddff", "#ffe0e0", "#d7f2f2"]
        palette: dict[str, str] = {}
        for index, segment in enumerate(self.result.gantt):
            x1 = left + segment.start * unit
            x2 = left + segment.end * unit
            if segment.pid == "IDLE":
                color = "#e8ebf0"
            else:
                if segment.pid not in palette:
                    palette[segment.pid] = colors[len(palette) % len(colors)]
                color = palette[segment.pid]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#8491a5", width=1)
            if x2 - x1 > 20:
                canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                  text=segment.pid, fill=INK, font=("Arial", 9, "bold"))
            canvas.create_text(x1, 69, text=str(segment.start), anchor="n",
                               fill=MUTED, font=("Arial", 8))
        canvas.create_text(left + total_time * unit, 69, text=str(total_time), anchor="n",
                           fill=MUTED, font=("Arial", 8))


def main() -> None:
    root = tk.Tk()
    SchedulingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
