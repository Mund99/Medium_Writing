import streamlit as st
import random
import time
import logging
from typing import List, Set, Dict
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Game configuration
class GameConfig:
    MAX_LIVES = 6
    COOLDOWN_SECONDS = 0.5
    DIFFICULTY_LENGTHS = {
        'easy': (3, 5),
        'medium': (6, 7),
        'hard': (8, 30)
    }

@dataclass
class GameState:
    word: str
    guessed_letters: Set[str] = field(default_factory=set)
    incorrect_attempts: int = 0
    game_over: bool = False
    game_won: bool = False
    message: str = ""
    message_type: str = "info"
    guessing_board: List[str] = field(default_factory=list)
    last_guess_time: float = 0.0

# Hangman ASCII art
HANGMAN_IMAGES = [
"""-----
  |   |
      |
      |
      |
      |
-------""",
"""-----
  |   |
  O   |
      |
      |
      |
-------""",
"""-----
  |   |
  O   |
  |   |
      |
      |
-------""",
"""-----
  |   |
  O   |
 /|   |
      |
      |
-------""",
"""-----
  |   |
  O   |
 /|\\  |
      |
      |
-------""",
"""-----
  |   |
  O   |
 /|\\  |
 /    |
      |
-------""",
"""-----
  |   |
  O   |
 /|\\  |
 / \\  |
      |
-------"""
]

@st.cache_data
def load_word_bank() -> List[str]:
    """Load and cache the word bank."""
    try:
        with open('assets/wordbank.txt', 'r') as file:
            return [word.strip().lower() for word in file.readlines() if word.strip()]
    except FileNotFoundError:
        logger.error("Word bank file not found!")
        return ["hangman"]  # Default fallback

def get_random_word(difficulty: str) -> str:
    """Get a random word based on difficulty level."""
    word_list = load_word_bank()
    min_len, max_len = GameConfig.DIFFICULTY_LENGTHS[difficulty]
    filtered_words = [
        word for word in word_list
        if min_len <= len(word) <= max_len
    ]
    return random.choice(filtered_words) if filtered_words else random.choice(word_list)

