from camera import VideoFrame, MyModel, VideoFrameWithPredictions, render_boxes_on_frame

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    
class Game:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        
    def play(self, player1_hand, player2_hand):
        result = ""
        round = 0
        for round in range(1):
            if player1_hand == player2_hand:
                result = "Egalité"
            elif player1_hand == "Pierre":
                if player2_hand == "Ciseaux":
                    result = f"{self.player1.name} gagne"
                    self.player1.score += 1
                else:
                    result = f"{self.player2.name} gagne"
                    self.player2.score += 1

            elif player1_hand == "Ciseaux":
                if player2_hand == "Pierre":
                    result = f"{self.player2.name} gagne"
                    self.player2.score += 1
                else:
                    result = f"{self.player1.name} gagne"
                    self.player1.score += 1
            elif player1_hand == "Feuille":
                if player2_hand == "Pierre":
                    result = f"{self.player1.name} gagne"
                    self.player1.score += 1
                else:
                    result = f"{self.player2.name} gagne"
                    self.player2.score += 1
            else:
                result = f"Gestes non reconnus, veuillez recommencer"
            round += 1
            return result

    def get_score(self):
            return f"Score: {self.player1.name}: {self.player1.score}, {self.player2.name}: {self.player2.score}"
                
            
            
            