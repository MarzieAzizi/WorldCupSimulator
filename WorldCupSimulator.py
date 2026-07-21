# WorldCupSimulator.py
""" کلاس اصلی شبیه‌ساز جام جهانی را نگهداری می‌کند """

import random
import csv
import matplotlib.pyplot as plt
from Team import Team
from Match import Match
from Group import Group
from KnockoutStage import KnockoutStage

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
