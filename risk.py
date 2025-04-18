def calculate_risk_position(df, entry, sl, capital=200, risk_percent=0.02):
    risk_amount = capital * risk_percent
    stop_loss_pips = abs(entry - sl)
    if stop_loss_pips == 0:
        stop_loss_pips = 0.0001
    position_size = round(risk_amount / stop_loss_pips, 4)
    return {
        "risk_amount": round(risk_amount, 2),
        "position_size": position_size
    }
