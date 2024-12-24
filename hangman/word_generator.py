import nltk
import os
import argparse
from collections import Counter

class WordGenerator:
    def __init__(self):
        # Download necessary NLTK resources
        nltk.download('brown')
        nltk.download('words')
        nltk.download('wordnet')
        nltk.download('gutenberg')
        nltk.download('reuters')

    def generate_word_list(self, word_type='common'):
        if word_type == 'common':
            return self.get_common_words()
        else:  # all words
            return self.get_all_words()

    def get_common_words(self):
        # Get words from Brown corpus and count their frequency
        brown_words = nltk.corpus.brown.words()
        reuters_words = nltk.corpus.reuters.words()
        
        # Combine words from both corpora
        all_words = list(brown_words) + list(reuters_words)
        word_freq = Counter(word.lower() for word in all_words)
        
        # Get words that appear at least 50 times (adjustable threshold)
        common_words = [word for word, freq in word_freq.items() if freq >= 50]
        
        # Filter words based on criteria
        filtered_common_words = self.filter_words(common_words)
        return filtered_common_words

    def get_all_words(self):
        # Get words from different corpora
        brown_words = set(nltk.corpus.brown.words())
        words_words = set(nltk.corpus.words.words())
        wordnet_words = set(nltk.corpus.wordnet.words())
        gutenberg_words = set(nltk.corpus.gutenberg.words())

        # Combine word lists
        word_list = list(brown_words | words_words | wordnet_words | gutenberg_words)
        
        # Filter words based on criteria
        filtered_word_list = self.filter_words(word_list)
        return filtered_word_list

    @staticmethod
    def filter_words(words):
        # Convert to lowercase and remove duplicates
        words = list(set(word.lower() for word in words))
        
        # Filter out words containing digits
        filtered_words = [word for word in words if word.isalpha()]
        
        # Filter out words with length less than 4 or greater than 12
        filtered_words = [word for word in filtered_words if 4 <= len(word) <= 12]
        
        # Filter out uncommon characters and non-English words (basic check)
        filtered_words = [word for word in filtered_words if all(ord(c) < 128 for c in word)]
        
        return filtered_words

    def download_wordbank(self, word_type='common', file_path='wordbank.txt'):
        try:
            # Remove existing wordbank if it exists
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed existing wordbank at {file_path}")
            
            word_list = self.generate_word_list(word_type)
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the word list to a file
            with open(file_path, 'w', encoding='utf-8') as file:
                for word in sorted(word_list):
                    file.write(word + '\n')

            print(f"Generated {len(word_list)} words")
            print(f"Wordbank saved to {file_path}")
            
        except OSError as e:
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description='Generate word bank for Hangman game')
    parser.add_argument('word_type', choices=['common', 'all'],
                      help='Type of words to generate: "common" for commonly used words, "all" for all words')
    parser.add_argument('--output', '-o', default='assets/wordbank.txt',
                      help='Output file path (default: assets/wordbank.txt)')

    args = parser.parse_args()

    # Get the script's directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    # Create full file path
    if not os.path.isabs(args.output):
        full_file_path = os.path.join(script_directory, args.output)
    else:
        full_file_path = args.output

    # Generate word bank
    word_generator = WordGenerator()
    word_generator.download_wordbank(args.word_type, full_file_path)

if __name__ == "__main__":
    main()
    

# Example 
# python word_generator.py common