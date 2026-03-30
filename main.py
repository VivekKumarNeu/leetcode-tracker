#!/usr/bin/env python3
"""
LeetCode Tracker - Main CLI Interface
A tool to track progress on NeetCode 150 problems with spaced repetition.
"""

import argparse
import sys
from datetime import datetime, timedelta
from typing import Optional
import uuid

from models import Attempt, ProblemProgress, Session, StudyPlan
from storage import Storage
from selector import QuestionSelector
from guide import LeetCodeGuide


class LeetCodeTracker:
    """Main application class."""
    
    def __init__(self):
        self.storage = Storage()
        self.selector = QuestionSelector(self.storage)
        self.guide = LeetCodeGuide()
    
    def print_header(self, text: str):
        """Print a formatted header."""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60 + "\n")
    
    def print_problem(self, problem: dict, index: int = 1):
        """Print a problem in formatted way."""
        status_icons = {
            "unsolved": "⬜",
            "solving": "🔄",
            "solved": "✅",
            "reviewing": "👁️"
        }
        difficulty_colors = {
            "Easy": "\033[92m",    # Green
            "Medium": "\033[93m",  # Yellow
            "Hard": "\033[91m"     # Red
        }
        reset = "\033[0m"
        
        icon = status_icons.get(problem["status"], "⬜")
        color = difficulty_colors.get(problem["difficulty"], "")
        
        print(f"{index}. {icon} {problem['id']}. {problem['title']}")
        print(f"   {color}[{problem['difficulty']}]{reset} | {problem['pattern']} | {problem['category']}")
        print(f"   🔗 {problem['url']}")
        
        if problem["attempts"] > 0:
            print(f"   Attempts: {problem['attempts']}", end="")
            if problem["last_time_minutes"]:
                print(f" | Last: {problem['last_time_minutes']} min", end="")
            if problem["last_solved"]:
                print(" | Solved", end="")
            print()
        
        if problem["confidence"] > 0:
            confidence_bar = "█" * problem["confidence"] + "░" * (5 - problem["confidence"])
            print(f"   Confidence: [{confidence_bar}] ({problem['confidence']}/5)")
        
        print()
    
    def cmd_daily(self, count: int = 2, topic: Optional[str] = None):
        """Get daily practice questions."""
        self.print_header("Your Daily Practice")
        
        if topic:
            topics = self.storage.load_topics()
            if topic not in topics:
                print(f"Invalid topic: '{topic}'")
                print(f"Valid topics: {', '.join(topics)}")
                return None

        questions = self.selector.get_daily_questions(count, topic=topic)
        
        if not questions:
            print("No questions available! Check your study plan settings.")
            return
        
        # Create a session
        session_id = str(uuid.uuid4())[:8]
        session = Session(
            session_id=session_id,
            date=datetime.now().isoformat(),
            problems_attempted=[]
        )
        
        print(f"Session ID: {session_id}")
        if topic:
            print(f"💡 Topic: {topic}")
        print(f"💡 Today's goal: {count} problem(s)\n")
        
        for i, q in enumerate(questions, 1):
            self.print_problem(q, i)
            session.problems_attempted.append(q["id"])

        # Persist the session with selected problem IDs
        self.storage.add_session(session)
        
        print("\n💬 Use 'hint <problem_id>' to get a hint")
        print("💬 Use 'start <problem_id>' when you begin solving")
        print("💬 Use 'complete <problem_id>' when you're done")
        
        return questions
    
    def cmd_review(self, count: int = 3):
        """Get review questions based on spaced repetition."""
        self.print_header("Review Queue")
        
        reviews = self.selector.get_review_questions(count)
        
        if not reviews:
            print("No reviews due! You're caught up.")
            return
        
        print(f"📋 {len(reviews)} problem(s) due for review\n")
        
        for i, q in enumerate(reviews, 1):
            self.print_problem(q, i)
    
    def cmd_stats(self):
        """Show progress statistics."""
        self.print_header("Your Progress")
        
        stats = self.storage.get_stats()
        
        print(f"Total Problems: {stats['total_problems']}")
        print(f"Solved: {stats['solved']} ({stats['completion_percentage']}%)")
        print(f"Attempted: {stats['attempted']}")
        print(f"Unsolved: {stats['unsolved']}")
        print()
        print("By Difficulty:")
        for diff, count in stats['by_difficulty'].items():
            print(f"  {diff}: {count}")
        print()
        print(f"Total Sessions: {stats['total_sessions']}")
        print(f"Total Time: {stats['total_time_hours']} hours")
        
        # Category breakdown
        print("\n📁 Progress by Category:")
        categories = self.selector.get_progress_by_category()
        for cat, data in sorted(categories.items()):
            pct = (data['solved'] / data['total'] * 100) if data['total'] > 0 else 0
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            print(f"  {cat:30} [{bar}] {data['solved']}/{data['total']}")
    
    def cmd_start(self, problem_id: int):
        """Mark a problem as being worked on."""
        progress = self.storage.get_problem_progress(problem_id)
        
        if progress.status == "solved":
            print("You've already solved this! Use 'review' to practice it again.")
            return
        
        progress.status = "solving"
        self.storage.update_problem_progress(problem_id, progress)
        
        print(f"🚀 Started working on problem #{problem_id}")
        print("Good luck! Use 'hint' if you need help.")
    
    def cmd_complete(self, problem_id: int, solved: bool, time_minutes: int, 
                     notes: str = "", solution: str = ""):
        """Mark a problem as completed."""
        progress = self.storage.get_problem_progress(problem_id)
        
        # Create attempt record
        attempt = Attempt(
            timestamp=datetime.now().isoformat(),
            solved=solved,
            time_taken_minutes=time_minutes,
            notes=notes,
            solution_code=solution
        )
        
        progress.attempts.append(attempt)
        progress.last_attempt_date = attempt.timestamp
        
        if solved:
            progress.status = "solved"
            progress.confidence_level = min(progress.confidence_level + 1, 5)
            
            # Schedule next review based on confidence
            review_intervals = [1, 3, 7, 14, 30]  # days
            interval = review_intervals[min(progress.confidence_level - 1, 4)]
            next_review = datetime.now() + timedelta(days=interval)
            progress.next_review_date = next_review.isoformat()
            
            print(f"✅ Great job! Next review scheduled in {interval} days.")
        else:
            progress.status = "solving"
            print("❌ Keep trying! You'll get it next time.")
        
        self.storage.update_problem_progress(problem_id, progress)
        
        # Show analysis
        problem = next((p for p in self.storage.load_problems() if p.id == problem_id), None)
        if problem:
            analysis = self.guide.analyze_performance(time_minutes, problem.difficulty, solved)
            print(f"\n{analysis}")
    
    def cmd_hint(self, problem_id: int, hint_num: int = 1):
        """Get a hint for a problem."""
        problem = next((p for p in self.storage.load_problems() if p.id == problem_id), None)
        
        if not problem:
            print(f"Problem #{problem_id} not found.")
            return
        
        print(f"\n💡 Hints for: {problem.title}")
        print(f"   Pattern: {problem.pattern}")
        print()
        
        hint = self.guide.get_hint(problem.category, problem.difficulty, hint_num)
        print(hint)
        
        print(f"\n💬 Use 'hint {problem_id} {hint_num + 1}' for another hint")
    
    def cmd_search(self, query: str = "", category: str = "", difficulty: str = "", 
                   status: str = ""):
        """Search for problems."""
        results = self.selector.search_questions(query, category, difficulty, status)
        
        if not results:
            print("No problems found matching your criteria.")
            return
        
        self.print_header(f"🔍 Search Results ({len(results)} found)")
        
        for i, problem in enumerate(results[:20], 1):  # Limit to 20
            self.print_problem(problem, i)
    
    def cmd_list_categories(self):
        """List all available categories."""
        problems = self.storage.load_problems()
        categories = set(p.category for p in problems)
        
        print("\n📁 Available Categories:")
        for cat in sorted(categories):
            count = sum(1 for p in problems if p.category == cat)
            print(f"  - {cat} ({count} problems)")
    
    def cmd_config(self, daily_goal: Optional[int] = None, 
                   difficulties: Optional[list] = None,
                   focus: Optional[list] = None):
        """Configure study plan."""
        plan = self.storage.load_study_plan()
        
        if daily_goal:
            plan.daily_goal = daily_goal
            print(f"✅ Daily goal set to {daily_goal} problems")
        
        if difficulties:
            plan.preferred_difficulty = difficulties
            print(f"✅ Difficulty filter: {', '.join(difficulties)}")
        
        if focus:
            plan.focus_categories = focus
            print(f"✅ Focus categories: {', '.join(focus)}")
        
        self.storage.save_study_plan(plan)
        
        # Show current config
        print("\n📋 Current Study Plan:")
        print(f"  Daily Goal: {plan.daily_goal}")
        print(f"  Difficulties: {', '.join(plan.preferred_difficulty)}")
        print(f"  Focus Categories: {', '.join(plan.focus_categories) if plan.focus_categories else 'All'}")
        print(f"  Exclude solved for: {plan.exclude_solved_days} days")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LeetCode Tracker - Track your NeetCode 150 progress",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s daily              # Get daily practice problems
  %(prog)s daily -n 5         # Get 5 problems for today
  %(prog)s daily --topic stack # Restrict to a NeetCode topic key
  %(prog)s review             # Get problems due for review
  %(prog)s stats              # Show your progress
  %(prog)s hint 1             # Get hint for problem #1
  %(prog)s start 1            # Mark problem #1 as started
  %(prog)s complete 1 -s      # Mark as solved (interactive)
  %(prog)s search -q "array"  # Search for problems with "array"
  %(prog)s config -g 3        # Set daily goal to 3
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Daily command
    daily_parser = subparsers.add_parser("daily", help="Get daily practice problems")
    daily_parser.add_argument("-n", "--count", type=int, default=2, help="Number of problems")
    daily_parser.add_argument(
        "--topic",
        default=None,
        help="Restrict daily questions to a topic key from data/neetcode150.json (e.g. arrays_hashing, stack)"
    )
    
    # Review command
    review_parser = subparsers.add_parser("review", help="Get review problems")
    review_parser.add_argument("-n", "--count", type=int, default=3, help="Number of problems")
    
    # Stats command
    subparsers.add_parser("stats", help="Show progress statistics")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start working on a problem")
    start_parser.add_argument("problem_id", type=int, help="Problem ID")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Mark problem as complete")
    complete_parser.add_argument("problem_id", type=int, help="Problem ID")
    complete_parser.add_argument("-s", "--solved", action="store_true", help="Mark as solved")
    complete_parser.add_argument("-t", "--time", type=int, required=True, help="Time taken in minutes")
    complete_parser.add_argument("--notes", default="", help="Notes about the solution")
    
    # Hint command
    hint_parser = subparsers.add_parser("hint", help="Get a hint for a problem")
    hint_parser.add_argument("problem_id", type=int, help="Problem ID")
    hint_parser.add_argument("hint_num", nargs="?", type=int, default=1, help="Hint number")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for problems")
    search_parser.add_argument("-q", "--query", default="", help="Search query")
    search_parser.add_argument("-c", "--category", default="", help="Filter by category")
    search_parser.add_argument("-d", "--difficulty", default="", help="Filter by difficulty")
    search_parser.add_argument("-s", "--status", default="", help="Filter by status")
    
    # Categories command
    subparsers.add_parser("categories", help="List all categories")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure study plan")
    config_parser.add_argument("-g", "--goal", type=int, help="Daily goal")
    config_parser.add_argument("--difficulties", nargs="+", help="Preferred difficulties")
    config_parser.add_argument("--focus", nargs="+", help="Focus categories")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    tracker = LeetCodeTracker()
    
    if args.command == "daily":
        tracker.cmd_daily(args.count, args.topic)
    elif args.command == "review":
        tracker.cmd_review(args.count)
    elif args.command == "stats":
        tracker.cmd_stats()
    elif args.command == "start":
        tracker.cmd_start(args.problem_id)
    elif args.command == "complete":
        tracker.cmd_complete(
            args.problem_id,
            args.solved,
            args.time,
            args.notes
        )
    elif args.command == "hint":
        tracker.cmd_hint(args.problem_id, args.hint_num)
    elif args.command == "search":
        tracker.cmd_search(args.query, args.category, args.difficulty, args.status)
    elif args.command == "categories":
        tracker.cmd_list_categories()
    elif args.command == "config":
        tracker.cmd_config(args.goal, args.difficulties, args.focus)


if __name__ == "__main__":
    main()
