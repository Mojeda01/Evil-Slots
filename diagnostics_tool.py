import json
import dearpygui.dearpygui as dpg
import threading
import time
import os
from config_manager import get_reel_probabilities, update_probabilities

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
        
        # Average Win per Spin
        avg_wins = stats['cumulative_avg_wins']
        dpg.set_value("average_win_chart", [spins, avg_wins])
        dpg.fit_axis_data("average_win_chart_x")
        dpg.fit_axis_data("average_win_chart_y")
        
        # Balance Over Time
        balances = [log['balance_after'] for log in logs]
        dpg.set_value("balance_chart", [spins, balances])
        dpg.fit_axis_data("balance_chart_x")
        dpg.fit_axis_data("balance_chart_y")
        
        # Bet Amount Distribution
        bet_amounts = [log['bet_amount'] for log in logs]
        dpg.set_value("bet_distribution_chart", [bet_amounts, [bet_amounts.count(amount) for amount in set(bet_amounts)]])
        dpg.fit_axis_data("bet_distribution_chart_x")
        dpg.fit_axis_data("bet_distribution_chart_y")
        
        # Points Won Over Time
        points_won = [log.get('points_won', 0) for log in logs]
        dpg.set_value("points_won_chart", [spins, points_won])
        dpg.fit_axis_data("points_won_chart_x")
        dpg.fit_axis_data("points_won_chart_y")
        
        # Winnings Breakdown
        regular_winnings = [log.get('regular_winnings', 0) for log in logs]
        jackpot_wins = [log.get('jackpot_win', 0) for log in logs]
        bonus_wins = [log.get('bonus_win', 0) for log in logs]
        dpg.set_value("winnings_breakdown_chart", [spins, regular_winnings, jackpot_wins, bonus_wins])
        dpg.fit_axis_data("winnings_breakdown_chart_x")
        dpg.fit_axis_data("winnings_breakdown_chart_y")
        
        # Jackpot Progression
        jackpot_values = [log.get('current_jackpot', 0) for log in logs]
        dpg.set_value("jackpot_progression_chart", [spins, jackpot_values])
        dpg.fit_axis_data("jackpot_progression_chart_x")
        dpg.fit_axis_data("jackpot_progression_chart_y")
        
        # Win Frequency
        win_frequency = [1 if log.get('total_winnings', 0) > 0 else 0 for log in logs]
        dpg.set_value("win_frequency_chart", [spins, win_frequency])
        dpg.fit_axis_data("win_frequency_chart_x")
        dpg.fit_axis_data("win_frequency_chart_y")
        
        # RTP Over Time
        cumulative_winnings = [sum(log.get('total_winnings', 0) for log in logs[:i+1]) for i in range(len(logs))]
        cumulative_bets = [sum(log['bet_amount'] for log in logs[:i+1]) for i in range(len(logs))]
        rtp_over_time = [w / b * 100 if b > 0 else 0 for w, b in zip(cumulative_winnings, cumulative_bets)]
        dpg.set_value("rtp_over_time_chart", [spins, rtp_over_time])
        dpg.fit_axis_data("rtp_over_time_chart_x")
        dpg.fit_axis_data("rtp_over_time_chart_y")
        
        # Bonus Trigger Frequency
        bonus_triggers = [1 if log.get('bonus_win', 0) > 0 else 0 for log in logs]
        dpg.set_value("bonus_trigger_chart", [spins, bonus_triggers])
        dpg.fit_axis_data("bonus_trigger_chart_x")
        dpg.fit_axis_data("bonus_trigger_chart_y")
    
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

def create_reel_probability_window():
    with dpg.window(label="Reel Probabilities", width=400, height=300):
        dpg.add_text("Current Reel Probabilities")
        for reel, symbols in get_reel_probabilities().items():
            with dpg.collapsing_header(label=reel):
                for symbol, probability in symbols.items():
                    dpg.add_text(f"{symbol}: {probability}")

def main():
    dpg.create_context()

    with dpg.window(label="Slot Machine Diagnostics"):
        dpg.add_text("Statistics", color=(255, 255, 0))
        with dpg.group(horizontal=True):
            dpg.add_text("", tag="total_spins")
            dpg.add_text("", tag="total_winnings")
        with dpg.group(horizontal=True):
            dpg.add_text("", tag="average_win")
            dpg.add_text("", tag="rtp")
        dpg.add_text("", tag="status")
        
        with dpg.group(horizontal=True):
            with dpg.group():
                create_plot("Average Win per Spin", "Spins", "Average Win ($)", "average_win_chart")
                create_plot("Bet Amount Distribution", "Bet Amount", "Frequency", "bet_distribution_chart", series_type="bar")
                create_plot("Winnings Breakdown", "Spins", "Winnings ($)", "winnings_breakdown_chart", series_type="bar")
            
            with dpg.group():
                create_plot("Balance Over Time", "Spins", "Balance ($)", "balance_chart")
                create_plot("Points Won Over Time", "Spins", "Points Won", "points_won_chart")
                create_plot("Jackpot Progression", "Spins", "Jackpot Value ($)", "jackpot_progression_chart")
            
            with dpg.group():
                create_plot("Win Frequency", "Spins", "Win (1) / Loss (0)", "win_frequency_chart", series_type="stem")
                create_plot("RTP Over Time", "Spins", "RTP (%)", "rtp_over_time_chart")
                create_plot("Bonus Trigger Frequency", "Spins", "Bonus Triggered", "bonus_trigger_chart", series_type="stem")
        
        dpg.add_button(label="Show Reel Probabilities", callback=create_reel_probability_window)

    dpg.create_viewport(title="Slot Machine Diagnostics", width=1200, height=800)
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

def create_plot(label, x_label, y_label, tag, height=200, width=380, series_type="line"):
    with dpg.plot(label=label, height=height, width=width):
        dpg.add_plot_legend()
        x_axis = dpg.add_plot_axis(dpg.mvXAxis, label=x_label, tag=f"{tag}_x")
        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label=y_label, tag=f"{tag}_y")
        if series_type == "line":
            dpg.add_line_series([], [], label=label, parent=y_axis, tag=tag)
        elif series_type == "bar":
            dpg.add_bar_series([], [], label=label, parent=y_axis, tag=tag)
        elif series_type == "stem":
            dpg.add_stem_series([], [], label=label, parent=y_axis, tag=tag)

if __name__ == "__main__":
    main()
