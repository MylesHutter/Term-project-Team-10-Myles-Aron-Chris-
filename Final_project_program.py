import random
import textwrap
import time
def main()

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False




class UserProfile:
    def __init__(self, name, age, occupation, marital_status, goal):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.marital_status = marital_status
        self.goal = goal

    def summary(self):
        return (
            f"\nProfile for {self.name}:\n"
            f"  Age: {self.age}\n"
            f"  Occupation: {self.occupation}\n"
            f"  Marital status: {self.marital_status}\n"
            f"  Savings goal: {self.goal}\n"
        )

    def recommended_budget_percentages(self):
        """
        Give a simple example budget split based on the goal.
        This is only for learning.
        """
        base = {
            "Needs": 50,
            "Wants": 30,
            "Savings / Investing": 20
        }

        goal_lower = self.goal.lower()

        if "debt" in goal_lower:
            base["Savings / Investing"] = 30
            base["Wants"] = 20
        elif "house" in goal_lower or "home" in goal_lower:
            base["Savings / Investing"] = 25
            base["Wants"] = 25
        elif "retire" in goal_lower:
            base["Savings / Investing"] = 30
            base["Wants"] = 20

        return base


class Portfolio:
    def __init__(self, starting_cash=10000.0):
        self.cash = float(starting_cash)
        self.holdings = {}  # ticker -> shares

    def buy(self, ticker, price, amount):
        cost = price * amount
        if cost > self.cash:
            return False, "You do not have enough cash for that purchase."
        self.cash -= cost
        self.holdings[ticker] = self.holdings.get(ticker, 0) + amount
        return True, f"Bought {amount} shares of {ticker} at ${price:.2f}."

    def sell(self, ticker, price, amount):
        shares = self.holdings.get(ticker, 0)
        if amount > shares:
            return False, "You do not own that many shares."
        self.holdings[ticker] = shares - amount
        self.cash += price * amount
        return True, f"Sold {amount} shares of {ticker} at ${price:.2f}."

    def total_value(self, market):
        value = self.cash
        for ticker, shares in self.holdings.items():
            value += shares * market.prices.get(ticker, 0)
        return value

    def pretty_print(self, market):
        print("\nYour portfolio:")
        print(f"  Cash: ${self.cash:.2f}")
        if not self.holdings:
            print("  You do not own any stocks yet.")
        else:
            for ticker, shares in self.holdings.items():
                price = market.prices.get(ticker, 0)
                position_value = shares * price
                print(f"  {ticker}: {shares} shares at ${price:.2f} "
                      f"(value ${position_value:.2f})")
        print(f"  Total value: ${self.total_value(market):.2f}")


class StockMarket:
    """
    Very simple mock stock market for SAFE, GROW and YOLO stocks.
    """

    def __init__(self):
        self.prices = {
            "SAFE": 50.0,   # low risk
            "GROW": 35.0,   # medium risk
            "YOLO": 10.0    # high risk
        }
        self.history = {ticker: [price] for ticker, price in self.prices.items()}
        self.day = 0

    def simulate_day(self):
        """
        Move each stock price a random percent each day.
        """
        self.day += 1
        for ticker in self.prices:
            current = self.prices[ticker]

            if ticker == "SAFE":
                change_percent = random.uniform(-0.015, 0.015)
            elif ticker == "GROW":
                change_percent = random.uniform(-0.03, 0.03)
            else:
                change_percent = random.uniform(-0.07, 0.07)

            new_price = current * (1 + change_percent)
            new_price = max(new_price, 1.0)  # do not drop below 1
            self.prices[ticker] = new_price
            self.history[ticker].append(new_price)

    def print_table(self):
        print(f"\nDay {self.day} prices:")
        for ticker, price in self.prices.items():
            print(f"  {ticker}: ${price:.2f}")

    def print_ascii_chart(self, ticker, last_n=15):
        """
        Text chart that animates over time in the terminal.
        """
        prices = self.history.get(ticker, [])
        if not prices:
            print("No prices to chart yet.")
            return

        if len(prices) > last_n:
            prices = prices[-last_n:]

        max_price = max(prices)
        min_price = min(prices)
        span = max_price - min_price if max_price != min_price else 1

        print(f"\nPrice chart for {ticker} (last {len(prices)} days)")
        for i, p in enumerate(prices):
            normalized = int((p - min_price) / span * 30)
            bar = "#" * max(1, normalized)
            print(f"  Day {self.day - len(prices) + 1 + i:>3}: "
                  f"{bar} ${p:6.2f}")

    def plot_matplotlib_chart(self, ticker):
        """
        Real line chart using matplotlib.
        """
        if not MATPLOTLIB_AVAILABLE:
            print("\nMatplotlib is not installed. Install it with:")
            print("  pip install matplotlib")
            return

        prices = self.history.get(ticker, [])
        if not prices:
            print("No prices to chart yet.")
            return

        days = list(range(len(prices)))
        plt.figure()
        plt.plot(days, prices, marker="o")
        plt.title(f"{ticker} price history")
        plt.xlabel("Day")
        plt.ylabel("Price")
        plt.grid(True)
        plt.tight_layout()
        plt.show()




