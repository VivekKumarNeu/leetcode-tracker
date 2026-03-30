#!/usr/bin/env python3
"""
Interactive mode for LeetCode Tracker
A menu-driven interface for easier use
"""

import os
import sys
from datetime import datetime

from main import LeetCodeTracker


class InteractiveMode:
    """Interactive CLI interface."""
    
    def __init__(self):
        self.tracker = LeetCodeTracker()
        self.running = True
        self.current_session = None
        self.active_problems = {}
    
    def clear_screen(self):
        """Clear the terminal."""
        os.system('clear' if os.name != 'nt' else 'cls')
    
    def print_menu(self):
        """Print the main menu."""
        print("\n" + "=" * 60)
        print("  🎯 LeetCode Tracker - Interactive Mode")
        print("=" * 60)
        print("\nMain Menu:")
        print("  1. 📚 Get Daily Problems")
        print("  2. 🔄 Review Queue")
        print("  3. 📊 View Statistics")
        print("  4. 🔍 Search Problems")
        print("  5. 💡 Get Hint")
        print("  6. ⚙️  Configuration")
        print("  7. ❓ Help")
        print("  0. 👋 Exit")
        print()
    
    def get_choice(self, prompt="Enter choice: "):
        """Get user input."""
        try:
            return input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n")
            return "0"
    
    def daily_problems_flow(self):
        """Get and work on daily problems."""
        self.clear_screen()
        
        print("\nHow many problems would you like today? (default: 2)")
        count = self.get_choice("Enter number: ")
        count = int(count) if count.isdigit() else 2
        
        self.tracker.cmd_daily(count)
        
        # Store active problems for quick access
        self.active_problems = {}
        
        print("\n" + "-" * 60)
        print("Actions:")
        print("  s # - Start problem #")
        print("  c # - Complete problem #")
        print("  h # - Hint for problem #")
        print("  Enter - Back to menu")
        
        while True:
            action = self.get_choice("\nAction: ").lower()
            if not action:
                break
            
            parts = action.split()
            if len(parts) < 2:
                print("Usage: s # (start), c # (complete), or h # (hint)")
                continue
            
            cmd, prob_id = parts[0], parts[1]
            if not prob_id.isdigit():
                print("Please enter a valid problem number")
                continue
            
            prob_id = int(prob_id)
            
            if cmd == 's':
                self.tracker.cmd_start(prob_id)
            elif cmd == 'c':
                self.complete_problem_flow(prob_id)
            elif cmd == 'h':
                self.tracker.cmd_hint(prob_id)
            else:
                print("Unknown command. Use s, c, or h")
    
    def complete_problem_flow(self, problem_id: int):
        """Interactive flow for completing a problem."""
        print(f"\nMarking problem #{problem_id} as complete")
        
        solved = self.get_choice("Did you solve it? (y/n): ").lower() == 'y'
        
        while True:
            time_str = self.get_choice("How many minutes did it take? ")
            if time_str.isdigit():
                time_minutes = int(time_str)
                break
            print("Please enter a number")
        
        notes = self.get_choice("Any notes? (optional): ")
        
        self.tracker.cmd_complete(problem_id, solved, time_minutes, notes)
    
    def review_flow(self):
        """Review queue flow."""
        self.clear_screen()
        self.tracker.cmd_review(5)
    
    def stats_flow(self):
        """Statistics flow."""
        self.clear_screen()
        self.tracker.cmd_stats()
        input("\nPress Enter to continue...")
    
    def search_flow(self):
        """Search flow."""
        self.clear_screen()
        
        print("\n🔍 Search Problems")
        print("Leave blank to skip a filter\n")
        
        query = self.get_choice("Search term: ")
        
        print("\nCategories (or 'all'):")
        self.tracker.cmd_list_categories()
        category = self.get_choice("Category: ")
        if category == 'all':
            category = ""
        
        print("\nDifficulties: Easy, Medium, Hard (comma-separated or 'all')")
        diff = self.get_choice("Difficulty: ")
        if diff == 'all':
            difficulty = ""
        else:
            difficulty = diff
        
        print("\nStatus: unsolved, solving, solved")
        status = self.get_choice("Status: ")
        
        self.clear_screen()
        self.tracker.cmd_search(query, category, difficulty, status)
        input("\nPress Enter to continue...")
    
    def hint_flow(self):
        """Get hint flow."""
        self.clear_screen()
        
        prob_id = self.get_choice("Enter problem ID: ")
        if prob_id.isdigit():
            self.tracker.cmd_hint(int(prob_id))
        input("\nPress Enter to continue...")
    
    def config_flow(self):
        """Configuration flow."""
        self.clear_screen()
        
        print("\n⚙️  Configuration")
        print("Leave blank to keep current value\n")
        
        goal = self.get_choice("Daily goal (number of problems): ")
        goal = int(goal) if goal.isdigit() else None
        
        print("\nPreferred difficulties (comma-separated): Easy, Medium, Hard")
        diffs = self.get_choice("Difficulties: ")
        difficulties = [d.strip() for d in diffs.split(",")] if diffs else None
        
        print("\nFocus categories (comma-separated) - leave blank for all")
        focus = self.get_choice("Categories: ")
        focus_cats = [c.strip() for c in focus.split(",")] if focus else None
        
        self.tracker.cmd_config(goal, difficulties, focus_cats)
        input("\nPress Enter to continue...")
    
    def help_flow(self):
        """Show help."""
        self.clear_screen()
        print("""
🎯 LeetCode Tracker Help

QUICK START:
  1. Select "Get Daily Problems" to get your practice set
  2. Work on each problem
  3. Mark them complete with your results
  4. Review scheduled problems regularly

COMMANDS:
  • Daily mode gives you fresh problems based on your plan
  • Review mode shows problems due for spaced repetition
  • Search lets you find specific problems
  • Stats shows your overall progress

TIPS:
  • Use hints when stuck - don't waste too much time
  • Track your time to see improvement
  • Focus on patterns, not memorizing solutions
  • Regular reviews are key to retention

SPACED REPETITION:
  When you solve a problem, it's scheduled for review:
  - Confidence 1 → Review in 1 day
  - Confidence 2 → Review in 3 days
  - Confidence 3 → Review in 7 days
  - Confidence 4 → Review in 14 days
  - Confidence 5 → Review in 30 days

The tracker contains all 145 NeetCode problems organized by category.
        """)
        input("\nPress Enter to continue...")
    
    def run(self):
        """Main loop."""
        while self.running:
            self.clear_screen()
            self.print_menu()
            
            choice = self.get_choice()
            
            if choice == "0":
                self.running = False
                print("\nHappy coding! See you next time.\n")
            elif choice == "1":
                self.daily_problems_flow()
            elif choice == "2":
                self.review_flow()
            elif choice == "3":
                self.stats_flow()
            elif choice == "4":
                self.search_flow()
            elif choice == "5":
                self.hint_flow()
            elif choice == "6":
                self.config_flow()
            elif choice == "7":
                self.help_flow()
            else:
                print("Invalid choice. Press Enter to continue...")
                input()


def main():
    """Entry point for interactive mode."""
    app = InteractiveMode()
    app.run()


if __name__ == "__main__":
    main()
