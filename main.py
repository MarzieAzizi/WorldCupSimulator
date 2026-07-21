# ================================
# دانشجو: مرضیه عزیزی
# شماره دانشجویی: 403131063
# عنوان پروژه: شبیه‌ساز جام جهانی
# تاریخ تحویل: 1405/04/30
# ================================

# main.py
""" شبیه سازی جام جهانی 2026 با 32 تیم به صورت شی‌گرا و با استفاده از توزیع پواسون """

from WorldCupSimulator import WorldCupSimulator

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
