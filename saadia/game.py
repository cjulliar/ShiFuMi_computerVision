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
        while True:
            if player1_hand == player2_hand:
                print("Egalité")
            elif player1_hand == "rock":
                if player2_hand == "scissors":
                    print(f"{self.player1.name} gagne")
                    self.player1.score += 1
                else:
                    print(f"{self.player2.name} gagne")
                    self.player2.score += 1

            elif player1_hand == "scissors":
                if player2_hand == "rock":
                    print(f"{self.player2.name} gagne")
                    self.player2.score += 1
                else:
                    print(f"{self.player1.name} gagne")
                    self.player1.score += 1
            elif player1_hand == "paper":
                if player2_hand == "rock":
                    print(f"{self.player1.name} gagne")
                    self.player1.score += 1
                else:
                    print(f"{self.player2.name} gagne")
                    self.player2.score += 1
            else:
                print("Gestes non reconnus, veuillez recommencer")

    def get_score(self):
            return f"Score: {self.player1.name}: {self.player1.score}, {self.player2.name}: {self.player2.score}"
                
            
            
            