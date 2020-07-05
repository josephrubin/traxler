import random
import string


# URL safe characters without vowels (we try not to spell words).
ALPHABET = ''.join([c for c in string.ascii_letters + string.digits
                    if c not in 'aeiouAEIOU'])


def id(length=18):
    """Create a random, probabilistically unique string."""
    return ''.join(random.choice(ALPHABET) for _ in range(length))
