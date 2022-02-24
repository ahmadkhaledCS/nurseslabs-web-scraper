class Question:
    def __init__(self, text, answers, rationals, right_answer=None):
        self.text = text
        self.answers = answers
        self.rationals = rationals
        self.right_answer = right_answer

    def set_rationals(self):
        text = self.rationals
        text = text.split('\n')[2:]
        try:
            self.right_answer.rational = text[0].split(':')[-1]
            text = text[1:]
            for t in text:
                for a in self.answers:
                    if a.letter in t.split(':')[0]:
                        a.rational = t.split(':')[-1]
        except:
            return


class Answer:
    def __init__(self, text=None, letter=None, status=None, rational=None):
        self.text = text
        self.letter = letter
        self.rational = rational
        self.status = status
