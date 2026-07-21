# KnockoutStage.py
""" کلاس مرحله حذفی را نگهداری می‌کند """

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