def load_custom_css() -> None:
    """Load custom CSS styles."""
    st.markdown("""
        <style>
        .game-title {
            text-align: center;
            color: #1E88E5;
            font-size: 48px;
            margin-bottom: 30px;
        }
        /* Hide Streamlit form hints */
        .stTextInput + div[data-baseweb="form-control-counter"] {
            display: none !important;
        }
        .st-emotion-cache-16idsys p {
            display: none;
        }
        .word-display {
            font-family: monospace;
            font-size: 36px;
            letter-spacing: 5px;
            margin: 20px 0;
            text-align: center;
        }
        .lives-remaining {
            font-size: 24px;
            font-weight: bold;
            color: #E53935;
            text-align: center;
        }
        .hangman-ascii {
            font-family: monospace;
            white-space: pre;
            font-size: 18px;
            line-height: 1.2;
            background-color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            margin: 20px auto;
            text-align: center;
        }
        .guessed-letters {
            font-family: monospace;
            font-size: 20px;
            color: #666;
            letter-spacing: 2px;
            text-align: center;
            margin: 20px 0;
        }
        .stats-container {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        .letter-badge {
            display: inline-block;
            color: white;
            width: 30px;
            height: 30px;
            line-height: 30px;
            text-align: center;
            border-radius: 50%;
            margin: 0 3px;
        }
        .letter-badge-correct {
            background-color: #4CAF50;  /* Green color for correct guesses */
        }
        .letter-badge-incorrect {
            background-color: #F44336;  /* Red color for incorrect guesses */
        }
        /* Game message styles */
        .game-message-error {
            color: #F44336;  /* Red for errors/incorrect guesses */
            font-weight: bold;
        }
        .game-message-success {
            color: #4CAF50;  /* Green for correct guesses */
            font-weight: bold;
        }
        .game-message-warning {
            color: #FFA726;  /* Orange for warnings */
            font-weight: bold;
        }
        .game-message-info {
            color: #2196F3;  /* Blue for info */
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

def initialize_session_state() -> None:
    """Initialize all session state variables."""
    # Initialize difficulty if not present
    if 'difficulty' not in st.session_state:
        st.session_state.difficulty = 'medium'
    
    # Initialize game statistics if not present
    if 'game_stats' not in st.session_state:
        st.session_state.game_stats = {
            'wins': 0,
            'losses': 0,
            'total_games': 0,
            'best_streak': 0,
            'current_streak': 0
        }
    
    # Initialize game state if not present
    if 'game_state' not in st.session_state or st.session_state.game_state is None:
        word = get_random_word(st.session_state.difficulty)
        st.session_state.game_state = GameState(
            word=word,
            guessing_board=['_' for _ in word]
        )

def update_game_stats(won: bool) -> None:
    """Update game statistics."""
    stats = st.session_state.game_stats
    stats['total_games'] += 1
    
    if won:
        stats['wins'] += 1
        stats['current_streak'] += 1
        stats['best_streak'] = max(stats['best_streak'], stats['current_streak'])
    else:
        stats['losses'] += 1
        stats['current_streak'] = 0

def process_guess(guess: str) -> bool:
    """Process the player's guess and update game state."""
    game_state = st.session_state.game_state

    # Rate limiting
    current_time = time.time()
    if current_time - game_state.last_guess_time < GameConfig.COOLDOWN_SECONDS:
        game_state.message = 'Please wait before guessing again'
        game_state.message_type = "warning"
        return False

    # Input validation
    if not guess or not guess.isalpha() or len(guess) != 1:
        game_state.message = 'Please enter a single letter'
        game_state.message_type = "error"
        return False

    guess = guess.lower()
    if guess in game_state.guessed_letters:
        game_state.message = 'You already guessed that letter!'
        game_state.message_type = "warning"
        return False

    # Update game state
    game_state.last_guess_time = current_time
    game_state.guessed_letters.add(guess)

    if guess in game_state.word:
        # Update guessing board
        for i, letter in enumerate(game_state.word):
            if letter == guess:
                game_state.guessing_board[i] = guess
        game_state.message = "Good guess!"
        game_state.message_type = "success"
    else:
        game_state.incorrect_attempts += 1
        game_state.message = f"Incorrect guess! {GameConfig.MAX_LIVES - game_state.incorrect_attempts} lives remaining"
        game_state.message_type = "error"

    # Check win/lose conditions
    if '_' not in game_state.guessing_board:
        game_state.game_over = True
        game_state.game_won = True
        update_game_stats(True)
    elif game_state.incorrect_attempts >= GameConfig.MAX_LIVES:
        game_state.game_over = True
        game_state.game_won = False
        update_game_stats(False)

    return True

def get_letter_badge_class(letter: str, word: str) -> str:
    """Return the CSS class for letter badge based on whether the guess was correct."""
    return "letter-badge-correct" if letter in word else "letter-badge-incorrect"

def display_game_stats() -> None:
    """Display game statistics."""
    stats = st.session_state.game_stats
    total_games = stats['total_games']
    if total_games > 0:
        win_rate = (stats['wins'] / total_games) * 100
        st.markdown(
            f"""
            <div class="stats-container">
                <div>Games Played: {total_games}</div>
                <div>Win Rate: {win_rate:.1f}%</div>
                <div>Best Streak: {stats['best_streak']}</div>
                <div>Current Streak: {stats['current_streak']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_difficulty_selector() -> None:
    """Display difficulty level selector."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        difficulty = st.select_slider(
            "Select Difficulty",
            options=['easy', 'medium', 'hard'],
            value=st.session_state.difficulty,
            key='difficulty_selector'
        )
        
        # Only update if difficulty actually changed
        if difficulty != st.session_state.difficulty:
            st.session_state.difficulty = difficulty
            st.session_state.game_state = None  # Clear game state
            st.rerun()

def main() -> None:
    """Main game function."""
    try:
        st.set_page_config(
            page_title="Hangman Game",
            page_icon="🎮",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Initialize all session state variables first
        initialize_session_state()
        
        load_custom_css()
        
        st.markdown('<h1 class="game-title">🎮 Hangman Game</h1>', unsafe_allow_html=True)
        
        if not st.session_state.game_state.game_over:
            display_difficulty_selector()

        # Create two columns for layout
        left_col, right_col = st.columns([3, 2])
        
        with right_col:
            # Display hangman image
            st.markdown(
                f'<div class="hangman-ascii">{HANGMAN_IMAGES[st.session_state.game_state.incorrect_attempts]}</div>',
                unsafe_allow_html=True
            )
            display_game_stats()
        
        with left_col:
            game_state = st.session_state.game_state
            
            # Display lives remaining
            st.markdown(
                f'<div class="lives-remaining">Lives remaining: {GameConfig.MAX_LIVES - game_state.incorrect_attempts}</div>',
                unsafe_allow_html=True
            )
            
            # Display word progress
            st.markdown(
                f'<div class="word-display">{" ".join(game_state.guessing_board)}</div>',
                unsafe_allow_html=True
            )
            
            # Display guessed letters
            if game_state.guessed_letters:
                guessed = sorted(game_state.guessed_letters)
                letter_badges = ''.join([
                    f'<span class="letter-badge {get_letter_badge_class(letter, game_state.word)}">{letter}</span>'
                    for letter in guessed
                ])
                st.markdown(
                    f'<div class="guessed-letters">Guessed letters: {letter_badges}</div>',
                    unsafe_allow_html=True
                )
            
            # Display game messages
            if game_state.message:
                st.markdown(
                    f'<div class="game-message-{game_state.message_type}">{game_state.message}</div>',
                    unsafe_allow_html=True
                )
            
            # Game over conditions
            if game_state.game_over:
                if game_state.game_won:
                    st.success('🎉 Congratulations! You won!')
                else:
                    st.error(f'💔 Game Over! The word was: {game_state.word}')
                
                if st.button("Play Again", key="new_game"):
                    st.session_state.game_state = None
                    st.rerun()
            else:
                # Game input form
                with st.form(key='guess_form', clear_on_submit=True):
                    col1, col2, col3 = st.columns([3, 2, 3])
                    with col2:
                        guess = st.text_input(
                            "Enter your guess",
                            max_chars=1,
                            key="guess_input",
                            placeholder="Type a letter",
                            label_visibility="collapsed"
                        )
                        submit_button = st.form_submit_button(
                            "Guess!",
                            use_container_width=True
                        )
                    
                    if submit_button or guess:
                        if process_guess(guess):
                            st.rerun()

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        st.error("Oops! Something went wrong. Please try refreshing the page.")

if __name__ == "__main__":
    main()