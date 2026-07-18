# worldcup_simulator.py
""" شبیه سازی جام جهانی 2026 با 32 تیم به صورت شی‌گرا و با استفاده از توزیع پواسون """
# ================================
# دانشجو: مرضیه عزیزی
# شماره دانشجویی: 403131063
# عنوان پروژه: شبیه‌ساز جام جهانی
# تاریخ تحویل: 1405/04/27
# ================================


import random
import csv
import numpy
import matplotlib.pyplot as plt


class Team:

    """ کلاس تیم : نگهداری مشخصات و آمار هر تیم و شبیه‌سازی یک مسابقه """

    def __init__(self , name , attack , defense , rank) :

        """سازنده کلاس تیم
        Args:
            name (str): نام تیم
            attack (int): قدرت حمله
            defense (int): قدرت دفاع
            rank (int): رتبه فیفا
        """

        self.name = name
        self.attack = attack
        self.defense = defense
        self.rank = rank
        self.goals_for = 0          # گل های زده شده
        self.goals_against = 0      # گل های خورده شده
        self.points = 0             # امتیاز کسب شده در مرحله گروهی
        self.group = ""             # A نام گروهی که تیم در آن قرار دارد مثلا
        self.pens = 0               # گل‌های پنالتی این تیم در آخرین مسابقه حذفی

    def goal_difference(self):

        """تفاضل گل تیم را برمی‌گرداند
        Returns:
            int: goals_for - goals_against
        """

        return self.goals_for - self.goals_against

    def reset_stats(self):

        """ آمار تیم (گل زده ، گل خورده ، امتیاز و پنالتی) را صفر می‌کند """

        self.goals_for = 0
        self.goals_against = 0
        self.points = 0
        self.pens = 0

    def _goals_by_poisson(self , attack , defense , factor):

        """محاسبه تعداد گل یک تیم با فرمول لامبدا و توزیع پواسون
        Args:
            attack (int): قدرت حمله تیم زننده گل
            defense (int): قدرت دفاع تیم حریف
            factor (float): ضریب لامبدا (مثلا وقت اضافه = 0.33)
        Returns:
            int: تعداد گل های احتمالی
        """
        
        lam = ((attack / 100) * 1.5 + (1 - defense / 100) * 0.8) * factor
        return int(numpy.random.poisson(lam))
        # تولید تصادفی تعداد گل بر اساس توزیع پواسون

    def _penalty_prob(self , opponent):

        """احتمال گل شدن یک ضربه پنالتی در بازه [0.6 , 0.9] 
        Args:
            opponent (Team): تیم حریف
        Returns:
            float: احتمال گل شدن هر پنالتی
        """

        p = 0.75 + (self.attack - opponent.defense) / 250
        if p < 0.6:
            p = 0.6
        elif p > 0.9:
            p = 0.9
        return p

    def _penalty_shootout(self , opponent):

        """شبیه سازی ضربات پنالتی (ابتدا 5 ضربه و در صورت تساوی پنالتی ناگهانی)
        Args:
            opponent (Team): تیم حریف
        Returns:
            Team: تیم برنده ضربات پنالتی
        """

        # محاسبه احتمال گل شدن پنالتی هر تیم
        p_self = self._penalty_prob(opponent)
        p_opponent = opponent._penalty_prob(self)

        # تعداد پنالتی های هر تیم
        self.pens = 0
        opponent.pens = 0

        # پنج پنالتی برای هر تیم
        for i in range(5):
            if random.random() < p_self:
                self.pens += 1
            if random.random() < p_opponent:
                opponent.pens += 1

        # پنالتی ناگهانی : هر دور یک ضربه برای هر تیم و بررسی نتیجه
        while self.pens == opponent.pens:
            goal_self = 1 if random.random() < p_self else 0
            goal_opponent = 1 if random.random() < p_opponent else 0
            self.pens += goal_self
            opponent.pens += goal_opponent
            if goal_self != goal_opponent:
                break

        if self.pens > opponent.pens:
            return self
        else:
            return opponent

    def simulate_match(self , opponent , is_knockout=False):

        """شبیه‌سازی نتیجه بازی با تیم حریف
        Args:
            opponent (Team): تیم حریف
            is_knockout (bool): آیا مرحله حذفی است
        Returns:
            tuple: (گل تیم خودی , گل تیم حریف , برنده مسابقه)
        """

        self.pens = 0
        opponent.pens = 0

        # نود دقیقه بازی
        goals_self = self._goals_by_poisson(self.attack , opponent.defense , 1)
        goals_opponent = self._goals_by_poisson(opponent.attack, self.defense, 1)

        winner = None

        if goals_self > goals_opponent:
            winner = self
        elif goals_opponent > goals_self:
            winner = opponent

        # در مرحله حذفی اگر مساوی شد : وقت اضافه و سپس پنالتی
        if is_knockout and winner is None:
            # factor = 0.33 -> وقت اضافه
            goals_self += self._goals_by_poisson(self.attack, opponent.defense, 0.33)
            goals_opponent += self._goals_by_poisson(opponent.attack, self.defense, 0.33)

            if goals_self > goals_opponent:
                winner = self
            elif goals_opponent > goals_self:
                winner = opponent
            else:
                winner = self._penalty_shootout(opponent)

        return (goals_self, goals_opponent, winner)

    def __repr__(self):

        """ نمایش نام تیم هنگام چاپ شیء """

        return self.name


