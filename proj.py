import random
import textwrap
import time
import json
import os


SAVE_FILE = "finance_save.json"
SAVINGS_INTEREST_RATE_PER_ROUND = 0.002 / 100.0  # 0.002 percent per round


ACHIEVEMENTS_INFO = {
    "FIRST_BUDGET_GAME": "Played the budget game for the first time.",
    "FIRST_GOAL_REACHED": "Reached a savings goal in the budget game.",
    "FAST_SAVER": "Reached a savings goal in three rounds or fewer.",
    "PERSISTENT_SAVER": "Played ten or more budget rounds in one game.",
    "CHECKING_NEGATIVE": "Let checking go below zero.",
    "SUPER_SAVER": "Reached ten thousand or more in savings.",
    "INVEST_ONCE": "Bought your first stock.",
    "DIVERSIFIED": "Owned at least one stock in each sector.",
    "TRADE_MASTER": "Completed ten trades.",
    "GREEN_DAY": "Had a day where your portfolio grew in value.",
    "RED_DAY": "Had a day where your portfolio lost value.",
    "SIDE_HUSTLE_START": "Started your first side hustle game.",
    "SIDE_HUSTLE_PRO": "Reached the top side hustle reputation level.",
    "HUSTLE_RICH": "Earned one thousand or more from side hustles.",
    "LITERACY_LEARNER": "Completed the financial literacy lesson once.",
    "CALC_USER": "Used any interest calculator.",
    "RETIRE_PLANNER": "Used the retirement account calculator.",
    "HOME_DREAMER": "Used the housing loan calculator.",
    "ASK_FINNY": "Asked Finny the Finance Fox for help.",
    "LONG_TERM_PLAYER": "Opened the game five times.",
    "DATA_NERD": "Visited the Data Center.",
    "BALANCED_LIFE": "Reached a savings goal while checking stayed non negative.",
    "LOW_SPENDER": "Chose to save at least fifty percent of income.",
    "ALL_ROUNDER": "Unlocked ten or more achievements.",
}


def wrap_print(text):
    print(textwrap.fill(text, width=80))


