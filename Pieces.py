
import ChessGame

class Piece:
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier', type : str = ""):
        self.position = position
        self.color = color
        self.echequier = echequier
        self.type = type
        self.first_move = True

    def get_foresee_move(self) -> list:
        pass

    def move(self, position_target : str) -> None:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])

        target_pos_x = ChessGame.letters_to_index[position_target[0]]
        target_pos_y = 8 - int(position_target[1])


        response_target = self.get_foresee_move()[target_pos_y][target_pos_x]


        # On vérifie qu'il peut bien se déplacer / manger
        # FAIRE UN RESPONSE_TARGET AVEC 3, CELA VOUDRA DIRE QUE C'EST LE SWAP ENTRE LE ROI ET UNE TOUR
        if response_target == 1 or response_target == 2:
            self.echequier.table[target_pos_y][target_pos_x] = self
            self.echequier.table[pos_y][pos_x] = "."
            self.position = position_target

            if self.first_move:
                self.first_move = False

    def is_ennemy(self, piece : 'ChessGame.Piece') -> bool:
        return piece != "." and self.color != piece.color
    
    def tolist(self) -> dict:
        return [
            self.type,
            self.position,
            self.color.displayString,
            self.first_move
        ]


class Pawn(Piece):
    
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier

        super().__init__(position, color, echequier, "pawn")

    def __str__(self) -> str:
        return "P" if self.color == ChessGame.Color.WHITE else "p"

    def __repr__(self) -> str:
        return "P" if self.color == ChessGame.Color.WHITE else "p"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])


        table_possibility = [[0 for i in range(8)] for j in range(8)]


        # la variable pos c'est la position qu'on regarde pour voir si il y a possibilité de mouvement
        
        if pos_x-1 >= 0 and pos_y-1 >= 0: # On check les débordements
            pos_target = self.echequier.table[pos_y-1][pos_x-1]
            if self.is_ennemy(pos_target): # il y a un pion ennemie
                table_possibility[pos_y-1][pos_x-1]= 2 # ajouter à la matrice un "1" comme possibilité

        if pos_x+1 <= 7 and pos_y-1 >=0: # On check les débordements
            pos_target = self.echequier.table[pos_y-1][pos_x+1]

            if self.is_ennemy(pos_target): # il y a un pion ennemie
                table_possibility[pos_y-1][pos_x+1] = 2 # ajouter à la matrice un "1" comme possibilité


        if pos_y-1 >= 0: # On check les débordements

            pos_target = self.echequier.table[pos_y-1][pos_x] # Avancer tout droit

            if pos_target == ".":
                table_possibility[pos_y-1][pos_x] = 1 # ajouter à la matrice "1" comme possibilité
            
                if self.first_move:
                    pos_target = self.echequier.table[pos_y-2][pos_x]
                    if pos_target == ".":
                        table_possibility[pos_y-2][pos_x] = 1 # ajouter à la matrice "1" comme possibilité
                    
        return table_possibility

class Rook(Piece):
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier
        
        super().__init__(position, color, echequier, "rook")


    def __str__(self) -> str:
        return "R" if self.color == ChessGame.Color.WHITE else "r"

    def __repr__(self) -> str:
        return "R" if self.color == ChessGame.Color.WHITE else "r"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])

        table_possibility = [[0 for _ in range(8)] for _ in range(8)]


        # la variable pos c'est la position qu'on regarde pour voir si il y a possibilité de mouvement
        for i in range(pos_y+1, 8):
            pos = self.echequier.table[i][pos_x]
            if pos == '.':
                table_possibility[i][pos_x] = 1
            elif self.is_ennemy(pos):
                table_possibility[i][pos_x] = 2
                break
            else: 
                break
           
        for i in range(pos_y-1, -1,-1):
            pos = self.echequier.table[i][pos_x]
            if pos == '.':
                table_possibility[i][pos_x] = 1
            elif self.is_ennemy(pos):
                table_possibility[i][pos_x] = 2
                break
            else: 
                break
            
        for i in range(pos_x+1, 8):
            pos = self.echequier.table[pos_y][i]
            if pos == '.':
                table_possibility[pos_y][i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y][i] = 2
                break
            else: 
                break
            
        for i in range(pos_x-1, -1,-1):
            pos = self.echequier.table[pos_y][i]
            if pos == '.':
                table_possibility[pos_y][i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y][i] = 2
                break
            else: 
                break
        
        return table_possibility
    