class Match:

    """ کلاس مسابقه بین دو تیم : انجام بازی و به‌روزرسانی آمار تیم‌ها """

    def __init__(self , team1 , team2 , is_knockout=False):

        """سازنده کلاس مسابقه
        Args:
            team1 (Team): تیم اول
            team2 (Team): تیم دوم
            is_knockout (bool): آیا مسابقه در مرحله حذفی است
        """

        self.team1 = team1
        self.team2 = team2
        self.goals1 = 0
        self.goals2 = 0
        self.is_knockout = is_knockout
        self.winner = None
        self.went_to_pens = False       # آیا مسابقه به مرحله پنالتی رسیده است
        self.pens1 = 0
        self.pens2 = 0

    def play(self):

        """ انجام مسابقه ، به روز رسانی آمار تیم‌ها ، تعیین برنده """

        goals1 , goals2 , winner = self.team1.simulate_match(self.team2 , self.is_knockout)
        self.goals1 = goals1
        self.goals2 = goals2

        # به‌روزرسانی گل زده و گل خورده هر تیم
        self.team1.goals_for += goals1
        self.team1.goals_against += goals2
        self.team2.goals_for += goals2
        self.team2.goals_against += goals1

        if self.is_knockout:
        # اگر بازی در مرحله حذفی باشد
            self.winner = winner

            if goals1 == goals2:
            # اگر بازی به پنالتی رفته باشد،امتیاز پنالتی برای نمایش ذخیره می‌شود
                self.went_to_pens = True
                self.pens1 = self.team1.pens
                self.pens2 = self.team2.pens
        else:
        # اگر بازی در مرحله گروهی باشد
        # برد 3 امتیاز ، مساوی 1 امتیاز ، باخت 0 امتیاز
            if goals1 > goals2:
                self.team1.points += 3
            elif goals2 > goals1:
                self.team2.points += 3
            else:
                self.team1.points += 1
                self.team2.points += 1

    def result_line(self):

        """فرمت دهی متن نتیجه مسابقه با در نظر گرفتن پنالتی‌ها
        Returns:
             str: نتیجه بازی (مثلا : 'Brazil 1-1 (4-2 pens) France -> Winner: Brazil')
        """
        
        if self.went_to_pens:               # بازی به مرحله پنالتی رفته
            score = (f"{self.team1.name} {self.goals1}-{self.goals2} "
                     f"({self.pens1}-{self.pens2} pens) {self.team2.name}")
            
        else:                               # بازی به مرحله پنالتی نرفته
            score = f"{self.team1.name} {self.goals1}-{self.goals2} {self.team2.name}"

        return f"{score} -> Winner: {self.winner.name}"


