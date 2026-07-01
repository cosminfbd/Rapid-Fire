SCORES_FILE = "leaderboard.txt"

def load_scores():
    scores = {}

    try:
        with open(SCORES_FILE, "r") as f:
            for line in f: # go through all users
                line = line.strip()
                if not line:
                    continue
                username, score = line.split(";")
                scores[username] = int(score)
    except FileNotFoundError:
        pass

    return scores

def save_scores(scores):
    with open(SCORES_FILE, "w", encoding="utf-8") as file:
        for username, highscore in scores.items():
            file.write(f"{username};{highscore}\n")

def get_highscore(username):
    scores = load_scores()
    return scores.get(username, 0)

def update_highscore(username, score):
    scores = load_scores()

    old_highscore = scores.get(username, 0)

    if score > old_highscore:
        scores[username] = score
        save_scores(scores)
        return score

    return old_highscore