class Bishop(Piece):
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier

        super().__init__(position, color, echequier, "bishop")



    def __str__(self) -> str:
        return "B" if self.color == ChessGame.Color.WHITE else "b"

    def __repr__(self) -> str:
        return "B" if self.color == ChessGame.Color.WHITE else "b"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])

        table_possibility = [[0 for _ in range(8)] for _ in range(8)]

        pos_min_ld = min(pos_x, 7-pos_y)     # diagonal bas gauche
        
        for i in range(1,pos_min_ld+1):
            pos = self.echequier.table[pos_y+i][pos_x-i]
            if pos == '.':
                table_possibility[pos_y+i][pos_x-i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y+i][pos_x-i] = 2
                break
            else: 
                break
        
        pos_min_lu = min(pos_x, pos_y)     # diagonal haut gauche

        for i in range(1,pos_min_lu+1):
            pos = self.echequier.table[pos_y-i][pos_x-i]
            if pos == '.':
                table_possibility[pos_y-i][pos_x-i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y-i][pos_x-i] = 2
                break
            else: 
                break
        
        pos_min_rd = min(7-pos_x, pos_y)     # diagonal droite bas

        for i in range(1,pos_min_rd+1):
            pos = self.echequier.table[pos_y-i][pos_x+i]
            if pos == '.':
                table_possibility[pos_y-i][pos_x+i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y-i][pos_x+i] = 2
                break
            else: 
                break
        
        pos_min_rd = min(7-pos_x, 7-pos_y)     # diagonal droite haut
        for i in range(1,pos_min_rd+1):
            pos = self.echequier.table[pos_y+i][pos_x+i]
            if pos == '.':
                table_possibility[pos_y+i][pos_x+i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y+i][pos_x+i] = 2
                break
            else: 
                break
            
        return table_possibility
    
class Queen(Piece):
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier

        super().__init__(position, color, echequier, "queen")


    def __str__(self) -> str:
        return "Q" if self.color == ChessGame.Color.WHITE else "q"

    def __repr__(self) -> str:
        return "Q" if self.color == ChessGame.Color.WHITE else "q"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])

        table_possibility = [[0 for _ in range(8)] for _ in range(8)]

# la variable pos c'est la position qu'on regarde pour voir si il y a possibilité de mouvement
        for i in range(pos_y+1, 8):
            pos = self.echequier.table[i][pos_x]
            if pos == '.':
                table_possibility[i][pos_x] = 1
            elif self.is_ennemy(pos):
                table_possibility[i][pos_x] = 2
                break
            else: 
                break
           
        for i in range(pos_y-1, -1,-1):
            pos = self.echequier.table[i][pos_x]
            if pos == '.':
                table_possibility[i][pos_x] = 1
            elif self.is_ennemy(pos):
                table_possibility[i][pos_x] = 2
                break
            else: 
                break
            
        for i in range(pos_x+1, 8):
            pos = self.echequier.table[pos_y][i]
            if pos == '.':
                table_possibility[pos_y][i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y][i] = 2
                break
            else: 
                break
            
        for i in range(pos_x-1, -1,-1):
            pos = self.echequier.table[pos_y][i]
            if pos == '.':
                table_possibility[pos_y][i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y][i] = 2
                break
            else: 
                break
            
        pos_min_ld = min(pos_x, 7-pos_y)     # diagonal bas gauche
        
        for i in range(1,pos_min_ld+1):
            pos = self.echequier.table[pos_y+i][pos_x-i]
            if pos == '.':
                table_possibility[pos_y+i][pos_x-i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y+i][pos_x-i] = 2
                break
            else: 
                break
        
        pos_min_lu = min(pos_x, pos_y)     # diagonal haut gauche

        for i in range(1,pos_min_lu+1):
            pos = self.echequier.table[pos_y-i][pos_x-i]
            if pos == '.':
                table_possibility[pos_y-i][pos_x-i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y-i][pos_x-i] = 2
                break
            else: 
                break
        
        pos_min_rd = min(7-pos_x, pos_y)     # diagonal droite bas

        for i in range(1,pos_min_rd+1):
            pos = self.echequier.table[pos_y-i][pos_x+i]
            if pos == '.':
                table_possibility[pos_y-i][pos_x+i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y-i][pos_x+i] = 2
                break
            else: # Il y a 
                break
        
        pos_min_rd = min(7-pos_x, 7-pos_y)     # diagonal droite haut
        for i in range(1,pos_min_rd+1):
            pos = self.echequier.table[pos_y+i][pos_x+i]
            if pos == '.':
                table_possibility[pos_y+i][pos_x+i] = 1
            elif self.is_ennemy(pos):
                table_possibility[pos_y+i][pos_x+i] = 2
                break
            else: 
                break
            
        return table_possibility