class Group:

    """ کلاس گروه : نگهداری 4 تیم و انجام مسابقات و رتبه بندی درون گروهی """

    def __init__(self , name , teams):

        """سازنده کلاس گروه
        Args:
            name (str): نام گروه ( A , B , C , ... )
            teams (list): لیست 4 تیم گروه
        """

        self.name = name
        self.teams = teams

    def play_all_matches(self):

        """ تمام مسابقات گروه را انجام می‌دهد (هر تیم یک بار با سه تیم دیگر) """

        for i in range(4):
            for j in range(i + 1 , 4):
                match = Match(self.teams[i] , self.teams[j] , False)
                match.play()

    def get_ranking(self):

        """تیم های گروه را بر اساس قوانین فیفا مرتب میکند
        ترتیب : امتیاز بیشتر ، تفاضل گل بیشتر ، گل زده بیشتر ، قرعه تصادفی
        Returns:
            list: لیست تیم‌ها از رتبه اول تا چهارم
        """

        return sorted(
            self.teams , 
            key = lambda team : 
            (team.points , team.goal_difference() , team.goals_for , random.random()) , 
            reverse=True)

    def advance_teams(self):

        """دو تیم اول گروه را برمیگرداند
        Returns:
            tuple: (تیم اول , تیم دوم)
        """

        ranking = self.get_ranking()
        return (ranking[0] , ranking[1])


class KnockoutStage:

    """ کلاس مرحله حذفی : نگهداری مسابقات ، انجام آن‌ها و نمایش نتایج """

    def __init__(self , round_name , matches):

        """سازنده کلاس مرحله حذفی
        Args:
            round_name (str): نام مرحله (مثلا Round of 16)
            matches (list): لیست مسابقات این مرحله
        """

        self.round_name = round_name
        self.matches = matches

    def play_round(self):

        """ تمام مسابقات این مرحله را انجام می‌دهد """

        for match in self.matches:
            match.play()

    def get_winners(self):

        """لیست تیم‌های برنده این مرحله را به ترتیب برمیگرداند
        Returns:
            list: تیم‌های برنده
        """

        return [match.winner for match in self.matches]

    def display_results(self):

        """ خلاصه نتایج مرحله‌ی فعلی را چاپ می‌کند """

        print(f"===== {self.round_name} =====")
        for match in self.matches:
            print(match.result_line())