class GameData:
    def __init__(self):
        self.stats = {
            "launch_count": 0,
            "budget_sessions": 0,
            "budget_rounds": 0,
            "budget_goals_reached": 0,
            "investment_sessions": 0,
            "investment_days": 0,
            "trades_made": 0,
            "side_hustle_sessions": 0,
            "side_hustle_total_earned": 0.0,
            "side_hustle_best_week": 0.0,
            "financial_lessons_viewed": 0,
            "calculator_uses": 0,
            "retirement_calcs": 0,
            "home_calcs": 0,
            "finny_questions": 0,
            "data_center_visits": 0,
        }
        self.achievements = {code: False for code in ACHIEVEMENTS_INFO}
        self.history = []  # list of strings
        self.profile_dict = None  # saved profile data

    def log(self, text):
        self.history.append(text)
        if len(self.history) > 40:
            self.history.pop(0)

    def unlock(self, code):
        if code not in self.achievements:
            return
        if not self.achievements[code]:
            self.achievements[code] = True
            desc = ACHIEVEMENTS_INFO[code]
            print(f"\nFinny: Achievement unlocked - {desc}")
            unlocked_count = sum(1 for v in self.achievements.values() if v)
            if unlocked_count >= 10 and not self.achievements["ALL_ROUNDER"]:
                self.achievements["ALL_ROUNDER"] = True
                print(
                    "\nFinny: Achievement unlocked - "
                    "All Rounder (ten achievements reached)."
                )

    def to_dict(self):
        return {
            "stats": self.stats,
            "achievements": self.achievements,
            "history": self.history,
            "profile_dict": self.profile_dict,
        }

    @classmethod
    def from_dict(cls, data):
        g = cls()
        g.stats.update(data.get("stats", {}))
        ach = data.get("achievements", {})
        for code in g.achievements:
            if code in ach:
                g.achievements[code] = bool(ach[code])
        g.history = data.get("history", [])
        g.profile_dict = data.get("profile_dict")
        return g

    def save(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Finny: I could not save the game data because: {e}")


def load_game_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return GameData.from_dict(data)
        except Exception:
            return GameData()
    else:
        return GameData()


class UserProfile:
    def __init__(self, name, age, occupation, marital_status, goal,
                 job_title=None, monthly_income=None):
        self.name = name
        self.age = age
        self.occupation = occupation
        self.marital_status = marital_status
        self.goal = goal
        self.job_title = job_title
        self.monthly_income = monthly_income

    def summary(self):
        base = (
            f"\nProfile for {self.name}:\n"
            f"  Age: {self.age}\n"
            f"  Occupation: {self.occupation}\n"
            f"  Marital status: {self.marital_status}\n"
            f"  Financial goal: {self.goal}\n"
        )
        if self.job_title and self.monthly_income is not None:
            base += (
                f"  Game job: {self.job_title}, "
                f"monthly income: ${self.monthly_income:.2f}\n"
            )
        return base

    def recommended_budget_percentages(self):
        base = {
            "Needs": 50,
            "Wants": 30,
            "Savings / Investing": 20,
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

    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "occupation": self.occupation,
            "marital_status": self.marital_status,
            "goal": self.goal,
            "job_title": self.job_title,
            "monthly_income": self.monthly_income,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data.get("name", "Player"),
            data.get("age", 18),
            data.get("occupation", "Student"),
            data.get("marital_status", "Single"),
            data.get("goal", "Learn about money"),
            data.get("job_title"),
            data.get("monthly_income"),
        )


class Portfolio:
    def __init__(self, starting_cash=10000.0):
        self.cash = float(starting_cash)
        self.holdings = {}

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
                category = market.stock_info[ticker]["category"]
                print(
                    f"  {ticker} ({category}): {shares} shares "
                    f"at ${price:.2f} (value ${position_value:.2f})"
                )
        print(f"  Total value: ${self.total_value(market):.2f}")


class StockMarket:
    def __init__(self):
        self.stock_info = {
            "TCH1": {"category": "Tech", "base": 120.0, "vol": "med"},
            "TCH2": {"category": "Tech", "base": 80.0, "vol": "high"},
            "TCH3": {"category": "Tech", "base": 50.0, "vol": "med"},
            "HLT1": {"category": "Healthcare", "base": 90.0, "vol": "low"},
            "HLT2": {"category": "Healthcare", "base": 60.0, "vol": "med"},
            "HLT3": {"category": "Healthcare", "base": 40.0, "vol": "med"},
            "CSM1": {"category": "Consumer", "base": 70.0, "vol": "low"},
            "CSM2": {"category": "Consumer", "base": 30.0, "vol": "high"},
            "CSM3": {"category": "Consumer", "base": 45.0, "vol": "med"},
        }

        self.prices = {
            ticker: info["base"] for ticker, info in self.stock_info.items()
        }
        self.history = {
            ticker: [price] for ticker, price in self.prices.items()
        }
        self.day = 0

    def simulate_day(self):
        self.day += 1
        for ticker, info in self.stock_info.items():
            current = self.prices[ticker]
            vol = info["vol"]

            if vol == "low":
                change_percent = random.uniform(-0.01, 0.01)
            elif vol == "med":
                change_percent = random.uniform(-0.03, 0.03)
            else:
                change_percent = random.uniform(-0.07, 0.07)

            new_price = current * (1 + change_percent)
            new_price = max(new_price, 1.0)
            self.prices[ticker] = new_price
            self.history[ticker].append(new_price)

    def print_table(self):
        print(f"\nDay {self.day} prices:")
        categories = {}
        for ticker, price in self.prices.items():
            cat = self.stock_info[ticker]["category"]
            categories.setdefault(cat, []).append((ticker, price))

        for cat, items in categories.items():
            print(f"  Category: {cat}")
            for ticker, price in items:
                print(f"    {ticker}: ${price:.2f}")

    def print_ascii_chart(self, ticker, last_n=15):
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
            print(
                f"  Day {self.day - len(prices) + 1 + i:>3}: "
                f"{bar} ${p:6.2f}"
            )


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
    while True:
        print(prompt)
        for i, opt in enumerate(options, start=1):
            print(f"  {i}. {opt}")
        choice = ask_int("Enter a number: ", 1, len(options))
        return options[choice - 1]


def advice_bot(profile, portfolio, game_data):
    game_data.stats["finny_questions"] += 1
    if game_data.stats["finny_questions"] == 1:
        game_data.unlock("ASK_FINNY")

    wrap_print(
        "\nFinny the Finance Fox: I am your money sidekick. Ask me simple "
        "questions about budgeting, debt, credit or investing.\nType "
        "'back' to return to the main menu."
    )

    while True:
        question = input("\nYour question: ").strip()
        if question.lower() in ("back", "exit", "quit"):
            print("Finny: Got it, heading back to the main menu.")
            break

        q_low = question.lower()

        if "budget" in q_low or "spend" in q_low:
            rec = profile.recommended_budget_percentages()
            wrap_print(
                f"Finny: One simple idea is to split income into needs, wants "
                f"and savings.\nFor you, one possible split is "
                f"{rec['Needs']} percent needs, {rec['Wants']} percent wants "
                f"and {rec['Savings / Investing']} percent savings or "
                f"investing. This is for learning, not advice."
            )
        elif "invest" in q_low or "stock" in q_low:
            wrap_print(
                "Finny: Investing is about risk and time. In this game you can "
                "buy Tech, Healthcare and Consumer stocks. Spreading your "
                "money across sectors is usually less risky than putting "
                "everything into one stock."
            )
        elif "debt" in q_low or "loans" in q_low:
            wrap_print(
                "Finny: With debt, a common idea is to pay minimums on "
                "everything and then focus extra payments on the highest "
                "interest debt. Here that is just a learning rule, not "
                "personal advice."
            )
        elif "credit" in q_low:
            wrap_print(
                "Finny: Credit lets you borrow now and repay later. Paying on "
                "time and keeping balances lower are simple habits that can "
                "protect your credit history over time."
            )
        else:
            wrap_print(
                "Finny: I do not have a specific answer for that. Try asking "
                "about budgeting, investing, debt or credit."
            )

        if portfolio is not None:
            wrap_print(
                f"\nFinny: In this investment game your cash is currently "
                f"${portfolio.cash:.2f}."
            )


def job_quiz():
    wrap_print(
        "\nFinny: Before we start, let us figure out your role in this money "
        "simulation. Answer these questions and I will match you to a job."
    )

    categories = {
        "helper": 0,
        "people": 0,
        "analytical": 0,
        "action": 0,
    }

    ans = ask_choice(
        "\nQuestion 1: Which sounds the most fun?",
        [
            "Helping people one on one",
            "Talking to groups or teaching",
            "Solving puzzles or analyzing numbers",
            "Being active and out in the field",
        ],
    )
    if ans.startswith("Helping"):
        categories["helper"] += 1
    elif ans.startswith("Talking"):
        categories["people"] += 1
    elif ans.startswith("Solving"):
        categories["analytical"] += 1
    else:
        categories["action"] += 1

    ans = ask_choice(
        "\nQuestion 2: How do you feel about stress?",
        [
            "I can handle serious pressure if it matters",
            "I like steady, predictable work",
            "I enjoy fast paced and changing situations",
            "I prefer working alone at my own speed",
        ],
    )
    if "serious pressure" in ans:
        categories["helper"] += 1
    elif "steady" in ans:
        categories["people"] += 1
    elif "fast paced" in ans:
        categories["action"] += 1
    else:
        categories["analytical"] += 1

    ans = ask_choice(
        "\nQuestion 3: Pick a class you would enjoy the most.",
        [
            "Biology or health science",
            "Psychology or communication",
            "Computer science or math",
            "Criminal justice or sports training",
        ],
    )
    if "Biology" in ans:
        categories["helper"] += 1
    elif "Psychology" in ans:
        categories["people"] += 1
    elif "Computer science" in ans:
        categories["analytical"] += 1
    else:
        categories["action"] += 1

    ans = ask_choice(
        "\nQuestion 4: What is most important to you at work?",
        [
            "Making a direct difference in health or safety",
            "Helping people learn or feel supported",
            "Building or fixing systems and tools",
            "Protecting the community or responding to emergencies",
        ],
    )
    if "health or safety" in ans:
        categories["helper"] += 1
    elif "learn or feel supported" in ans:
        categories["people"] += 1
    elif "systems and tools" in ans:
        categories["analytical"] += 1
    else:
        categories["action"] += 1

    best_cat = max(categories, key=categories.get)

    if best_cat == "helper":
        job_title = "Doctor"
        monthly_income = 8000.0
    elif best_cat == "people":
        job_title = "Teacher"
        monthly_income = 3500.0
    elif best_cat == "analytical":
        job_title = "Software Developer"
        monthly_income = 5000.0
    else:
        job_title = "Police Officer"
        monthly_income = 3800.0

    wrap_print(
        f"\nFinny: Based on your answers, your game job is: {job_title}.\n"
        f"In this simulation you will earn about ${monthly_income:.2f} per "
        f"round of the budget game."
    )

    return job_title, monthly_income


def lesson_financial_literacy(game_data):
    print("\n========== Financial Literacy Lesson ==========")
    game_data.stats["financial_lessons_viewed"] += 1
    if game_data.stats["financial_lessons_viewed"] == 1:
        game_data.unlock("LITERACY_LEARNER")

    wrap_print(
        "Financial literacy means understanding how money flows in and out "
        "of your life. Basic ideas include income, expenses, saving, debt "
        "and investing. In this program we focus on budget, saving and "
        "investing examples, but all of these connect."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "Income is the money you receive. Expenses are the money you spend. "
        "If you spend less than you earn, the extra can go to savings or "
        "investing. If you spend more than you earn, you may need to borrow, "
        "which can create debt."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "An emergency fund is money set aside for surprise costs, such as "
        "car repairs or medical bills. Even a small emergency fund can "
        "reduce stress when something goes wrong."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "Credit lets you borrow now and repay later. It can be helpful, but "
        "high interest debt can grow quickly. Paying bills on time and "
        "keeping balances lower are basic habits that can protect your "
        "credit history."
    )
    input("\nPress Enter to continue...")

    wrap_print(
        "Investing means buying assets that can grow but can also lose "
        "value. Spreading your money across different investments, called "
        "diversification, helps reduce the impact of any single investment "
        "going badly."
    )
    input("\nEnd of lesson. Press Enter to return to the main menu...")


def lesson_budgeting(profile):
    print("\n========== Budgeting Lesson ==========")
    rec = profile.recommended_budget_percentages()
    wrap_print(
        "One simple way to budget is to split your monthly income between "
        "needs, wants and savings or investing.\nNeeds include rent, food, "
        "transportation and minimum debt payments.\nWants are extras like "
        "eating out, streaming and travel.\nSavings and investing is money "
        "set aside for future goals."
    )
    print()
    wrap_print(
        f"For your profile, an example split could be:\n"
        f"  Needs: {rec['Needs']} percent\n"
        f"  Wants: {rec['Wants']} percent\n"
        f"  Savings / Investing: {rec['Savings / Investing']} percent\n"
        "This is only educational, not financial advice."
    )
    input("\nPress Enter to continue into the budget game...")


def random_budget_event():
    events = [
        ("Your friend’s dog got sick while you were pet sitting. "
         "Emergency vet visit.", -500),
        ("You found money in an old coat pocket.", 20),
        ("Flat tire on the way to work. You had to replace it.", -120),
        ("You won a small prize in a local contest.", 50),
        ("You forgot to cancel a subscription and got charged.", -15),
        ("You sold an old video game console.", 100),
        ("You had to pay a parking ticket.", -80),
        ("You did a small freelance job for a neighbor.", 75),
    ]
    return random.choice(events)


def budget_simulation_game(profile, game_data):
    def life_goals_shop(goals, savings):
        """Allow the player to spend savings on life milestones."""
        while True:
            print("\n========== Life Goals Shop ==========")
            print("You can spend savings on big milestones just for fun in the game.")
            print("Each goal reduces your savings but gives you a milestone checked off.\n")

            for i, g in enumerate(goals, start=1):
                status = "BOUGHT" if g["bought"] else "available"
                print(f"  {i}. {g['name']} – cost ${g['cost']:.2f} – {status}")
            print("  0. Go back to budget round")

            choice = ask_int("Pick a goal number to buy or zero to go back: ", 0, len(goals))
            if choice == 0:
                return savings

            goal = goals[choice - 1]
            if goal["bought"]:
                print("You already purchased this milestone in the game.")
                continue
            if savings < goal["cost"]:
                print("You do not have enough in savings for that yet.")
                continue

            confirm = input(
                f"Spend ${goal['cost']:.2f} from savings to buy '{goal['name']}'? (y/n): "
            ).strip().lower()
            if confirm == "y":
                savings -= goal["cost"]
                goal["bought"] = True
                print(f"You bought the milestone: {goal['name']}!")
            else:
                print("No purchase made.")
        return savings

    lesson_budgeting(profile)
    print("\n========== Budget Simulation Game ==========")

    game_data.stats["budget_sessions"] += 1
    if game_data.stats["budget_sessions"] == 1:
        game_data.unlock("FIRST_BUDGET_GAME")

    if profile.monthly_income is None:
        base_income = ask_float(
            "Enter your monthly income for this game (for example 2500): ", 1
        )
    else:
        base_income = profile.monthly_income
        print(f"\nFinny: Using your game job income: ${base_income:.2f} per round.")

    savings_goal = ask_float(
        "\nEnter a savings goal for this game (for example 5000): ", 1
    )

    print("\nNow choose how much of your income you want to save each round.")
    save_percent = ask_float(
        "Percent of income to send to savings (0 to 80 recommended): ",
        0,
        100,
    )
    if save_percent >= 50:
        game_data.unlock("LOW_SPENDER")

    checking = 0.0
    savings = 0.0
    rounds = 0
    goal_reached = False

    life_goals = [
        {"name": "Start emergency fund", "cost": 1000.0, "bought": False},
        {"name": "Deposit for apartment", "cost": 3000.0, "bought": False},
        {"name": "Used starter car", "cost": 5000.0, "bought": False},
        {"name": "Dream vacation", "cost": 2000.0, "bought": False},
        {"name": "First house down payment", "cost": 20000.0, "bought": False},
    ]

    wrap_print(
        "\nFinny: Each round is about one month. Income arrives, a slice goes "
        "to savings, savings earns a small interest amount and then a random "
        "life event hits your money. You can also visit the Life Goals shop "
        "to spend savings on milestones like an emergency fund, car or house."
    )

    running = True
    while running:
        rounds += 1
        game_data.stats["budget_rounds"] += 1
        print(f"\n----- Budget Round {rounds} -----")

        income = base_income
        savings_contribution = income * (save_percent / 100.0)
        checking_contribution = income - savings_contribution

        checking += checking_contribution
        savings += savings_contribution

        print(f"Income this round: ${income:.2f}")
        print(f"  To checking: ${checking_contribution:.2f}")
        print(f"  To savings:  ${savings_contribution:.2f}")

        interest = savings * SAVINGS_INTEREST_RATE_PER_ROUND
        savings += interest
        print(f"Savings interest at 0.002 percent: ${interest:.4f}")

        desc, change = random_budget_event()
        print(f"\nRandom event: {desc}")
        if change < 0:
            print(f"  This cost you ${-change:.2f}.")
        else:
            print(f"  You gained ${change:.2f}.")
        checking += change

        if checking < 0:
            game_data.unlock("CHECKING_NEGATIVE")

        print("\nBalances before extra choices:")
        print(f"  Checking: ${checking:.2f}")
        print(f"  Savings:  ${savings:.2f}")
        print(f"  Savings goal: ${savings_goal:.2f}")

        move_choice = input(
            "Move money between checking and savings this round? (y/n): "
        ).strip().lower()
        if move_choice == "y":
            direction = ask_choice(
                "Choose transfer direction:",
                [
                    "Move from checking to savings",
                    "Move from savings to checking",
                    "Skip transfer",
                ],
            )
            if direction.startswith("Move from checking"):
                amount = ask_float("Amount to move to savings: ", 0)
                if amount > checking:
                    print("You do not have that much in checking.")
                else:
                    checking -= amount
                    savings += amount
                    print(f"Moved ${amount:.2f} from checking to savings.")
            elif direction.startswith("Move from savings"):
                amount = ask_float("Amount to move to checking: ", 0)
                if amount > savings:
                    print("You do not have that much in savings.")
                else:
                    savings -= amount
                    checking += amount
                    print(f"Moved ${amount:.2f} from savings to checking.")
            else:
                print("No transfer this round.")

        round_active = True
        while round_active:
            print("\nRound actions:")
            print("  1. Go to next month")
            print("  2. Visit Life Goals shop")
            print("  3. Adjust savings percentage")
            print("  4. End budget game")

            action = ask_int("Choose an action: ", 1, 4)

            if action == 1:
                round_active = False
            elif action == 2:
                savings = life_goals_shop(life_goals, savings)
                print(f"\nUpdated savings after shop: ${savings:.2f}")
            elif action == 3:
                new_percent = ask_float(
                    "Enter new percent of income to save each month: ", 0, 100
                )
                save_percent = new_percent
                print(f"Savings percent updated to {save_percent:.1f}.")
                if save_percent >= 50:
                    game_data.unlock("LOW_SPENDER")
            elif action == 4:
                wrap_print(
                    "\nFinny: Ending the budget simulation for now. You can "
                    "come back later with the same profile."
                )
                game_data.log(
                    f"Stopped budget game after {rounds} rounds with "
                    f"savings ${savings:.2f}."
                )
                running = False
                round_active = False

        print("\nBalances at end of round:")
        print(f"  Checking: ${checking:.2f}")
        print(f"  Savings:  ${savings:.2f}")
        progress = min(1.0, savings / savings_goal) if savings_goal > 0 else 0
        print(f"  Goal progress: {progress * 100:.1f} percent")

        if savings >= 10000:
            game_data.unlock("SUPER_SAVER")

        if (not goal_reached) and savings >= savings_goal:
            goal_reached = True
            game_data.stats["budget_goals_reached"] += 1
            game_data.unlock("FIRST_GOAL_REACHED")
            if rounds <= 3:
                game_data.unlock("FAST_SAVER")
            if checking >= 0:
                game_data.unlock("BALANCED_LIFE")
            if rounds >= 10:
                game_data.unlock("PERSISTENT_SAVER")

            wrap_print(
                f"\nFinny: Nice work. You hit your savings goal of "
                f"${savings_goal:.2f} in {rounds} rounds."
            )
            game_data.log(
                f"Reached savings goal of ${savings_goal:.2f} in {rounds} rounds."
            )

            keep_playing = input(
                "Do you want to keep playing this budget game to buy life "
                "milestones? (y/n): "
            ).strip().lower()
            if keep_playing != "y":
                running = False

        if not running:
            break


def investment_simulation(profile, game_data):
    print("\n========== Investment Simulation ==========")
    wrap_print(
        "In this simulation you start with a mock portfolio and can buy and "
        "sell nine example stocks in three sectors: Tech, Healthcare and "
        "Consumer. Prices move randomly each day. Each market day you also "
        "receive new cash flow to invest, similar to adding money from a "
        "paycheck. This is for learning only, not real investment advice."
    )

    market = StockMarket()
    portfolio = Portfolio(starting_cash=10000.0)
    CASH_FLOW_PER_DAY = 1000.0

    game_data.stats["investment_sessions"] += 1
    game_data.log("Started an investment simulation session.")

    while True:
        print("\n----- Investment Menu -----")
        print("  1. View prices by sector")
        print("  2. View portfolio")
        print("  3. Buy stock")
        print("  4. Sell stock")
        print("  5. Simulate next day with new cash flow")
        print("  6. View text price chart for a stock")
        print("  7. Ask Finny for help")
        print("  8. Exit to main menu")

        choice = ask_int("Choose an option: ", 1, 8)

        if choice == 1:
            market.print_table()

        elif choice == 2:
            portfolio.pretty_print(market)

        elif choice == 3:
            market.print_table()
            ticker = input(
                "Enter ticker to buy (for example TCH1, HLT2, CSM3): "
            ).strip().upper()
            if ticker not in market.prices:
                print("That ticker does not exist in this game.")
                continue
            amount = ask_int("How many shares do you want to buy: ", 1)
            price = market.prices[ticker]
            success, msg = portfolio.buy(ticker, price, amount)
            print(msg)
            if success:
                game_data.stats["trades_made"] += 1
                if game_data.stats["trades_made"] == 1:
                    game_data.unlock("INVEST_ONCE")
                if game_data.stats["trades_made"] >= 10:
                    game_data.unlock("TRADE_MASTER")

        elif choice == 4:
            portfolio.pretty_print(market)
            ticker = input("Enter ticker to sell: ").strip().upper()
            if ticker not in portfolio.holdings:
                print("You do not own that ticker.")
                continue
            amount = ask_int("How many shares do you want to sell: ", 1)
            price = market.prices.get(ticker, 0)
            success, msg = portfolio.sell(ticker, price, amount)
            print(msg)
            if success:
                game_data.stats["trades_made"] += 1
                if game_data.stats["trades_made"] == 1:
                    game_data.unlock("INVEST_ONCE")
                if game_data.stats["trades_made"] >= 10:
                    game_data.unlock("TRADE_MASTER")

        elif choice == 5:
            portfolio.cash += CASH_FLOW_PER_DAY
            print(
                f"\nFinny: New cash flow added for this round: "
                f"${CASH_FLOW_PER_DAY:.2f}. You can invest this over time."
            )

            before = portfolio.total_value(market)

            print("Simulating next market day...")
            market.simulate_day()
            market.print_table()
            time.sleep(0.7)

            after = portfolio.total_value(market)
            game_data.stats["investment_days"] += 1

            print("\nYour portfolio after the day change:")
            portfolio.pretty_print(market)

            if after > before:
                game_data.unlock("GREEN_DAY")
            elif after < before:
                game_data.unlock("RED_DAY")

            game_data.log(
                f"After market day {market.day} portfolio value is ${after:.2f} "
                f"with daily cash flow of ${CASH_FLOW_PER_DAY:.2f} added."
            )

        elif choice == 6:
            ticker = input(
                "Enter ticker to chart (for example TCH1, HLT2, CSM3): "
            ).strip().upper()
            if ticker not in market.prices:
                print("That ticker does not exist.")
            else:
                market.print_ascii_chart(ticker)

        elif choice == 7:
            advice_bot(profile, portfolio, game_data)

        elif choice == 8:
            categories_owned = set()
            for ticker in portfolio.holdings:
                if portfolio.holdings[ticker] > 0:
                    cat = market.stock_info[ticker]["category"]
                    categories_owned.add(cat)
            if len(categories_owned) >= 3:
                game_data.unlock("DIVERSIFIED")

            game_data.log(
                f"Ended investment simulation with portfolio value "
                f"${portfolio.total_value(market):.2f}."
            )
            print("Leaving investment simulation.")
            break


def simulate_account_growth(start_balance, monthly_contribution,
                            annual_rate_percent, years):
    balance = start_balance
    monthly_rate = annual_rate_percent / 100.0 / 12.0
    months = int(years * 12)
    balances = [balance]
    for _ in range(months):
        balance = balance * (1 + monthly_rate) + monthly_contribution
        balances.append(balance)
    return balances


def ascii_growth_chart(balances, title):
    print(f"\n{title}")
    if not balances:
        print("No data to show.")
        return

    years_count = max(1, len(balances) // 12)
    data_points = []
    for y in range(years_count + 1):
        index = min(y * 12, len(balances) - 1)
        data_points.append((y, balances[index]))

    max_balance = max(b for _, b in data_points)
    min_balance = min(b for _, b in data_points)
    span = max_balance - min_balance if max_balance != min_balance else 1

    for year, bal in data_points:
        normalized = int((bal - min_balance) / span * 40)
        bar = "#" * max(1, normalized)
        print(f"  Year {year:>2}: {bar} ${bal:,.2f}")


def simple_savings_calculator(game_data):
    print("\n========== Simple Savings Growth ==========")
    game_data.stats["calculator_uses"] += 1
    if game_data.stats["calculator_uses"] == 1:
        game_data.unlock("CALC_USER")

    start = ask_float("Starting balance: ", 0)
    monthly = ask_float("Monthly contribution: ", 0)
    rate = ask_float("Annual interest rate (percent): ", 0)
    years = ask_float("Number of years: ", 0.1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    interest_earned = final_balance - total_contrib

    print(
        f"\nAfter {years:.1f} years your balance could be about "
        f"${final_balance:,.2f}."
    )
    print(f"Total you put in: about ${total_contrib:,.2f}")
    print(
        f"Interest growth in this model: about ${interest_earned:,.2f}\n"
        "This is a simple compound interest model for learning, not a "
        "guarantee."
    )

    show_chart = input(
        "Show text chart of balance over time? (y/n): "
    ).strip().lower()
    if show_chart == "y":
        ascii_growth_chart(balances, "Simple savings growth")
    game_data.log("Used simple savings calculator.")


def retirement_account_calculator(game_data):
    print("\n========== IRA / 401k / 403b Growth ==========")
    game_data.stats["calculator_uses"] += 1
    game_data.stats["retirement_calcs"] += 1
    if game_data.stats["calculator_uses"] == 1:
        game_data.unlock("CALC_USER")
    if game_data.stats["retirement_calcs"] == 1:
        game_data.unlock("RETIRE_PLANNER")

    wrap_print(
        "This calculator models a retirement account like an IRA, 401k or "
        "403b with regular monthly contributions and compound growth. Real "
        "accounts have taxes, fees and rules that are not included here."
    )

    start = ask_float("Starting balance in the account: ", 0)
    monthly = ask_float("Monthly contribution: ", 0)
    rate = ask_float(
        "Expected average annual return (percent, for example 7): ", 0
    )
    years = ask_float("Number of years until retirement: ", 1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    growth = final_balance - total_contrib

    print(
        f"\nAfter about {years:.1f} years this model shows a balance of "
        f"${final_balance:,.2f}."
    )
    print(f"Total contributed: about ${total_contrib:,.2f}")
    print(f"Growth from returns in this model: about ${growth:,.2f}")
    print(
        "\nThis is an educational model only and not tax or investment "
        "advice."
    )

    show_chart = input(
        "Show text chart of account balance over time? (y/n): "
    ).strip().lower()
    if show_chart == "y":
        ascii_growth_chart(balances, "Retirement account growth")
    game_data.log("Used retirement account calculator.")


def savings_account_calculator(game_data):
    print("\n========== Savings Account Interest ==========")
    game_data.stats["calculator_uses"] += 1
    if game_data.stats["calculator_uses"] == 1:
        game_data.unlock("CALC_USER")

    wrap_print(
        "This calculator models a bank savings account with a lower interest "
        "rate but lower risk. Real interest rates can change over time."
    )

    start = ask_float("Starting balance: ", 0)
    monthly = ask_float("Monthly deposit: ", 0)
    rate = ask_float("Annual interest rate (percent, for example 2): ", 0)
    years = ask_float("Number of years: ", 0.1)

    balances = simulate_account_growth(start, monthly, rate, years)
    final_balance = balances[-1]
    total_contrib = start + monthly * int(years * 12)
    growth = final_balance - total_contrib

    print(
        f"\nAfter {years:.1f} years your savings could reach about "
        f"${final_balance:,.2f}."
    )
    print(f"Total deposited: about ${total_contrib:,.2f}")
    print(f"Interest gained in this model: about ${growth:,.2f}")

    show_chart = input(
        "Show text chart of savings balance over time? (y/n): "
    ).strip().lower()
    if show_chart == "y":
        ascii_growth_chart(balances, "Savings account growth")
    game_data.log("Used savings account calculator.")


def housing_loan_calculator(game_data):
    print("\n========== Housing Loan Interest Estimate ==========")
    game_data.stats["calculator_uses"] += 1
    game_data.stats["home_calcs"] += 1
    if game_data.stats["calculator_uses"] == 1:
        game_data.unlock("CALC_USER")
    if game_data.stats["home_calcs"] == 1:
        game_data.unlock("HOME_DREAMER")

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
        print("Your down payment covers the full price in this model.")
        return

    monthly_rate = rate / 100.0 / 12.0
    n_payments = years * 12

    if monthly_rate == 0:
        monthly_payment = loan_amount / n_payments
    else:
        monthly_payment = loan_amount * (
            monthly_rate * (1 + monthly_rate) ** n_payments
        ) / ((1 + monthly_rate) ** n_payments - 1)

    total_paid = monthly_payment * n_payments
    total_interest = total_paid - loan_amount

    print(f"\nApproximate monthly payment: ${monthly_payment:,.2f}")
    print(f"Total paid over {years} years: about ${total_paid:,.2f}")
    print(f"Total interest in this model: about ${total_interest:,.2f}")

    show_chart = input(
        "Show text chart of remaining balance over time? (y/n): "
    ).strip().lower()
    if show_chart == "y":
        balances = []
        balance = loan_amount
        for _ in range(n_payments):
            interest = balance * monthly_rate
            principal = monthly_payment - interest
            balance -= principal
            balances.append(max(balance, 0))
        ascii_growth_chart(balances, "Estimated remaining mortgage balance")
    game_data.log("Used housing loan calculator.")


def interest_calculators_menu(game_data):
    while True:
        print("\n========== Interest Calculators ==========")
        print("  1. Simple savings growth")
        print("  2. IRA / 401k / 403b growth")
        print("  3. Savings account interest")
        print("  4. Housing loan interest estimate")
        print("  5. Return to main menu")

        choice = ask_int("Choose an option: ", 1, 5)

        if choice == 1:
            simple_savings_calculator(game_data)
        elif choice == 2:
            retirement_account_calculator(game_data)
        elif choice == 3:
            savings_account_calculator(game_data)
        elif choice == 4:
            housing_loan_calculator(game_data)
        elif choice == 5:
            break


def side_hustle_simulation(profile, game_data):
    wrap_print(
        "\nFinny: Welcome to the Side Hustle Simulator. In this mini game "
        "you pick a side hustle and decide how many hours to work each week. "
        "You will see how much you can earn and how random events can help "
        "or hurt your progress."
    )

    hustle_choice = ask_choice(
        "\nPick a side hustle:",
        [
            "Food delivery driver",
            "Content creator",
            "Tutor",
            "Online reseller",
        ],
    )

    track_subs = False
    subscribers = 0

    if hustle_choice.startswith("Food"):
        hustle_name = "Food delivery"
        base_hourly = 15.0
        good_events = [
            ("Big tip from a happy customer.", 20, 0),
            ("Busy night, lots of small tips.", 35, 0),
            ("Bonus from the app for completing a challenge.", 25, 0),
        ]
        bad_events = [
            ("Extra gas cost this week.", -15, 0),
            ("Parking ticket while delivering.", -40, 0),
            ("Slow night, fewer orders than usual.", -20, 0),
        ]
    elif hustle_choice.startswith("Content"):
        hustle_name = "Content creator"
        base_hourly = 5.0
        track_subs = True
        subscribers = 100
        good_events = [
            ("One of your videos does better than usual.", 50, 80),
            ("A brand sends you a small sponsorship.", 80, 40),
            ("You get new followers and more ad views.", 40, 120),
        ]
        bad_events = [
            ("Your editing software crashes and wastes time.", -10, -20),
            ("You get demonetized on one video.", -30, -50),
            ("You burn out and cannot post much.", -20, -40),
        ]
    elif hustle_choice.startswith("Tutor"):
        hustle_name = "Tutor"
        base_hourly = 18.0
        good_events = [
            ("Student’s parent recommends you to a friend.", 40, 0),
            ("Student pays for an extra session.", 30, 0),
            ("You raise your hourly rate slightly.", 20, 0),
        ]
        bad_events = [
            ("Student cancels last minute and does not pay.", -25, 0),
            ("You need to buy materials for a lesson.", -15, 0),
            ("A test gets postponed so you lose sessions.", -20, 0),
        ]
    else:
        hustle_name = "Online reseller"
        base_hourly = 12.0
        good_events = [
            ("You flip an item for a great profit.", 60, 0),
            ("You get a bulk deal on items to resell.", 35, 0),
            ("You receive a five star review that boosts sales.", 25, 0),
        ]
        bad_events = [
            ("Item gets returned and you pay shipping.", -30, 0),
            ("Platform fee is higher than you expected.", -15, 0),
            ("Package goes missing and you must refund.", -40, 0),
        ]

    if game_data.stats["side_hustle_sessions"] == 0:
        game_data.unlock("SIDE_HUSTLE_START")
    game_data.stats["side_hustle_sessions"] += 1
    game_data.log(f"Started side hustle: {hustle_name}.")

    if track_subs:
        wrap_print(
            f"\nFinny: You chose {hustle_name}. You start with about "
            f"{subscribers} subscribers in this mini game. The base pay is "
            f"about ${base_hourly:.2f} per hour, and your choices will affect "
            "both money and subscriber growth."
        )
    else:
        wrap_print(
            f"\nFinny: You chose {hustle_name}. The base pay in this mini game "
            f"is about ${base_hourly:.2f} per hour. Each week you set your hours, "
            "then a random event will affect your total."
        )

    total_earned = 0.0
    best_week = 0.0
    reputation = 0
    week = 0

    while True:
        week += 1
        print(f"\n----- Side Hustle Week {week} -----")

        focus = ask_choice(
            "What is your focus this week?",
            [
                "Earn money",
                "Grow audience or reputation",
                "Balanced",
            ],
        )

        hours = ask_float(
            "How many hours do you want to work this week (0 to 40): ",
            0,
            40,
        )

        if focus.startswith("Earn"):
            money_multiplier = 1.2
            subs_multiplier = 0.8
        elif focus.startswith("Grow"):
            money_multiplier = 0.8
            subs_multiplier = 1.3
        else:
            money_multiplier = 1.0
            subs_multiplier = 1.0

        base_earnings = hours * base_hourly * money_multiplier
        print(f"Base earnings from hours worked: ${base_earnings:.2f}")

        if random.random() < 0.6:
            event_desc, bonus_money, bonus_subs = random.choice(good_events)
            print(f"Good event: {event_desc} +${bonus_money:.2f}")
        else:
            event_desc, bonus_money, bonus_subs = random.choice(bad_events)
            print(f"Challenging event: {event_desc} {bonus_money:.2f}")

        week_total = base_earnings + bonus_money
        total_earned += week_total
        best_week = max(best_week, week_total)

        if hours >= 10:
            reputation += 2
        elif hours > 0:
            reputation += 1

        if track_subs:
            base_sub_gain = int(hours * 3)
            subs_change = int(base_sub_gain * subs_multiplier) + bonus_subs
            subscribers = max(0, subscribers + subs_change)
            print(f"Subscriber change this week: {subs_change:+d}")
            print(f"Total subscribers: {subscribers}")

        print(f"Total earnings this week: ${week_total:.2f}")
        print(f"Cumulative earnings from side hustle: ${total_earned:.2f}")
        print(f"Reputation points: {reputation}")

        if reputation < 5:
            level = "Newbie"
        elif reputation < 12:
            level = "Growing"
        elif reputation < 20:
            level = "Trusted"
        else:
            level = "Side hustle pro"

        print(f"Reputation level: {level}")

        if level == "Side hustle pro":
            game_data.unlock("SIDE_HUSTLE_PRO")

        cont = input(
            "\nPlay another week of your side hustle? "
            "(y to continue, anything else to stop): "
        ).strip().lower()
        if cont != "y":
            game_data.stats["side_hustle_total_earned"] += total_earned
            if total_earned > game_data.stats["side_hustle_best_week"]:
                game_data.stats["side_hustle_best_week"] = best_week
            if total_earned >= 1000:
                game_data.unlock("HUSTLE_RICH")

            if track_subs:
                game_data.log(
                    f"Ended side hustle {hustle_name} after {week} weeks with "
                    f"total ${total_earned:.2f} and {subscribers} subscribers."
                )
            else:
                game_data.log(
                    f"Ended side hustle {hustle_name} after {week} weeks with "
                    f"total ${total_earned:.2f}."
                )

            wrap_print(
                "\nFinny: Ending side hustle simulation. Remember this is just "
                "a model, but it shows how extra income can add up over time."
            )
            if track_subs:
                wrap_print(
                    f"You earned about ${total_earned:.2f} with a best week of "
                    f"${best_week:.2f}, reputation level {level} and "
                    f"{subscribers} subscribers."
                )
            else:
                wrap_print(
                    f"You earned about ${total_earned:.2f} with a best week of "
                    f"${best_week:.2f} and reputation level {level}."
                )
            break


def data_center(game_data):
    print("\n========== Data Center and Achievements ==========")
    game_data.stats["data_center_visits"] += 1
    if game_data.stats["data_center_visits"] == 1:
        game_data.unlock("DATA_NERD")

    print("\nStats overview:")
    for key, value in game_data.stats.items():
        print(f"  {key}: {value}")

    print("\nAchievements:")
    unlocked_count = 0
    for code, done in game_data.achievements.items():
        mark = "[X]" if done else "[ ]"
        desc = ACHIEVEMENTS_INFO[code]
        if done:
            unlocked_count += 1
        print(f"  {mark} {desc}")
    print(f"\nTotal achievements unlocked: {unlocked_count} out of {len(ACHIEVEMENTS_INFO)}")

    print("\nRecent history:")
    if not game_data.history:
        print("  No history yet.")
    else:
        for entry in game_data.history[-20:]:
            print(f"  - {entry}")

    input("\nPress Enter to return to the main menu...")


def create_user_profile(game_data):
    print("\n========== Welcome to the Finance Simulator ==========")
    wrap_print(
        "Finny the Finance Fox: Welcome to your personal money adventure. "
        "We will build a profile for you, pick a game job and explore "
        "budgeting, saving and investing."
    )

    if game_data.profile_dict is not None:
        use_old = input(
            "\nA saved profile was found. Do you want to load it? (y/n): "
        ).strip().lower()
        if use_old == "y":
            profile = UserProfile.from_dict(game_data.profile_dict)
            print("\nLoaded saved profile:")
            print(profile.summary())
            input("Press Enter to continue to the main menu...")
            return profile

    name = input("\nFirst, what is your name? ").strip() or "Player"
    age = ask_int("Enter your age: ", 10, 120)

    occupations = [
        "Student",
        "Part-time worker",
        "Full-time worker",
        "Self-employed",
        "Other",
    ]
    occupation = ask_choice("\nChoose your current situation:", occupations)

    marital = ask_choice(
        "\nChoose your marital status:",
        ["Single", "In a relationship", "Married", "Prefer not to say"],
    )

    print("\nWhat is your main financial goal right now?")
    print("Examples: pay off debt, save for a house, build emergency fund, retire early")
    goal = input("Type your goal: ").strip() or "Learn about money"

    profile = UserProfile(name, age, occupation, marital, goal)

    job_title, monthly_income = job_quiz()
    profile.job_title = job_title
    profile.monthly_income = monthly_income

    print(profile.summary())
    input("Press Enter to continue to the main menu...")
    return profile


def main_menu(profile, game_data):
    while True:
        print("\n========== Main Menu ==========")
        print("  1. Learn financial literacy")
        print("  2. Play the budget simulation game")
        print("  3. Investment simulation")
        print("  4. Talk to Finny (helper)")
        print("  5. Interest calculators")
        print("  6. Side hustle simulation")
        print("  7. Data center and history")
        print("  8. Quit")

        choice = ask_int("Choose an option: ", 1, 8)

        if choice == 1:
            lesson_financial_literacy(game_data)
        elif choice == 2:
            budget_simulation_game(profile, game_data)
        elif choice == 3:
            investment_simulation(profile, game_data)
        elif choice == 4:
            advice_bot(profile, None, game_data)
        elif choice == 5:
            interest_calculators_menu(game_data)
        elif choice == 6:
            side_hustle_simulation(profile, game_data)
        elif choice == 7:
            data_center(game_data)
        elif choice == 8:
            print("\nFinny: Thanks for playing the Finance Simulator. See you next time!")
            break

        game_data.profile_dict = profile.to_dict()
        game_data.save()


def main():
    game_data = load_game_data()
    game_data.stats["launch_count"] += 1
    if game_data.stats["launch_count"] >= 5:
        game_data.unlock("LONG_TERM_PLAYER")

    profile = create_user_profile(game_data)
    game_data.profile_dict = profile.to_dict()
    game_data.save()
    main_menu(profile, game_data)
    game_data.profile_dict = profile.to_dict()
    game_data.save()


if __name__ == "__main__":
    main()