def ask_int(prompt, min_value=None, max_value=None):
    while True:
        value_str = input(prompt)
        if value_str.strip() == "":
            print("Please enter a number.")
            continue
        try:
            value = int(value_str)
        except ValueError:
            print("That is not a valid integer. Try again.")
            continue

        if min_value is not None and value < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return value


def ask_float(prompt, min_value=None, max_value=None):
    while True:
        value_str = input(prompt)
        if value_str.strip() == "":
            print("Please enter a number.")
            continue
        try:
            value = float(value_str)
        except ValueError:
            print("That is not a valid number. Try again.")
            continue

        if min_value is not None and value < min_value:
            print(f"Value must be at least {min_value}.")
            continue
        if max_value is not None and value > max_value:
            print(f"Value must be at most {max_value}.")
            continue
        return value


def ask_choice(prompt, options):
    """
    Ask user to choose from a list of options.
    """
    while True:
        print(prompt)
        for i, opt in enumerate(options, start=1):
            print(f"  {i}. {opt}")
        choice = ask_int("Enter a number: ", 1, len(options))
        return options[choice - 1]




def wrap_print(text):
    print(textwrap.fill(text, width=80))


def advice_bot(profile, portfolio=None):
    wrap_print(
        "\nWelcome to the Hint Bot. Ask me simple questions about budgeting "
        "or investing.\nType 'back' to return to the main menu."
    )

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("back", "exit", "quit"):
            print("Returning to main menu.")
            break

        q_low = question.lower()

        if "budget" in q_low or "spend" in q_low:
            rec = profile.recommended_budget_percentages()
            wrap_print(
                "A simple way to start a budget is to split your income into "
                f"needs, wants, and savings. For you, one possible split is "
                f"{rec['Needs']} percent needs, {rec['Wants']} percent wants, "
                f"and {rec['Savings / Investing']} percent savings or investing. "
                "This is not financial advice, just an educational example."
            )
        elif "invest" in q_low or "stock" in q_low:
            wrap_print(
                "Before investing, it is usually smart to know your goal "
                "and time horizon. In this game we show three stocks: "
                "SAFE (lower risk), GROW (medium risk) and YOLO (higher risk). "
                "Diversifying across different risk levels is often safer "
                "than putting everything into one very risky stock. "
                "This is for learning only, not real investment advice."
            )
        elif "debt" in q_low or "loans" in q_low:
            wrap_print(
                "With debt, an educational idea is to focus on the highest "
                "interest debt first while still making minimum payments "
                "on everything else. In real life, you would want to talk "
                "to a professional, but here you can practice thinking "
                "about priorities."
            )
        else:
            wrap_print(
                "I do not have a specific answer programmed for that. "
                "Try asking about budgeting, investing, or debt."
            )

        if portfolio is not None:
            wrap_print(
                f"\nRight now in the game your portfolio has about "
                f"${portfolio.cash:.2f} in cash."
            )




def lesson_financial_literacy():
    print("\n========== Financial Literacy Lesson ==========")
    wrap_print(
        "Financial literacy means understanding how money flows in and out "
        "of your life. Basic ideas include: income, expenses, saving, debt, "
        "and investing. In this program we focus on budget and investing "
        "examples, but these skills connect in real life."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "Income is the money you receive. Expenses are the money you spend. "
        "The difference between the two is your cash flow. If you spend less "
        "than you make, the extra can go to savings or investing. If you "
        "spend more than you make, you may need to borrow, which can create "
        "debt."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "Saving means setting money aside in a safe place, often for short "
        "term goals or an emergency fund. Investing means using money to buy "
        "assets such as stocks or funds that can grow in value but also can "
        "go down. In this project we simulate stocks so you can see how "
        "values change over time."
    )
    input("\nEnd of lesson. Press Enter to return to the main menu...")