class WorldCupSimulator:

    """ کلاس اصلی شبیه‌ساز جام جهانی : مدیریت تیم‌ها، گروه‌ها و مراحل حذفی """

    def __init__(self):

        """ سازنده کلاس اصلی و مقداردهی اولیه ویژگی‌ها """

        self.teams = []
        self.groups = []
        self.round_of_16 = None     # یک هشتم
        self.quarterfinals = None   # یک جهارم
        self.semifinals = None      # نیمه نهایی
        self.final = None           # نهایی
        self.champion = None        # قهرمان نهایی

    def load_teams_from_csv(self , filename):

        """ فایل سی اس وی را می‌خواند و لیست اشیاء کلاس تیم را می‌سازد 
        Args:
            filename (str): نام فایل سی اس وی تیم‌ها
        Returns:
            bool: Success -> True & Failure -> False
        """

        try:
            self.teams = []

            with open(filename) as csv_file:
            # باز کردن فایل و خواندن اطلاعات تیم‌ها

                reader = csv.reader(csv_file)
                next(reader)
                # رد کردن سطر عنوان یا هدر

                for row in reader:
                    name = row[0]
                    attack = int(row[1])
                    defense = int(row[2])
                    rank = int(row[3])

                    self.teams.append(Team(name , attack , defense , rank))

            print(f"{len(self.teams)} teams loaded successfully.")
            return True
        
        except FileNotFoundError:
        # مدیریت خطای عدم وجود فایل
            print(f"Error: file '{filename}' not found.")
            return False

    def seed_and_draw_groups(self):

        """گروه‌ها را بر اساس سیدبندی رنکینگ فیفا قرعه‌کشی می‌کند
        سید 1 : رتبه‌های 01-08 
        سید 2 : رتبه‌های 09-16
        سید 3 : رتبه‌های 17-24
        سید 4 : رتبه‌های 25-32
        هر گروه دقیقا یک تیم از هر سید دارد
        """

        # مرتب‌سازی تیم‌ها بر اساس رتبه فیفا
        ranked = sorted(self.teams, key=lambda team: team.rank)

        seed1 = ranked[0:8]
        seed2 = ranked[8:16]
        seed3 = ranked[16:24]
        seed4 = ranked[24:32]

        # بر زدن تصادفی تیم‌های هر سید برای قرعه‌کشی
        seed1 = random.sample(seed1 , 8)
        seed2 = random.sample(seed2 , 8)
        seed3 = random.sample(seed3 , 8)
        seed4 = random.sample(seed4 , 8)

        group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
        self.groups = []

        for i in range(8):      # seeds length = 8
            teams = [seed1[i], seed2[i], seed3[i], seed4[i]]
            for team in teams:
                team.group = group_names[i]
            self.groups.append(Group(group_names[i] , teams))

    def run_group_stage(self):

        """ مرحله گروهی را اجرا و جدول هر گروه را چاپ می‌کند """

        # صفر کردن آمار تیم‌ها برای اینکه اجرای دوباره این گزینه باعث جمع‌شدن امتیازها نشود
        for team in self.teams:
            team.reset_stats()

        for group in self.groups:
            group.play_all_matches()

        for group in self.groups:
            print(f"===== Group {group.name} =====")

            ranking = group.get_ranking()
            for i in range(4):      # len(ranking) = 4
                team = ranking[i]
                gd = team.goal_difference()
                gd_text = f"+{gd}" if gd > 0 else str(gd)
                print(f"{i + 1}. {team.name}: {team.points} pts, GD {gd_text}, GF {team.goals_for}")
                
            print()     # یک خط خالی چاپ میکند

    def _find_group(self , name):

        """گروه را با نام آن پیدا می‌کند
        Args:
            name (str): نام گروه
        Returns:
            Group: شیء گروه متناظر
        """

        for group in self.groups:
            if group.name == name:
                return group

    def setup_knockout_bracket(self):

        """ براکت مرحله یک هشتم را بر اساس قانون فیفا میسازد """

        # دو تیم اول هر گروه
        # Key = group.name : Value = Team object
        firsts = {}     
        seconds = {}

        for group in self.groups:
            first_team , second_team = group.advance_teams()
            firsts[group.name] = first_team
            seconds[group.name] = second_team

        # جفت‌های ثابت فیفا برای مرحله یک هشتم
        pairs = [("A", "B"), ("C", "D"), ("E", "F"), ("G", "H"),
                 ("B", "A"), ("D", "C"), ("F", "E"), ("H", "G")]

        matches = []

        for first_group , second_group in pairs:
            match = Match(firsts[first_group] , seconds[second_group] , True)
            matches.append(match)

        self.round_of_16 = KnockoutStage("Round of 16" , matches)

    def run_knockout_stage(self):

        """ تمام مراحل حذفی را اجرا و قهرمان را مشخص می‌کند """

        # یک‌ هشتم نهایی
        self.round_of_16.play_round()
        winners = self.round_of_16.get_winners()

        # یک‌ چهارم نهایی
        self.quarterfinals = KnockoutStage("Quarterfinals" , self._make_matches(winners))
        self.quarterfinals.play_round()
        winners = self.quarterfinals.get_winners()

        # نیمه‌ نهایی
        self.semifinals = KnockoutStage("Semifinals" , self._make_matches(winners))
        self.semifinals.play_round()
        winners = self.semifinals.get_winners()

        # فینال
        self.final = KnockoutStage("Final", self._make_matches(winners))
        self.final.play_round()

        # قهرمان نهایی
        self.champion = self.final.get_winners()[0]

    def _make_matches(self , teams):

        """از روی لیست برندگان ، مسابقات مرحله بعد را می‌سازد
        Args:
            teams (list): لیست تیم‌های برنده
        Returns:
            list: لیست مسابقات مرحله بعد
        """

        matches = []

        for i in range(0 , len(teams) , 2):
            matches.append(Match(teams[i], teams[i + 1], True))
        return matches

    def run_full_simulation(self):

        """ یک جام کامل (گروهی + حذفی) را اجرا و قهرمان را برمیگرداند  
        Returns:
            Team: قهرمان جام جهانی
        """

        # صفر کردن آمار همه تیم‌ها قبل از شروع شبیه‌سازی
        for team in self.teams:
            team.reset_stats()

        for group in self.groups:
            group.play_all_matches()

        self.setup_knockout_bracket()       
        # اجرای اولین مسابقات مرحله حذفی : یک هشتم
        self.run_knockout_stage()
        return self.champion

    def most_likely_champion(self , num_simulations=1000):

        """جام‌جهانی را چندبار شبیه‌سازی و درصد قهرمانی هر تیم را چاپ می‌کند
        Args:
            num_simulations (int): تعداد دفعات شبیه‌سازی با مقدار پیش فرض 1000     
            Returns:
            dict: تعداد قهرمانی هر تیم
        """

        if num_simulations <= 0:
            print("Error: number of simulations must be a positive number.")
            return {}       
            # یک دیکشنری خالی برمیگرداند که برنامه متوقف نشود 

        counter = {}
        for i in range(num_simulations):
            champion = self.run_full_simulation()
            
            # اگر این تیم قبلا هم قهرمان بوده، یکی به تعداد قهرمانی هایش اضافه کن
            if champion.name in counter:
                counter[champion.name] = counter[champion.name] + 1
            # اگر این اولین باری است که این تیم قهرمان می‌شود، آن را با مقدار 1 وارد دیکشنری کن
            else:
                counter[champion.name] = 1

        print(f"Simulation ran {num_simulations} times.")
        print("Championship percentage of each team:")

        # مرتب‌سازی نزولی بر اساس تعداد قهرمانی
        ordered = sorted(counter.items() , key=lambda item: item[1] , reverse=True)
        for name, wins in ordered:
            percent = wins / num_simulations * 100
            print(f"{name}: {percent:.1f}%")

        self._draw_chart(ordered , num_simulations)
        return counter

    def _draw_chart(self, ordered , num_simulations):

        """ نمودار میله‌ای درصد قهرمانی تیم‌های برتر را رسم و ذخیره می‌کند
        Args:
            ordered (list): لیست مرتب‌ شده (نام تیم , تعداد قهرمانی)
            num_simulations (int): تعداد کل شبیه‌سازی‌ها
        """

        # فقط 16 تیم برتر را نمایش بده
        top = ordered[:16]
        names = [item[0] for item in top]
        percents = [item[1] / num_simulations * 100 for item in top]

        plt.figure(figsize=(12 , 6))
        # یک پنجره جدید برای نمودار با ابعاد 12 در 6 اینچ ایجاد میکند
        plt.bar(names, percents, color="lightblue")
        # یک نمودار میله ای یا بار چارت رسم میکند
        # محور افقی : نام تیم‌ها & محور عمودی : درصد ها & رنگ : آبی
        plt.xlabel("Team")
        plt.ylabel("Championship %")
        plt.title(f"World Cup Simulator 2026")
        plt.xticks(rotation=45)
        # نام تیم ها را روی محور افقی با زاویه 45 درجه میچرخاند
        plt.tight_layout()
        # به طور خودکار حاشیه‌ها و فواصل نمودار را تنظیم می‌کند 
        # تا هیچ بخشی از متن‌ها یا نمودار از کادر بیرون نزند
        plt.savefig("championship_chart.png")
        # ذخیره نمودار به عنوان  یک عکس با نام داده شده
        print("Chart saved to 'championship_chart.png'.")

    def display_bracket(self):

        """ براکت حذفی آخرین شبیه‌سازی را نمایش می‌دهد """

        print("===== Knockout Bracket =====")
        self.round_of_16.display_results()
        self.quarterfinals.display_results()
        self.semifinals.display_results()
        self.final.display_results()

        print(f"WorldCup Champion: {self.champion.name}")


