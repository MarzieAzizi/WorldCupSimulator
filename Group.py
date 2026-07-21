# Group.py
""" کلاس گروه و مسابقات درون‌گروهی را نگهداری می‌کند """

import random
from Match import Match

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
