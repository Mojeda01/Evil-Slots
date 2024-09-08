import json
import dearpygui.dearpygui as dpg
import threading
import time
import os
from config_manager import get_reel_probabilities, update_probabilities, get_symbol_payouts, update_symbol_payouts
from database import SessionLocal
from db_models import GameResult, ReelConfiguration
from sqlalchemy import func, exc as SQLAlchemy
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

def save_probabilities_callback(sender, app_data, user_data):
    new_probabilities = {}
    for reel in range(1, 6):
        new_probabilities[f'Reel{reel}'] = {}
        for symbol in ['CHER', 'ONIO', 'CLOC', 'STAR', 'DIAMN', 'WILD', 'BONUS', 'SCAT', 'JACKP']:
            value = dpg.get_value(f"prob_{reel}_{symbol}")
            if value is None:
                logger.warning(f"Missing probability for Reel{reel}, symbol {symbol}. Setting to 0.0")
                value = 0.0
            else:
                try:
                    value = float(value)
                except ValueError:
                    logger.warning(f"Invalid probability for Reel{reel}, symbol {symbol}. Setting to 0.0")
                    value = 0.0
            new_probabilities[f'Reel{reel}'][symbol] = value
    
    logger.info(f"Sending probabilities to save: {new_probabilities}")
    save_probabilities(new_probabilities)
    dpg.set_value("save_status", "Probabilities saved and verified!")

def save_probabilities(new_probabilities):
    db = SessionLocal()
    try:
        logger.info(f"Attempting to save new probabilities: {new_probabilities}")
        for reel, symbols in new_probabilities.items():
            reel_number = int(reel[4:])
            logger.debug(f"Processing reel {reel_number}")
            for symbol, probability in symbols.items():
                logger.debug(f"Saving {symbol} with probability {probability} for reel {reel_number}")
                config = db.query(ReelConfiguration).filter(
                    ReelConfiguration.reel_number == reel_number,
                    ReelConfiguration.symbol == symbol
                ).first()
                if config:
                    logger.debug(f"Updating existing configuration for {symbol}")
                    config.probability = probability
                else:
                    logger.debug(f"Creating new configuration for {symbol}")
                    new_config = ReelConfiguration(reel_number=reel_number, symbol=symbol, probability=probability)
                    db.add(new_config)
        db.commit()
        logger.info("Probabilities saved successfully")
        
        # Verify save
        saved_probs = get_reel_probabilities()
        logger.info(f"Verifying saved probabilities: {saved_probs}")
        
        # Compare saved probabilities with input
        for reel, symbols in new_probabilities.items():
            for symbol, probability in symbols.items():
                saved_prob = saved_probs[reel].get(symbol)
                if saved_prob != probability:
                    logger.error(f"Mismatch for {reel} {symbol}: Input {probability}, Saved {saved_prob}")
                else:
                    logger.debug(f"Verified {reel} {symbol}: {probability}")
        
        logger.info("Probability verification complete")
    except SQLAlchemy.exc.SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        db.rollback()
    finally:
        db.close()

def apply_to_all_reels(sender, app_data, user_data):
    source_reel = dpg.get_value("source_reel_combo")
    slider_tags = {reel: {symbol: f"prob_{reel[4]}_{symbol}" for symbol in symbols} 
                   for reel, symbols in get_reel_probabilities().items()}
    
    source_probabilities = {symbol: dpg.get_value(slider_tags[source_reel][symbol]) 
                            for symbol in slider_tags[source_reel]}
    
    for reel in slider_tags:
        if reel != source_reel:
            for symbol, probability in source_probabilities.items():
                dpg.set_value(slider_tags[reel][symbol], probability)
    
    dpg.set_value("apply_status", f"Applied {source_reel} probabilities to all reels!")

def toggle_probabilities_window():
    if dpg.does_item_exist("Reel Probabilities"):
        dpg.delete_item("Reel Probabilities")
    else:
        create_reel_probability_window()

def create_reel_probability_window():
    with dpg.window(label="Reel Probabilities", width=400, height=500, tag="Reel Probabilities"):
        dpg.add_text("Adjust Reel Probabilities")
        
        dpg.add_combo(("Reel1", "Reel2", "Reel3", "Reel4", "Reel5"), label="Source Reel", default_value="Reel1", tag="source_reel_combo")
        dpg.add_button(label="Apply to All Reels", callback=apply_to_all_reels, tag="apply_to_all_button")
        dpg.add_text("", tag="apply_status")
        
        slider_tags = {}
        current_probabilities = get_reel_probabilities()
        
        if not current_probabilities:
            dpg.add_text("Error loading probabilities. Please check database connection.")
        else:
            for reel, symbols in current_probabilities.items():
                with dpg.collapsing_header(label=reel):
                    reel_sliders = {}
                    for symbol, probability in symbols.items():
                        tag = f"prob_{reel[4]}_{symbol}"
                        dpg.add_slider_float(label=symbol, min_value=0, max_value=1, default_value=float(probability), format="%.4f", tag=tag)
                        reel_sliders[symbol] = tag
                    slider_tags[reel] = reel_sliders
        
            dpg.add_button(label="Save Probabilities", callback=save_probabilities_callback, user_data=slider_tags)
            dpg.add_text("", tag="save_status")

def create_symbol_payout_window():
    if dpg.does_item_exist("Symbol Payouts"):
        dpg.delete_item("Symbol Payouts")
    
    with dpg.window(label="Symbol Payouts", width=300, height=400, tag="Symbol Payouts"):
        current_payouts = get_symbol_payouts()
        input_tags = {}
        
        for symbol, payout in current_payouts.items():
            tag = f"{symbol}_payout_input"
            dpg.add_input_float(label=symbol, default_value=payout, tag=tag)
            input_tags[symbol] = tag
        
        dpg.add_button(label="Save Payouts", callback=save_payouts, user_data=input_tags)
        dpg.add_button(label="Reset to Default", callback=reset_payouts, user_data=input_tags)
        dpg.add_text("", tag="payout_status")

def save_payouts(sender, app_data, user_data):
    new_payouts = {symbol: dpg.get_value(tag) for symbol, tag in user_data.items()}
    update_symbol_payouts(new_payouts)
    dpg.set_value("payout_status", "Payouts updated successfully!")

def reset_payouts(sender, app_data, user_data):
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
        update_stats()
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
