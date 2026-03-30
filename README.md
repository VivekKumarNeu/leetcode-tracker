# 🎯 N-LeetCode Tracker

A fun Python CLI tool to track your progress through the NeetCode 150 problems with spaced repetition and intelligent question selection.

## Features

- **Progress Tracking** - Track your progress across all 150 NeetCode problems
- **Spaced Repetition** - Automatically schedules reviews based on your confidence level
- **Smart Selection** - Prioritizes unsolved problems and those due for review
- **Hints System** - Get pattern-based hints without spoilers
- **Statistics** - View completion stats by category, difficulty, and more
- **Search & Filter** - Find problems by category, difficulty, or keyword


![LeetCode Tracker Interactive mode](images/1.png)
![LeetCode Tracker Practice](images/2.png)
![LeetCode Tracker Status](images/3.png)

## Quick Start

```bash
# Get your daily practice problems
python main.py daily

# Get more problems
python main.py daily -n 5

# Check your progress
python main.py stats

# Get problems due for review
python main.py review

# Search for problems
python main.py search -q "two sum"
python main.py search -c arrays_hashing -d Easy
```

## Commands

### Daily Practice
```bash
python main.py daily          # Get 2 problems (default)
python main.py daily -n 5     # Get 5 problems
python main.py daily --topic stack   # Restrict to one NeetCode topic key
```

### Track Progress
```bash
python main.py start 1        # Mark problem #1 as "in progress"
python main.py complete 1 -s -t 25   # Mark as solved in 25 minutes
python main.py complete 1 -t 30      # Mark as attempted but not solved
```

### Get Help
```bash
python main.py hint 1         # Get hint for problem #1
python main.py hint 1 2       # Get second hint
```

### Configuration
```bash
python main.py config -g 3                     # Set daily goal to 3
python main.py config --difficulties Easy Medium  # Focus on Easy/Medium
python main.py config --focus arrays_hashing two_pointers  # Focus categories
```

### Other Commands
```bash
python main.py stats          # View your progress
python main.py review         # Get problems due for review
python main.py categories     # List all categories
python main.py search -q "dynamic"   # Search problems
```

## Data Files

All data is stored in the `data/` directory as JSON:

- `neetcode150.json` - The problem database
- `progress.json` - Your progress tracking
- `sessions.json` - Study session history
- `study_plan.json` - Your configuration

## Spaced Repetition Schedule

When you solve a problem, it's scheduled for review:

| Confidence Level | Review Interval |
|-----------------|-----------------|
| 1 | 1 day |
| 2 | 3 days |
| 3 | 7 days |
| 4 | 14 days |
| 5 | 30 days |

Your confidence increases each time you successfully solve a problem.

## Project Structure

```
leetcode-tracker/
├── main.py          # CLI interface
├── models.py        # Data models
├── storage.py       # JSON persistence
├── selector.py      # Question selection algorithm
├── guide.py         # Hints and guidance
├── data/            # Data directory
│   └── neetcode150.json
└── README.md
```

## Tips

1. **Start small**: Begin with 2 problems per day
2. **Use hints**: Don't struggle too long - get a hint and learn
3. **Review regularly**: Spaced repetition is key to retention
4. **Track time**: This helps gauge your improvement
5. **Focus on patterns**: Understanding patterns > memorizing solutions

## License

MIT License - Feel free to modify and share!