def print_menu():

    """ منوی اصلی برنامه را چاپ می‌کند """

    print("===== World Cup Simulator =====")
    print("1) Load teams from CSV file")
    print("2) Draw groups (automatic seeding)")
    print("3) Run group stage and show each group's table")
    print("4) Run full tournament (group + knockout) and show champion")
    print("5) Run 1000 simulations and report championship percentage")
    print("6) Show knockout bracket of last simulation")
    print("7) Exit")


def main():

    """ حلقه اصلی برنامه : نمایش منو و مدیریت انتخاب‌های کاربر """

    simulator = WorldCupSimulator()
    teams_loaded = False        # بارگذاری فایل 
    groups_drawn = False        # قرعه کشی
    # مدیریت مراحل بازی 

    while True:
        print_menu()
        choice = input("Please choose an option: ").strip()
        # strip() : فاصله های اضافه را از اول و آخر ورودی کاربر حذف میکند

        if choice == "1":
            if simulator.load_teams_from_csv("worldcup_2026_teams.csv"):
                teams_loaded = True
                groups_drawn = False
                # اگر قبلا قرعه کشی انجام شده بود با لود مجدد فایل، قرعه کشی قبلی باطل میشه

        elif choice == "2":
            if not teams_loaded:
                print("Please load the teams first.")
            else:
                simulator.seed_and_draw_groups()
                groups_drawn = True
                print("Groups were drawn successfully.")

        elif choice == "3":
            if not teams_loaded:
                print("Please load the teams first.")
            elif not groups_drawn:
                print("Please draw the groups first.")
            else:
                simulator.run_group_stage()

        elif choice == "4":
            if not teams_loaded:
                print("Please load the teams first.")
            elif not groups_drawn:
                print("Please draw the groups first.")
            else:
                simulator.run_full_simulation()
                match = simulator.final.matches[0]
                print("===== FINAL =====")
                print(f"{match.team1.name} {match.goals1} - {match.goals2} {match.team2.name}")
                print(f"🏆 World Cup Champion: {simulator.champion.name} 🏆")

        elif choice == "5":
            if not teams_loaded:
                print("Please load the teams first.")
            elif not groups_drawn:
                print("Please draw the groups first.")
            else:
                number = input("Number of simulations (default 1000): ").strip()
                if  number == "" :
                    number = 1000
                try:
                # بررسی میکند که کاربر حتما عدد وارد کرده باشد
                    number = int(number)
                    simulator.most_likely_champion(number)
                except ValueError:
                    print("Error: please enter a valid integer.")

        elif choice == "6":
            if not teams_loaded:
                print("Please load the teams first.")
            elif not groups_drawn:
                print("Please draw the groups first.")
            elif simulator.final is None:
                print("Please run a full simulation first (option 4 or 5).")
            else:
                simulator.display_bracket()

        elif choice == "7":
            print("Goodbye!")
            break
            # while شکستن حلقه بی نهایت

        else:
            print("Invalid option, please try again.")

        print()


main()