def lesson_budgeting(profile):
    print("\n========== Budgeting Lesson ==========")
    rec = profile.recommended_budget_percentages()
    wrap_print(
        "A basic way to budget is to split your monthly income between "
        "needs, wants, and savings or investing. Needs include rent, food, "
        "transportation and minimum debt payments. Wants are extras like "
        "eating out, streaming, and travel. Savings and investing is money "
        "set aside for future goals."
    )
    print()
    wrap_print(
        f"For your profile, an example split could be:\n"
        f"  Needs: {rec['Needs']} percent\n"
        f"  Wants: {rec['Wants']} percent\n"
        f"  Savings / Investing: {rec['Savings / Investing']} percent\n"
        "Again, this is only educational, not advice."
    )
    input("\nPress Enter to continue into the budget game...")


def budget_game(profile):
    lesson_budgeting(profile)
    print("\n========== Budget Game ==========")

    income = ask_float("Enter your monthly income (for example 2500): ", 1)

    rec = profile.recommended_budget_percentages()
    rec_needs = income * rec["Needs"] / 100
    rec_wants = income * rec["Wants"] / 100
    rec_savings = income * rec["Savings / Investing"] / 100

    print("\nNow you decide how to split your income.")
    needs = ask_float("How much per month for NEEDS: ", 0)
    wants = ask_float("How much per month for WANTS: ", 0)
    savings = ask_float("How much per month for SAVINGS / INVESTING: ", 0)

    total = needs + wants + savings
    print(f"\nYou allocated a total of ${total:.2f}.")
    if abs(total - income) > 0.01:
        wrap_print(
            "Your budget does not add up to your income. In real life, this "
            "would mean you either forgot a category or you are spending "
            "more than you earn."
        )
    else:
        wrap_print(
            "Nice, your budget adds up to your income. Now compare your "
            "choices to the example split."
        )

    print("\nExample split based on your profile:")
    print(f"  Needs: about ${rec_needs:.2f}")
    print(f"  Wants: about ${rec_wants:.2f}")
    print(f"  Savings / Investing: about ${rec_savings:.2f}")

    print("\nYour choices:")
    print(f"  Needs: ${needs:.2f}")
    print(f"  Wants: ${wants:.2f}")
    print(f"  Savings / Investing: ${savings:.2f}")

    input("\nEnd of budget game. Press Enter to return to main menu...")




def investment_simulation(profile):
    print("\n========== Investment Simulation ==========")
    wrap_print(
        "In this simulation you start with a simple mock portfolio and can "
        "buy and sell three example stocks. Prices move randomly each day "
        "so you can see risk and reward. This is only for learning, not "
        "real investment advice."
    )

    market = StockMarket()
    portfolio = Portfolio(starting_cash=10000.0)

    while True:
        print("\n----- Investment Menu -----")
        print("  1. View prices")
        print("  2. View portfolio")
        print("  3. Buy stock")
        print("  4. Sell stock")
        print("  5. Simulate next day")
        print("  6. View text price chart")
        print("  7. View matplotlib price chart")
        print("  8. Ask the Hint Bot")
        print("  9. Exit to main menu")

        choice = ask_int("Choose an option: ", 1, 9)

        if choice == 1:
            market.print_table()
        elif choice == 2:
            portfolio.pretty_print(market)
        elif choice == 3:
            market.print_table()
            ticker = input("Enter ticker to buy (SAFE, GROW, YOLO): ").strip().upper()
            if ticker not in market.prices:
                print("That ticker does not exist in this game.")
                continue
            amount = ask_int("How many shares do you want to buy: ", 1)
            price = market.prices[ticker]
            success, msg = portfolio.buy(ticker, price, amount)
            print(msg)
        elif choice == 4:
            portfolio.pretty_print(market)
            ticker = input("Enter ticker to sell (SAFE, GROW, YOLO): ").strip().upper()
            if ticker not in portfolio.holdings:
                print("You do not own that ticker.")
                continue
            amount = ask_int("How many shares do you want to sell: ", 1)
            price = market.prices.get(ticker, 0)
            success, msg = portfolio.sell(ticker, price, amount)
            print(msg)
        elif choice == 5:
            print("Simulating next market day...")
            market.simulate_day()
            market.print_table()
            time.sleep(0.7)
            print("\nYour portfolio after the day change:")
            portfolio.pretty_print(market)
        elif choice == 6:
            ticker = input("Enter ticker to chart (SAFE, GROW, YOLO): ").strip().upper()
            if ticker not in market.prices:
                print("That ticker does not exist.")
            else:
                market.print_ascii_chart(ticker)
        elif choice == 7:
            ticker = input("Enter ticker to chart (SAFE, GROW, YOLO): ").strip().upper()
            if ticker not in market.prices:
                print("That ticker does not exist.")
            else:
                market.plot_matplotlib_chart(ticker)
        elif choice == 8:
            advice_bot(profile, portfolio)
        elif choice == 9:
            print("Leaving investment simulation.")
            break




