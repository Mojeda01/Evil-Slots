import json
import dearpygui.dearpygui as dpg
import threading
import time
import os
from config_manager import get_reel_probabilities, update_probabilities, get_symbol_payouts, update_symbol_payouts
from database import SessionLocal
from db_models import GameResult
from sqlalchemy import func

last_modified_time = 0
update_needed = threading.Event()

def load_logs():
    db = SessionLocal()
    try:
        return db.query(GameResult).all()
    finally:
        db.close()

def calculate_stats(logs):
    total_spins = len(logs)
    total_bets = sum(log.bet_amount for log in logs if log.bet_amount is not None)
    total_winnings = sum(log.winnings for log in logs if log.winnings is not None)
    
    cumulative_winnings = 0
    cumulative_avg_wins = []
    for i, log in enumerate(logs):
        cumulative_winnings += log.winnings if log.winnings is not None else 0
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
    """Updates the statistics display in the diagnostics tool."""
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
        balances = [log.balance_after if log.balance_after is not None else 0 for log in logs]
        dpg.set_value("balance_chart", [spins, balances])
        dpg.fit_axis_data("balance_chart_x")
        dpg.fit_axis_data("balance_chart_y")
        
        # Points Won Over Time
        points_won = [log.points_won if log.points_won is not None else 0 for log in logs]
        dpg.set_value("points_won_chart", [spins, points_won])
        dpg.fit_axis_data("points_won_chart_x")
        dpg.fit_axis_data("points_won_chart_y")
        
        # Winnings Breakdown
        regular_winnings = [log.regular_winnings if log.regular_winnings is not None else 0 for log in logs]
        jackpot_wins = [log.jackpot_win if log.jackpot_win is not None else 0 for log in logs]
        bonus_wins = [log.bonus_win if log.bonus_win is not None else 0 for log in logs]
        dpg.set_value("winnings_breakdown_chart", [spins, regular_winnings, jackpot_wins, bonus_wins])
        dpg.fit_axis_data("winnings_breakdown_chart_x")
        dpg.fit_axis_data("winnings_breakdown_chart_y")
        
        # Jackpot Progression
        jackpot_values = [log.current_jackpot if log.current_jackpot is not None else 0 for log in logs]
        dpg.set_value("jackpot_progression_chart", [spins, jackpot_values])
        dpg.fit_axis_data("jackpot_progression_chart_x")
        dpg.fit_axis_data("jackpot_progression_chart_y")
        
        # Win Frequency
        win_frequency = [1 if log.winnings and log.winnings > 0 else 0 for log in logs]
        dpg.set_value("win_frequency_chart", [spins, win_frequency])
        dpg.fit_axis_data("win_frequency_chart_x")
        dpg.fit_axis_data("win_frequency_chart_y")
        
        # RTP Over Time
        cumulative_winnings = [sum(log.winnings if log.winnings is not None else 0 for log in logs[:i+1]) for i in range(len(logs))]
        cumulative_bets = [sum(log.bet_amount if log.bet_amount is not None else 0 for log in logs[:i+1]) for i in range(len(logs))]
        rtp_over_time = [w / b * 100 if b > 0 else 0 for w, b in zip(cumulative_winnings, cumulative_bets)]
        dpg.set_value("rtp_over_time_chart", [spins, rtp_over_time])
        dpg.fit_axis_data("rtp_over_time_chart_x")
        dpg.fit_axis_data("rtp_over_time_chart_y")
        
        # Bonus Trigger Frequency
        bonus_triggers = [1 if log.bonus_win and log.bonus_win > 0 else 0 for log in logs]
        dpg.set_value("bonus_trigger_chart", [spins, bonus_triggers])
        dpg.fit_axis_data("bonus_trigger_chart_x")
        dpg.fit_axis_data("bonus_trigger_chart_y")
    
    dpg.set_value("status", "Up to date")

def save_probabilities(sender, app_data, user_data):
    """Saves the new reel probabilities to the configuration."""
    # Initialize a dictionary to store new probabilities
    new_probabilities = {}
    # Iterate through each reel and its symbols
    for reel, symbols in user_data.items():
        # Get the new probability values from the UI sliders
        new_probabilities[reel] = {symbol: dpg.get_value(tag) for symbol, tag in symbols.items()}
    # Update the probabilities in the backend
    update_probabilities(new_probabilities)
    # Update the UI to show that probabilities have been saved
    dpg.set_value("save_status", "Probabilities saved!")

def apply_to_all_reels(sender, app_data, user_data):
    """Applies the probabilities from one reel to all other reels."""
    # Get the selected source reel from the combo box
    source_reel = dpg.get_value("source_reel_combo")
    # Create a dictionary of slider tags for each reel and symbol
    slider_tags = {reel: {symbol: f"{reel}_{symbol}_slider" for symbol in get_reel_probabilities()[reel]} for reel in get_reel_probabilities()}
    
    # Get the probabilities from the source reel
    source_probabilities = {symbol: dpg.get_value(slider_tags[source_reel][symbol]) for symbol in slider_tags[source_reel]}
    
    # Apply the source reel probabilities to all other reels
    for reel in slider_tags:
        if reel != source_reel:
            for symbol, probability in source_probabilities.items():
                dpg.set_value(slider_tags[reel][symbol], probability)
    
    # Update the UI to show that probabilities have been applied
    dpg.set_value("apply_status", f"Applied {source_reel} probabilities to all reels!")

