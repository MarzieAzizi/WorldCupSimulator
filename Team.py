# Team.py
""" کلاس تیم جام جهانی را نگهداری می‌کند """

import random
import numpy

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
