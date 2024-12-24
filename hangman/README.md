# Streamlit Hangman Game

An implementation of the classic Hangman word guessing game built with Streamlit. Features multiple difficulty levels, game statistics tracking, and a customizable word bank.

## 🎮 Features

- Three difficulty levels (Easy, Medium, Hard)
- Game statistics
- Custom word bank generator
- Visual feedback with ASCII art
- Colorful UI with correct/incorrect guess indicators
- Game state persistence

## 🚀 Getting Started

### Prerequisites

```bash
pip install -r requirements.txt
```

### Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd hangman-game
```

2. Generate the word bank:
```bash
# For common words (recommended)
python word_generator.py common

# For all words
python word_generator.py all
```

3. Run the game:
```bash
streamlit run main.py
```

## 🎯 How to Play

1. Select a difficulty level:
   - Easy: 4-5 letter words
   - Medium: 6-7 letter words
   - Hard: 8-30 letter words

2. Type a letter and click "Guess!" or press Enter
3. Try to guess the word before running out of lives
4. Track your progress with the statistics panel

## 📁 Project Structure

```
hangman/
├── main.py              # Main game implementation
├── word_generator.py    # Word bank generator
└── assets/
    └── wordbank.txt     # Generated word bank
```

## 🎨 Game Components

### GameState Class
Manages the core game state including:
- Current word
- Guessed letters
- Game progress
- Score tracking
- Message display

### Word Generator
- Uses NLTK corpus for word generation
- Filters words based on length and complexity
- Supports common and comprehensive word lists

### User Interface
- Responsive layout with Streamlit
- ASCII art for hangman visualization
- Color-coded feedback for guesses
- Real-time statistics tracking

## 🛠️ Configuration

Game settings can be adjusted in the `GameConfig` class:
- `MAX_LIVES`: Number of allowed incorrect guesses
- `COOLDOWN_SECONDS`: Delay between guesses
- `DIFFICULTY_LENGTHS`: Word length ranges for each difficulty

## 📊 Statistics Tracked

- Games played
- Win rate
- Best streak
- Current streak

## 🤝 Contributing

Feel free to fork the repository and submit pull requests. You can also open issues for bugs or feature requests.

## 🙏 Acknowledgments

- Streamlit for the awesome framework
- NLTK for providing the word corpus
- ASCII art for hangman visualization