# We can't afford to use any randomizers in calculating 
# experience, becuase of processing speed reasons.
# This is because randomizer functions are significantly slow
# and should be used sparingly.

from config import EXP_PER_MESSAGE


def message_to_xp(raw_message):
    words_in_message = raw_message.split()
    words_filtered = len([word for word in words_in_message if len(word) > 3])
    return words_filtered ^ MESSAGE_EXP_FACTOR