class King(Piece):
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier

        super().__init__(position, color, echequier, "king")

    def __str__(self) -> str:
        return "K" if self.color == ChessGame.Color.WHITE else "k"

    def __repr__(self) -> str:
        return "K" if self.color == ChessGame.Color.WHITE else "k"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])

        table_possibility = [[0 for _ in range(8)] for _ in range(8)]


        # la variable pos c'est la position qu'on regarde pour voir si il y a possibilité de mouvement
    
        if pos_x-1 >= 0:
            if pos_y+1 <= 7: # On check les débordements
                pos = self.echequier.table[pos_y+1][pos_x-1]
                ennemy = self.is_ennemy(pos)
                table_possibility[pos_y+1][pos_x-1] = 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité
            
            if pos_y-1 >= 0: # On check les débordements
                pos = self.echequier.table[pos_y-1][pos_x-1]
                ennemy = self.is_ennemy(pos)
                table_possibility[pos_y-1][pos_x-1]= 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité

            pos = self.echequier.table[pos_y][pos_x-1]
            ennemy = self.is_ennemy(pos)
            table_possibility[pos_y][pos_x-1] = 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité


        if pos_x+1 <= 7:
            if pos_y+1 <= 7: # On check les débordements
                pos = self.echequier.table[pos_y+1][pos_x+1]
                ennemy = self.is_ennemy(pos)
                table_possibility[pos_y+1][pos_x+1] = 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité
        
            if pos_y-1 >=0: # On check les débordements
                pos = self.echequier.table[pos_y-1][pos_x+1]
                ennemy = self.is_ennemy(pos)
                table_possibility[pos_y-1][pos_x+1]= 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité

            pos = self.echequier.table[pos_y][pos_x+1]
            ennemy = str(pos.__str__()).isupper()
            table_possibility[pos_y][pos_x+1]= 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité

        if pos_y+1 <= 7:
            pos = self.echequier.table[pos_y+1][pos_x]
            ennemy = self.is_ennemy(pos)
            table_possibility[pos_y+1][pos_x]= 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité

        if pos_y-1 >= 0:
            pos = self.echequier.table[pos_y-1][pos_x]
            ennemy = self.is_ennemy(pos)
            table_possibility[pos_y-1][pos_x]= 2 if ennemy else 1 if pos == "." else 0 # ajouter à la matrice un "1" comme possibilité
       
  
        return table_possibility

class Knight(Piece):
    def __init__(self, position : str, color : 'ChessGame.Color', echequier : 'ChessGame.Echequier') -> None:
        self.position = position
        self.color = color
        self.echequier = echequier

        super().__init__(position, color, echequier, "knight")

    def __str__(self) -> str:
        return "N" if self.color == ChessGame.Color.WHITE else "n"
 
    def __repr__(self) -> str:
        return "N" if self.color == ChessGame.Color.WHITE else "n"
        
    def get_foresee_move(self) -> list:
        pos_x = ChessGame.letters_to_index[self.position[0]]
        pos_y = 8 - int(self.position[1])
  
        table_possibility = [[0 for _ in range(8)] for _ in range(8)]
 
        if 0<=pos_y+2 and pos_y+2<=7:
            if 0<=pos_x+1 and pos_x+1<=7:
                pos = self.echequier.table[pos_y+2][pos_x+1]
                if pos == '.':
                    table_possibility[pos_y+2][pos_x+1]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y+2][pos_x+1]= 2
            if 0<=pos_x-1 and pos_x-1<=7:
                pos = self.echequier.table[pos_y+2][pos_x-1]
                if pos == '.':
                    table_possibility[pos_y+2][pos_x-1]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y+2][pos_x-1]= 2
 
        if 0<=pos_y-2 and pos_y-2<=7:
            if 0<=pos_x+1 and pos_x+1 <=7:
                pos = self.echequier.table[pos_y-2][pos_x+1]
                if pos == '.':
                    table_possibility[pos_y-2][pos_x+1]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y-2][pos_x+1]= 2
            if 0<=pos_x-1 and pos_x-1 <=7:
                pos = self.echequier.table[pos_y-2][pos_x-1]
                if pos == '.':
                    table_possibility[pos_y-2][pos_x-1]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y-2][pos_x-1]= 2
 
        if 0<=pos_x+2 and pos_x+2<=7:
            if 0<=pos_y+1 and pos_y+1<=7:
                pos = self.echequier.table[pos_y+1][pos_x+2]
                if pos == '.':
                    table_possibility[pos_y+1][pos_x+2]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y+1][pos_x+2]= 2
            if 0<=pos_y-1 and pos_y-1<=7:
                pos = self.echequier.table[pos_y-1][pos_x+2]
                if pos == '.':
                    table_possibility[pos_y-1][pos_x+2]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y-1][pos_x+2]= 2
 
        if 0<=pos_x-2 and pos_x-2<=7:
            if 0<=pos_y+1 and pos_y+1<=7:
                pos = self.echequier.table[pos_y+1][pos_x-2]
                if pos == '.':
                    table_possibility[pos_y+1][pos_x-2]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y+1][pos_x-2]= 2
            if 0<=pos_x-1 and pos_y-1 <=7:
                pos = self.echequier.table[pos_y-1][pos_x-2]
                if pos == '.':
                    table_possibility[pos_y-1][pos_x-2]= 1
                elif self.is_ennemy(pos):
                    table_possibility[pos_y-1][pos_x-2]= 2
        return table_possibility