def toggle_probabilities_window():
    """Toggles the visibility of the Reel Probabilities window."""
    # Check if the Reel Probabilities window exists
    if dpg.does_item_exist("Reel Probabilities"):
        # If it exists, delete it (close the window)
        dpg.delete_item("Reel Probabilities")
    else:
        # If it doesn't exist, create the window
        create_reel_probability_window()

def create_reel_probability_window():
    """Creates a new window for adjusting reel probabilities."""
    with dpg.window(label="Reel Probabilities", width=400, height=500, tag="Reel Probabilities"):
        dpg.add_text("Adjust Reel Probabilities")
        
        # Add a combo box to select the source reel for copying probabilities
        dpg.add_combo(("Reel1", "Reel2", "Reel3", "Reel4", "Reel5"), label="Source Reel", default_value="Reel1", tag="source_reel_combo")
        
        # Add a button to apply the selected reel's probabilities to all other reels
        dpg.add_button(label="Apply to All Reels", callback=apply_to_all_reels, tag="apply_to_all_button")
        
        # Add a text element to display the status of the "Apply to All" operation
        dpg.add_text("", tag="apply_status")
        
        # Dictionary to store slider tags for each reel and symbol
        slider_tags = {}
        # Get the current probabilities for all reels
        current_probabilities = get_reel_probabilities()
        
        if not current_probabilities:
            dpg.add_text("Error loading probabilities. Please check database connection.")
        else:
            # Iterate through each reel and its symbols
            for reel, symbols in current_probabilities.items():
                # Create a collapsing header for each reel
                with dpg.collapsing_header(label=reel):
                    reel_sliders = {}
                    # Create a slider for each symbol in the reel
                    for symbol, probability in symbols.items():
                        tag = f"{reel}_{symbol}_slider"
                        # Add a float slider with range 0-1 for probability adjustment
                        dpg.add_slider_float(label=symbol, min_value=0, max_value=1, default_value=probability, tag=tag)
                        reel_sliders[symbol] = tag
                    # Store the sliders for this reel in the slider_tags dictionary
                    slider_tags[reel] = reel_sliders
        
            # Add a button to save the adjusted probabilities
            dpg.add_button(label="Save Probabilities", callback=save_probabilities, user_data=slider_tags)
            # Add a text element to display the status of the save operation
            dpg.add_text("", tag="save_status")

def create_symbol_payout_window():
    """Creates a new window for adjusting symbol payouts."""
    if dpg.does_item_exist("Symbol Payouts"):
        dpg.delete_item("Symbol Payouts")
    
    with dpg.window(label="Symbol Payouts", width=300, height=400, tag="Symbol Payouts"):
        current_payouts = get_symbol_payouts()
        input_tags = {}
        
        # Create input fields for each symbol's payout
        for symbol, payout in current_payouts.items():
            tag = f"{symbol}_payout_input"
            dpg.add_input_float(label=symbol, default_value=payout, tag=tag)
            input_tags[symbol] = tag
        
        # Add buttons for saving and resetting payouts
        dpg.add_button(label="Save Payouts", callback=save_payouts, user_data=input_tags)
        dpg.add_button(label="Reset to Default", callback=reset_payouts, user_data=input_tags)
        dpg.add_text("", tag="payout_status")

def save_payouts(sender, app_data, user_data):
    """Saves the new payout values to the configuration."""
    new_payouts = {symbol: dpg.get_value(tag) for symbol, tag in user_data.items()}
    update_symbol_payouts(new_payouts)
    dpg.set_value("payout_status", "Payouts updated successfully!")

def reset_payouts(sender, app_data, user_data):
    """Resets the payout values to their defaults."""
    default_payouts = {
        'CHER': 5, 'ONIO': 7, 'CLOC': 10, 'STAR': 15, 'DIAMN': 20,
        'WILD': 25, 'BONUS': 30, 'SCAT': 35, 'JACKP': 50
    }
    for symbol, tag in user_data.items():
        dpg.set_value(tag, default_payouts[symbol])
    update_symbol_payouts(default_payouts)
    dpg.set_value("payout_status", "Payouts reset to default!")

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
                create_plot("Winnings Breakdown", "Spins", "Winnings ($)", "winnings_breakdown_chart", series_type="bar")
            
            with dpg.group():
                create_plot("Balance Over Time", "Spins", "Balance ($)", "balance_chart")
                create_plot("Points Won Over Time", "Spins", "Points Won", "points_won_chart")
                create_plot("Jackpot Progression", "Spins", "Jackpot Value ($)", "jackpot_progression_chart")
            
            with dpg.group():
                create_plot("Win Frequency", "Spins", "Win (1) / Loss (0)", "win_frequency_chart", series_type="stem")
                create_plot("RTP Over Time", "Spins", "RTP (%)", "rtp_over_time_chart")
                create_plot("Bonus Trigger Frequency", "Spins", "Bonus Triggered", "bonus_trigger_chart", series_type="stem")
        
        dpg.add_button(label="Probabilities", callback=toggle_probabilities_window)
        dpg.add_button(label="Adjust Symbol Payouts", callback=create_symbol_payout_window)

    dpg.create_viewport(title="Slot Machine Diagnostics", width=1200, height=800)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    
    while dpg.is_dearpygui_running():
        update_stats()  # Update stats on each frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()

def create_plot(label, x_label, y_label, tag, height=200, width=380, series_type="line"):
    """Creates a new plot with the given label, height, and width."""
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
