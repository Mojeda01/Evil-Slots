import json
import dearpygui.dearpygui as dpg
import threading
import time
import os

last_modified_time = 0

update_needed = threading.Event()

def load_logs():
    try:
        with open('logs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def calculate_stats(logs):
    if not logs:
        return {"total_spins": 0, "total_winnings": 0, "average_win": 0, "rtp": 0, "cumulative_avg_wins": []}
    
    total_spins = len(logs)
    total_winnings = sum(log.get('total_winnings', 0) for log in logs)
    total_bets = sum(log['bet_amount'] for log in logs)
    
    # Calculate cumulative average wins correctly
    cumulative_winnings = 0
    cumulative_avg_wins = []
    for i, log in enumerate(logs):
        cumulative_winnings += log.get('total_winnings', 0)
        cumulative_avg_wins.append(cumulative_winnings / (i + 1))
    
    average_win = total_winnings / total_spins if total_spins > 0 else 0
    rtp = (total_winnings / total_bets) * 100 if total_bets > 0 else 0
    
    return {
        "total_spins": total_spins,
        "total_winnings": total_winnings,
        "average_win": average_win,
        "rtp": rtp,
        "cumulative_avg_wins": cumulative_avg_wins
    }

def update_stats():
    dpg.set_value("status", "Updating...")
    logs = load_logs()
    stats = calculate_stats(logs)
    
    dpg.set_value("total_spins", f"Total Spins: {stats['total_spins']}")
    dpg.set_value("total_winnings", f"Total Winnings: ${stats['total_winnings']:.2f}")
    dpg.set_value("average_win", f"Average Win: ${stats['average_win']:.2f}")
    dpg.set_value("rtp", f"Return to Player: {stats['rtp']:.2f}%")
    
    if logs:
        spins = list(range(1, len(logs) + 1))
        avg_wins = stats['cumulative_avg_wins']
        
        dpg.set_value("balance_chart", [spins, avg_wins])
        dpg.fit_axis_data("x_axis")
        dpg.fit_axis_data("y_axis")
    
    dpg.set_value("status", "Up to date")

def check_file_changes():
    global last_modified_time
    while True:
        try:
            current_modified_time = os.path.getmtime('logs.json')
            if current_modified_time != last_modified_time:
                last_modified_time = current_modified_time
                update_needed.set()
        except FileNotFoundError:
            pass
        time.sleep(0.1)  # Check every 100ms for more responsiveness

def main():
    dpg.create_context()

    with dpg.window(label="Slot Machine Diagnostics"):
        dpg.add_text("Statistics", color=(255, 255, 0))
        dpg.add_text("", tag="total_spins")
        dpg.add_text("", tag="total_winnings")
        dpg.add_text("", tag="average_win")
        dpg.add_text("", tag="rtp")
        dpg.add_text("", tag="status")
        
        with dpg.plot(label="Average Win per Spin", height=300, width=400):
            dpg.add_plot_legend()
            x_axis = dpg.add_plot_axis(dpg.mvXAxis, label="Spins", tag="x_axis")
            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Average Win ($)", tag="y_axis")
            dpg.add_line_series([], [], label="Avg Win", parent=y_axis, tag="balance_chart")

    dpg.create_viewport(title="Slot Machine Diagnostics", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    # Start the background thread to check for file changes
    thread = threading.Thread(target=check_file_changes, daemon=True)
    thread.start()
    
    # Initial update
    update_stats()
    
    while dpg.is_dearpygui_running():
        if update_needed.is_set():
            update_stats()
            update_needed.clear()
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

if __name__ == "__main__":
    main()
