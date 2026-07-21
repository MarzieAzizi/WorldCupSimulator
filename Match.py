# Match.py
""" کلاس مسابقه بین دو تیم را نگهداری می‌کند """

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
