from collections import namedtuple
import copy
from enum import Enum

from chess import parse_square

from Pieces import *

letters_to_index = {'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7}

index_to_names = {"p" : "Pion", "q" : "Reine", "n" : "Cavalier", "r" : "Tour", "k" : "Roi", "b" : "Fou"}

Color_tuple = namedtuple('Color', ['value', 'displayString'])

class Color(Enum):

    @property
    def displayString(self) -> str:
        return self.value.displayString
    
    BLACK = Color_tuple(0, "noirs")
    WHITE = Color_tuple(1, "blancs")
    
    @classmethod
    def get_by_name(cls, name) -> 'Color':
        for color in cls:
            if color.value.displayString == name:
                return color
        raise ValueError(f"No color with display string '{name}' found")

class Echequier:
    def __init__(self, game_id : int, channel_id : int) -> None:
        self.game_id = game_id
        self.channel_id = channel_id

        self.table = [['.' for _ in range(8)] for _ in range(8)]
        
    def init_echec(self) -> None:
        self.add_piece(Rook("A8", Color.BLACK, self))
        self.add_piece(Knight("B8", Color.BLACK, self))
        self.add_piece(Bishop("C8", Color.BLACK, self))
        self.add_piece(Queen("D8", Color.BLACK, self))
        self.add_piece(King("E8", Color.BLACK, self))
        self.add_piece(Bishop("F8", Color.BLACK, self))
        self.add_piece(Knight("G8", Color.BLACK, self))
        self.add_piece(Rook("H8", Color.BLACK, self))

        i = 0
        for key in letters_to_index.keys():
            self.add_piece(Pawn(str(key) + "7", Color.BLACK, self))
            self.add_piece(Pawn(str(key) + "2", Color.WHITE, self))
            i+=1

        self.add_piece(Rook("A1", Color.WHITE, self))
        self.add_piece(Knight("B1", Color.WHITE, self))
        self.add_piece(Bishop("C1", Color.WHITE, self))
        self.add_piece(Queen("D1", Color.WHITE, self))
        self.add_piece(King("E1", Color.WHITE, self))
        self.add_piece(Bishop("F1", Color.WHITE, self))
        self.add_piece(Knight("G1", Color.WHITE, self))
        self.add_piece(Rook("H1", Color.WHITE, self))  

    def add_piece(self, piece : Piece) -> None:
        pos_x = letters_to_index[piece.position[0]]
        pos_y = 8 - int(piece.position[1])

        self.table[pos_y][pos_x] = piece

    def get_piece(self, position : str) -> Piece:
        pos_x = letters_to_index[position[0]]
        pos_y = 8 - int(position[1])

        return self.table[pos_y][pos_x]
    
    def has_piece(self, position : str) -> bool:
        pos_x = letters_to_index[position[0]]
        pos_y = 8 - int(position[1])

        return isinstance(self.table[pos_y][pos_x], Piece)
    
    # raw_table c'est pour l'utiliser dans l'api chess.Board super important. convertir l'echequier en un format adapté pour l'api  
    def get_raw_table(self) -> str:
        raw_table = ""

        for line in self.table:

            counter = 0

            for piece in line:
                if piece == ".":
                    counter+=1
                else:
                    if counter != 0:
                        raw_table+=str(counter)
                        counter=0
                    raw_table+=str(piece)

            if counter != 0:
                raw_table+=str(counter)
                counter=0
            raw_table+="/"

        return raw_table[:-1]
    
    # même concepte que le raw_table, pour avoir la liste des coups possible converti via l'api chess.Board
    def get_raw_mouvement(self, piece : Piece) -> dict:
        foresee_move = piece.get_foresee_move()

        moves = []
        attacks = []

        i = 1

        # Algorithme pour mettre sur le schéma la commande /mouvement <case>
        i = 8
        for y in foresee_move:
            p = 0
            for x in y:
                if x == 1:
                    moves.append(parse_square(str(list(letters_to_index.keys())[list(letters_to_index.values()).index(p)].lower() + str(i))))
                elif x == 2:
                    attacks.append(parse_square(str(list(letters_to_index.keys())[list(letters_to_index.values()).index(p)].lower() + str(i))))
                p+=1
            i-=1

        return dict.fromkeys(moves, "#808000") | dict.fromkeys(attacks, "#cc0000cc")
    

    def reverse_echequier(self) -> None:
        reverse = []
        for line in self.table[::-1]:
            reverse.append(line[::-1])


        for line_reverse in reverse:
            for piece in line_reverse:
                if isinstance(piece,Piece):
                    ligne, colonne = int(piece.position[1]) - 1, letters_to_index[piece.position[0]]
                    piece.position = chr(ord('A') + (7 - colonne)) + str(8 - ligne)


        self.table = reverse

    
    def is_in_echec(self, piece : Piece, target_position : str) -> bool:

        # On fait une deep copy de l'echequier pour vérifie si il ne se met pas en echec tout seul (On simule le coup puis on voit tous les prochains coups des ennemies)
        echequier_copy = copy.deepcopy(self)

        echequier_copy.get_piece(piece.position).move(target_position)

        echequier_copy.reverse_echequier()

        for line in echequier_copy.table:
            for piece_ennemy in line:
                if piece.is_ennemy(piece_ennemy):
                    foresee_move = piece_ennemy.get_foresee_move()
                    i = 8
                    for y in foresee_move:
                        p = 0
                        for x in y:
                            if x == 2:
                                if isinstance(echequier_copy.get_piece(str(list(letters_to_index.keys())[list(letters_to_index.values()).index(p)] + str(i))), King):
                                    return True
                            p+=1
                        i-=1
        return False
    
    def is_checkmate(self, piece_attacker : Piece):
        # A ce moment la, on a besoin de retourner l'echequier pour vérifier la pov de l'autre si il est echec et mat ou non.
            self.reverse_echequier()
            
            king_ennemy = None

            # On récupère le roi ennemie
            for line in self.table:
                for piece_ennemy in line:
                    if piece_attacker.is_ennemy(piece_ennemy) and isinstance(piece_ennemy, King):
                        king_ennemy = piece_ennemy
                        

            # On prend les coordoonées opposés du roi pour match
    
            checkmate = self.is_in_echec(king_ennemy, king_ennemy.position)

            # on check ses positions possibles et si y'en a une qui n'est pas en echec la partie continue
        
            i = 8
            for y in king_ennemy.get_foresee_move():
                p = 0

                if not checkmate: 
                        break
                
                for x in y:
                    if x == 2 or x == 1:
                        if not self.is_in_echec(king_ennemy, str(list(ChessGame.letters_to_index.keys())[list(ChessGame.letters_to_index.values()).index(p)] + str(i))):
                            checkmate = False
                            break
                    p+=1
                i-=1

         

            # Le roi n'a pas de possibilité, on vérifie d'abord si une pièce peut manger la pièce qui met le roi en echec
            if checkmate:
                echequier_copy = copy.deepcopy(self)

                pieces_ennemy = [element for ligne in echequier_copy.table for element in ligne if element != "." and element.is_ennemy(piece_attacker)]

                pos_x = ChessGame.letters_to_index[piece_attacker.position[0]]
                pos_y = 8 - int(piece_attacker.position[1])
                
                for piece_ennemy in pieces_ennemy:
                    if piece_ennemy.get_foresee_move()[pos_y][pos_x] == 2:
                        checkmate = False
                        break

                # Aucunes pièces n'a pu avoir la possibilité de manger la pièce qui met le roi en echec, maintenant on va regarder si une pièce peut barrer la route
                # Donc on va faire bouger les pièces à toutes les positions où elles peuvent (pas très opti mais j'ai pas trouvé mieux)
                # et on regarde si le roi est encore en echec.
                
                if checkmate:
                    for piece_ennemy in pieces_ennemy:
                        position_inital = copy.deepcopy(piece_ennemy.position)
                        i = 8
                        for y in piece_ennemy.get_foresee_move():
                            p = 0

                            if checkmate: 
                                    break
                            
                            for x in y:
                                if x == 2 or x == 1:
                                    if not isinstance(piece_ennemy, King):
                                        piece_ennemy.move(str(list(ChessGame.letters_to_index.keys())[list(ChessGame.letters_to_index.values()).index(p)] + str(i)))
                                        if not echequier_copy.is_in_echec(king_ennemy, king_ennemy.position):
                                            checkmate = False
                                            break
                                p+=1
                            i-=1
                        # Si on le remet pas à sa position inital, ça va casser tout le système. Une pièce par pièce pour vérifier.
                        piece_ennemy.move(position_inital)

            # FIN VERIFICATION ECHEC ET MAT

            #On revient à la normal
            self.reverse_echequier()

            return checkmate

    def todict(self) -> dict :
            
            pieces = [element.tolist() for ligne in self.table for element in ligne if element != "."]
            
            #print(pieces)
            
            return {
                "id" : self.game_id,
                "channel_id" : self.channel_id,
                "pieces" : pieces,
            }