def simulate_account_growth(start_balance, monthly_contribution, annual_rate_percent, years):
    """
    Generic compound interest simulator.
    Monthly compounding with monthly contributions.
    """
    balance = start_balance
    monthly_rate = annual_rate_percent / 100.0 / 12.0
    months = int(years * 12)
    balances = [balance]
    for _ in range(months):
        balance = balance * (1 + monthly_rate) + monthly_contribution
        balances.append(balance)
    return balances


def plot_account_growth(balances, title, label):
    if not MATPLOTLIB_AVAILABLE:
        print("\nMatplotlib is not installed. Install it with:")
        print("  pip install matplotlib")
        return

    months = list(range(len(balances)))
    years = [m / 12.0 for m in months]

    plt.figure()
    plt.plot(years, balances)
    plt.title(title)
    plt.xlabel("Years")
    plt.ylabel(label)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def simple_savings_calculator():
    print("\n========== Simple Savings Growth ==========")
    start = ask_float("Starting balance: ", 0)
    monthly = ask_float("Monthly contribution: ", 0)
    rate = ask_float("Annual interest rate (percent): ", 0)
    years = ask_float("Number of years: ", 0.1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    interest_earned = final_balance - total_contrib

    print(f"\nAfter {years:.1f} years your balance could be about ${final_balance:,.2f}.")
    print(f"Total you put in: about ${total_contrib:,.2f}")
    print(f"Interest growth in this model: about ${interest_earned:,.2f}")
    print("\nThis is a simple compound interest model for learning, not a guarantee.")

    show_chart = input("Show chart of balance over time? (y/n): ").strip().lower()
    if show_chart == "y":
        plot_account_growth(balances, "Simple savings growth", "Balance")


def retirement_account_calculator():
    print("\n========== IRA / 401k / 403b Growth ==========")
    wrap_print(
        "This calculator models a retirement account like an IRA, 401k or 403b "
        "with regular monthly contributions and compound growth. Real accounts "
        "have taxes, fees and rules that are not included here."
    )

    start = ask_float("Starting balance in the account: ", 0)
    monthly = ask_float("Monthly contribution: ", 0)
    rate = ask_float("Expected average annual return (percent, for example 7): ", 0)
    years = ask_float("Number of years until retirement: ", 1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    growth = final_balance - total_contrib

    print(f"\nAfter about {years:.1f} years this model shows a balance of ${final_balance:,.2f}.")
    print(f"Total contributed: about ${total_contrib:,.2f}")
    print(f"Growth from returns in this model: about ${growth:,.2f}")
    print("\nThis is an educational model only and not tax or investment advice.")

    show_chart = input("Show chart of account balance over time? (y/n): ").strip().lower()
    if show_chart == "y":
        plot_account_growth(balances, "Retirement account growth", "Balance")


def savings_account_calculator():
    print("\n========== Savings Account Interest ==========")
    wrap_print(
        "This calculator models a bank savings account with a lower interest rate "
        "but lower risk. Real interest rates can change often."
    )

    start = ask_float("Starting balance: ", 0)
    monthly = ask_float("Monthly deposit: ", 0)
    rate = ask_float("Annual interest rate (percent, for example 2): ", 0)
    years = ask_float("Number of years: ", 0.1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    growth = final_balance - total_contrib

    print(f"\nAfter {years:.1f} years your savings could reach about ${final_balance:,.2f}.")
    print(f"Total deposited: about ${total_contrib:,.2f}")
    print(f"Interest gained in this model: about ${growth:,.2f}")

    show_chart = input("Show chart of savings balance over time? (y/n): ").strip().lower()
    if show_chart == "y":
        plot_account_growth(balances, "Savings account growth", "Balance")


def housing_loan_calculator():
    print("\n========== Housing Loan Interest Estimate ==========")
    wrap_print(
        "This calculator estimates a fixed rate mortgage payment and shows "
        "how much could go to interest over the life of the loan. It is a "
        "simplified model for learning."
    )

    home_price = ask_float("Home price: ", 0.01)
    down_payment = ask_float("Down payment amount: ", 0)
    rate = ask_float("Annual interest rate (percent, for example 6.5): ", 0)
    years = ask_int("Loan term in years (for example 30): ", 1)

    loan_amount = home_price - down_payment
    if loan_amount <= 0:
        print("Your down payment covers the full price in this model. No loan needed.")
        return

    monthly_rate = rate / 100.0 / 12.0
    n_payments = years * 12

    if monthly_rate == 0:
        monthly_payment = loan_amount / n_payments
    else:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** n_payments) / (
            (1 + monthly_rate) ** n_payments - 1
        )

    total_paid = monthly_payment * n_payments
    total_interest = total_paid - loan_amount

    print(f"\nApproximate monthly payment: ${monthly_payment:,.2f}")
    print(f"Total paid over {years} years: about ${total_paid:,.2f}")
    print(f"Total interest in this model: about ${total_interest:,.2f}")

    show_chart = input("Show chart of remaining balance over time? (y/n): ").strip().lower()
    if show_chart == "y":
        if not MATPLOTLIB_AVAILABLE:
            print("\nMatplotlib is not installed. Install it with:")
            print("  pip install matplotlib")
            return

        balances = []
        balance = loan_amount
        for _ in range(n_payments):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal
            balances.append(max(balance, 0))

        months = list(range(len(balances)))
        years_axis = [m / 12.0 for m in months]

        plt.figure()
        plt.plot(years_axis, balances)
        plt.title("Estimated remaining mortgage balance")
        plt.xlabel("Years")
        plt.ylabel("Balance")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def interest_calculators_menu():
    """
    Menu that links all the interest and account calculators.
    """
    while True:
        print("\n========== Interest Calculators ==========")
        print("  1. Simple savings growth")
        print("  2. IRA / 401k / 403b growth")
        print("  3. Savings account interest")
        print("  4. Housing loan interest estimate")
        print("  5. Return to main menu")

        choice = ask_int("Choose an option: ", 1, 5)

        if choice == 1:
            simple_savings_calculator()
        elif choice == 2:
            retirement_account_calculator()
        elif choice == 3:
            savings_account_calculator()
        elif choice == 4:
            housing_loan_calculator()
        elif choice == 5:
            break


# ============= MAIN PROGRAM =============

def create_user_profile():
    print("\n========== Welcome to the Finance Simulator ==========")
    name = input("First, what is your name? ").strip() or "Player"
    age = ask_int("Enter your age: ", 10, 120)

    occupations = [
        "Student",
        "Part-time worker",
        "Full-time worker",
        "Self-employed",
        "Other"
    ]
    occupation = ask_choice("\nChoose your current situation:", occupations)

    marital = ask_choice(
        "\nChoose your marital status:",
        ["Single", "In a relationship", "Married", "Prefer not to say"]
    )

    print("\nWhat is your main financial goal right now?")
    print("Examples: pay off debt, save for a house, build emergency fund, retire early")
    goal = input("Type your goal: ").strip() or "Learn about money"

    profile = UserProfile(name, age, occupation, marital, goal)
    print(profile.summary())
    input("Press Enter to continue to the main menu...")
    return profile


def main_menu(profile):
    while True:
        print("\n========== Main Menu ==========")
        print("  1. Learn financial literacy")
        print("  2. Learn and play the budget game")
        print("  3. Investment simulation")
        print("  4. Ask the Hint Bot directly")
        print("  5. Interest calculators")
        print("  6. Quit")

        choice = ask_int("Choose an option: ", 1, 6)

        if choice == 1:
            lesson_financial_literacy()
        elif choice == 2:
            budget_game(profile)
        elif choice == 3:
            investment_simulation(profile)
        elif choice == 4:
            advice_bot(profile)
        elif choice == 5:
            interest_calculators_menu()
        elif choice == 6:
            print("\nThank you for using the Finance Simulator. Goodbye!")
            break


def main():
    profile = create_user_profile()
    main_menu(profile)


if __name__ == "__main__":
    main()
