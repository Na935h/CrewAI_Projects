import gradio as gr
from accounts import Account, get_share_price

# Initialize the single user account for this demo
account = Account()

def format_currency(value):
    """Helper to format currency strings."""
    return f"${value:,.2f}"

def perform_cash_operation(amount, operation):
    """Handles Deposit and Withdrawal logic."""
    try:
        amount = float(amount)
        if operation == "Deposit":
            account.deposit(amount)
            return f"✅ Successfully deposited {format_currency(amount)}."
        elif operation == "Withdraw":
            account.withdraw(amount)
            return f"✅ Successfully withdrew {format_currency(amount)}."
    except ValueError as e:
        return f"❌ Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

def perform_trade_operation(symbol, quantity, operation):
    """Handles Buy and Sell logic."""
    try:
        qty = int(quantity)
        if operation == "Buy":
            account.buy(symbol, qty)
            return f"✅ Successfully bought {qty} shares of {symbol}."
        elif operation == "Sell":
            account.sell(symbol, qty)
            return f"✅ Successfully sold {qty} shares of {symbol}."
    except ValueError as e:
        return f"❌ Error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected Error: {str(e)}"

def get_dashboard_data():
    """Retrieves current account status for the dashboard."""
    balance = account.balance
    port_value = account.get_portfolio_value()
    pl = account.get_profit_loss()
    
    holdings = account.get_holdings()
    holdings_data = []
    
    if not holdings:
        # Return empty state if no holdings
        pass
    else:
        for sym, qty in holdings.items():
            price = get_share_price(sym)
            total_val = qty * price
            holdings_data.append([sym, qty, format_currency(price), format_currency(total_val)])
            
    return (
        format_currency(balance),
        format_currency(port_value),
        format_currency(pl),
        holdings_data
    )

def get_transaction_log():
    """Retrieves and formats transaction history."""
    txs = account.get_transaction_history()
    data = []
    # Show newest first
    for t in reversed(txs):
        data.append([
            t.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            t.type,
            format_currency(t.amount),
            t.symbol if t.symbol else "-",
            str(t.quantity) if t.quantity else "-",
            format_currency(t.price) if t.price else "-"
        ])
    return data

# Build the Gradio UI
with gr.Blocks(title="Trading Account Demo", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📈 Trading Simulation Platform")
    gr.Markdown("Manage your funds and trade stocks (AAPL, TSLA, GOOGL).")
    
    with gr.Row():
        # Left Column: Cash Management
        with gr.Column():
            gr.Markdown("### 💰 Cash Management")
            with gr.Group():
                cash_amount = gr.Number(label="Amount ($)", value=1000, precision=2)
                cash_action = gr.Radio(["Deposit", "Withdraw"], label="Action", value="Deposit")
                cash_btn = gr.Button("Execute Transaction", variant="primary")
            cash_status = gr.Textbox(label="Result", interactive=False)

        # Right Column: Trading
        with gr.Column():
            gr.Markdown("### 🤝 Stock Trading")
            with gr.Group():
                with gr.Row():
                    trade_symbol = gr.Dropdown(["AAPL", "TSLA", "GOOGL"], label="Symbol", value="AAPL")
                    trade_qty = gr.Number(label="Quantity", value=1, precision=0)
                trade_action = gr.Radio(["Buy", "Sell"], label="Action", value="Buy")
                trade_btn = gr.Button("Execute Trade", variant="primary")
            trade_status = gr.Textbox(label="Result", interactive=False)

    gr.Markdown("---")
    
    # Dashboard Section
    gr.Markdown("### 📊 Account Dashboard")
    refresh_btn = gr.Button("🔄 Refresh Dashboard")
    
    with gr.Group():
        with gr.Row():
            d_balance = gr.Textbox(label="Cash Balance", value="$0.00", interactive=False)
            d_value = gr.Textbox(label="Total Portfolio Value", value="$0.00", interactive=False)
            d_pl = gr.Textbox(label="Total Profit/Loss", value="$0.00", interactive=False)

    with gr.Row():
        d_holdings = gr.Dataframe(
            headers=["Symbol", "Quantity", "Current Price", "Total Value"],
            label="Current Holdings",
            interactive=False,
            datatype=["str", "number", "str", "str"]
        )

    with gr.Accordion("📜 Transaction History", open=False):
        d_history = gr.Dataframe(
            headers=["Time", "Type", "Net Amount", "Symbol", "Quantity", "Price/Share"],
            label="Log",
            interactive=False,
            datatype=["str", "str", "str", "str", "str", "str"]
        )

    # --- Event Wiring ---

    # 1. Cash Button Click
    cash_btn.click(
        perform_cash_operation,
        inputs=[cash_amount, cash_action],
        outputs=[cash_status]
    ).success(
        # Update dashboard after cash op
        get_dashboard_data,
        outputs=[d_balance, d_value, d_pl, d_holdings]
    ).success(
        # Update history after cash op
        get_transaction_log,
        outputs=[d_history]
    )

    # 2. Trade Button Click
    trade_btn.click(
        perform_trade_operation,
        inputs=[trade_symbol, trade_qty, trade_action],
        outputs=[trade_status]
    ).success(
        get_dashboard_data,
        outputs=[d_balance, d_value, d_pl, d_holdings]
    ).success(
        get_transaction_log,
        outputs=[d_history]
    )

    # 3. Refresh Button Click
    refresh_btn.click(
        get_dashboard_data,
        outputs=[d_balance, d_value, d_pl, d_holdings]
    ).success(
        get_transaction_log,
        outputs=[d_history]
    )

    # 4. Initial Load
    demo.load(get_dashboard_data, outputs=[d_balance, d_value, d_pl, d_holdings])
    demo.load(get_transaction_log, outputs=[d_history])

if __name__ == "__main__":
    demo.launch()