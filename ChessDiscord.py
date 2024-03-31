import discord
from discord import app_commands

import aspose.words as aw
import chess
import chess.svg

import ChessGame
from Pieces import *

from ChessSQL import SQLite

import random

import os

import re

import json

games = {}

game_id_increment = 0

chess_sql = SQLite("chess.db")


class MyClient(discord.Client):

    async def on_ready(self):
        print(f'Logged on as {self.user}!')
        #await tree.sync(guild=discord.Object(id=GUILD_ID)) #sync commands

        # Ici load les echequiers
        await load_games(chess_sql, self)    

intents = discord.Intents.default()
intents.message_content = True


client = MyClient(intents=intents)
tree = app_commands.CommandTree(client)


token = '' # Change me

GUILD_ID = 1166350080106827798 # Change me
PARTIES_CATEGORY_ID = 1185276222528303215 # Change me

    
class User:
    def __init__(self, discord_id, color : ChessGame.Color, points=0) -> None:
        self.discord_id = discord_id
        self.color = color
        self.points = points
        pass

    def todict(self) -> str :
            return {
                "discord_id" : self.discord_id,
                "color" : self.color.displayString,
                "points" : self.points,
            }

class Game:
    def __init__(self, channel_id : int, user_1 : User, user_2 : User, game_id : int = 0 , color_playing : ChessGame.Color = ChessGame.Color.WHITE, winner : str = "") -> None:
        self.game_id = game_id
        self.channel_id = channel_id
        self.user_1 = user_1
        self.user_2 = user_2    
        self.echequier = ChessGame.Echequier(game_id, channel_id)
        self.color_playing = color_playing        
        self.winner = winner

    def todict(self) -> dict :
            return {
                "id" : self.game_id,
                "channel_id" : self.channel_id,
                "color_playing" : self.color_playing.displayString,
                "user_1" : self.user_1.todict(),
                "user_2" : self.user_2.todict(),
                "winner" : self.winner
            }




@tree.command(name = "help", description = "Afficher les commandes", guild=discord.Object(id=GUILD_ID)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def command_help(ctx : discord.Interaction) -> None:
    
    message = "Voici les commandes : \n- /play <user> (Jouer contre un utilisateur) \n- /mouvement <position> (Affiche les mouvements d'une pièce dans une partie) \n- /deplacer <position> <futur_position> (Déplacer une pièce à un endroit dans une partie) \n- /abandonner (Abandonner la partie en cours)"
    await ctx.response.send_message(message)


@tree.command(name = "abandonner", description = "Abandonner une partie", guild=discord.Object(id=GUILD_ID)) 
async def command_forfeit(ctx : discord.Interaction) -> None:
    channel = ctx.channel
    author_member = ctx.user
    

    if channel.category_id == PARTIES_CATEGORY_ID and str(channel.id) in games.keys():
        game = games.get(str(channel.id))

        if game.user_1.discord_id != author_member.id and game.user_2.discord_id != author_member.id:
            await ctx.response.send_message("Vous n'êtes pas un participant !", ephemeral=True)
            return
        

        user_1 = await client.fetch_user(game.user_1.discord_id)
        user_2 = await client.fetch_user(game.user_2.discord_id)
                
            
        await channel.set_permissions(user_1,send_messages=False)
        await channel.set_permissions(user_2,send_messages=False)

        winner_name = user_1.name if game.user_1.discord_id != author_member.id  else user_2.name  

        game.winner = winner_name

        chess_sql.update_by_id(game.todict(), "games", game.game_id)
        
        del games[str(game.channel_id)]

        await ctx.response.send_message(f"{author_member.name} a abandonné la partie ! La victoire revient à {winner_name} !")


    else:
        await ctx.response.send_message("Cette commande est réservée en partie.", ephemeral=True)
        
@tree.command(name = "deplacer", description = "Déplacer une pièce", guild=discord.Object(id=GUILD_ID)) 
async def command_move(ctx : discord.Interaction, case_position : str, case_target_position : str) -> None:
    channel = ctx.channel
    author_member = ctx.user
    
    # On upper() pour supporter les minuscules sans se prendre la tête
    case_position = case_position.upper()
    case_target_position = case_target_position.upper()

    if channel.category_id == PARTIES_CATEGORY_ID and str(channel.id) in games.keys():
        game = games.get(str(channel.id))

        if not validate_chess_move_format(case_position) or not validate_chess_move_format(case_target_position):
            await ctx.response.send_message("Veuillez saisir des positions valides !")
            return
        
        if game.user_1.discord_id == author_member.id and game.user_1.color == game.color_playing:
            await process_mouvement(ctx, game, game.user_1, case_position, case_target_position)
        elif game.user_2.discord_id == author_member.id and game.user_2.color == game.color_playing:
            await process_mouvement(ctx, game, game.user_2, case_position, case_target_position)
        else:
            await ctx.response.send_message("Ce n'est pas votre tour !")
            return
                
    else:
        await ctx.response.send_message("Cette commande est réservée en partie.")

@tree.command(name = "mouvements", description = "Afficher les mouvements d'une pièce", guild=discord.Object(id=GUILD_ID)) 
async def command_foresee(ctx : discord.Interaction, position : str) -> None:
    
    channel = ctx.channel
    author_member = ctx.user
    
    # On upper() pour supporter les minuscules sans se prendre la tête
    position = position.upper()

    if channel.category_id == PARTIES_CATEGORY_ID and str(channel.id) in games.keys():
        game = games.get(str(channel.id))

        if not validate_chess_move_format(position):
            await ctx.response.send_message("Veuillez saisir une position valide !")
            return
        if game.user_1.discord_id == author_member.id and game.user_1.color == game.color_playing:
            await process_foresee(ctx, game, game.user_1, position)
        elif game.user_2.discord_id == author_member.id and game.user_2.color == game.color_playing:
            await process_foresee(ctx, game, game.user_2, position)
        else:
            await ctx.response.send_message("Ce n'est pas votre tour !")
            return
        
        # discord.errors.InteractionResponded: This interaction has already been responded to before
        await ctx.response.send_message(content='Prédiction de la pièce ' + position + ".", ephemeral=True)
        
    else:
        await ctx.response.send_message("Cette commande est réservée en partie.")


@tree.command(name = "promotion", description = "Promouvoir un pion", guild=discord.Object(id=GUILD_ID)) 
@app_commands.choices(choices=[
        app_commands.Choice(name="Reine", value="queen"),
        app_commands.Choice(name="Cavalier", value="knight"),
        app_commands.Choice(name="Fou", value="bishop"),
        app_commands.Choice(name="Tour", value="rook"),
        ])
async def command_foresee(ctx : discord.Interaction, position : str, position_target : str, choices: app_commands.Choice[str]) -> None:
    
    channel = ctx.channel
    author_member = ctx.user
    
    # On upper() pour supporter les minuscules sans se prendre la tête
    position = position.upper()
    position_target = position_target.upper()

    if channel.category_id == PARTIES_CATEGORY_ID and str(channel.id) in games.keys():
        game = games.get(str(channel.id))

        if not validate_chess_move_format(position) or not validate_chess_move_format(position_target):
            await ctx.response.send_message("Veuillez saisir une position valide !")
            return
        
        if game.user_1.discord_id == author_member.id and game.user_1.color == game.color_playing:
            await process_promotion(ctx, game, game.user_1, position, position_target, choices.value)
        elif game.user_2.discord_id == author_member.id and game.user_2.color == game.color_playing:
            await process_promotion(ctx, game, game.user_2, position, position_target, choices.value)
        else:
            await ctx.response.send_message("Ce n'est pas votre tour !")
            return
       
        
    else:
        await ctx.response.send_message("Cette commande est réservée en partie.")

@tree.command(name = "play", description = "Jouer contre un joueur", guild=discord.Object(id=GUILD_ID)) 
async def command_play(ctx : discord.Interaction, opponent: discord.Member) -> None:

    category = discord.utils.get(ctx.guild.categories, id=PARTIES_CATEGORY_ID)

    if category is None:
        # La catégorie n'a pas été trouvée
        await ctx.response.send_message("Catégorie introuvable.")
        return
    
    
    # Récupère les objets Member pour l'auteur et le joueur mentionné
    author_member = ctx.user
    opponent_member = opponent

    if author_member and opponent_member:

        if opponent_member == client.user:
            await ctx.response.send_message("Désolé ! Je ne possède pas encore d'IA.")
            return

        if author_member == opponent_member:
            await ctx.response.send_message("Vous n'allez pas jouer contre vous mêmes !")
        else:
            # Crée le nom du salon

            channel_name = f'Partie-Echec-{chess_sql.get_next_id()}'

            # Crée le salon dans la catégorie spécifiée
            new_channel = await category.create_text_channel(channel_name)

            # Autorise uniquement l'auteur et le joueur mentionné à accéder au salon
            await new_channel.set_permissions(author_member, read_messages=True, send_messages=True)
            await new_channel.set_permissions(opponent_member, read_messages=True, send_messages=True)

            # Autorise le bot à lire et envoyer des messages
            await new_channel.set_permissions(ctx.guild.me, read_messages=True, send_messages=True)

            # Refuse l'accès d'écriture aux autres membres
            await new_channel.set_permissions(ctx.guild.default_role, send_messages=False)


            # Répond avec un message confirmant la création du salon

            await ctx.response.defer()
            #asyncio.sleep()
            await ctx.followup.send(f"Le salon {new_channel.mention} a été créé. Bonne partie! {author_member.mention} VS {opponent_member.mention}")

            colors = [ChessGame.Color.WHITE, ChessGame.Color.BLACK]
            random.shuffle(colors) 

            new_game = Game(new_channel.id, User(author_member.id, colors[0]), User(opponent_member.id, colors[1]), chess_sql.get_next_id())

            new_game.echequier.init_echec()

            games[str(new_channel.id)] = new_game

            chess_sql.add_game(new_game)
            chess_sql.add_echequier(new_game.echequier)

            if new_game.user_1.color == ChessGame.Color.WHITE:
                await new_channel.send(f"{author_member.mention} a été choisi pour jouer les blancs, il commence donc en premier !")
            else:
                await new_channel.send(f"{opponent_member.mention} a été choisi pour jouer les blancs, il commence donc en premier !")
            
            await send_chess_image(new_game)

    else:
        await ctx.response.send_message("Erreur lors de la récupération des membres. Opération avortée")




async def process_promotion(ctx : discord.Interaction, game : Game, user : User, position : str, target_position : str, promotion : str) -> None:
    """ Fonction qui:
            vérifie que la pièce existe
            que c'est bien un pion
            qu'il est bien en X7
            
            que le mouvement est possible (si il peut graille en même temps y'a pas de soucis)
    """

    if not game.echequier.has_piece(position):
        await ctx.response.send_message("Il n'y a pas de pion à cette case !")
        return
    
    piece = game.echequier.get_piece(position)

    if piece.color != user.color:
        await ctx.response.send_message("Ce n'est pas votre pièce !") 
        return

    if not isinstance(piece, Pawn):
        await ctx.response.send_message("Ce n'est pas un pion !") 
        return
    

    next_pos_x = ChessGame.letters_to_index[target_position[0]]
    next_pos_y = 8 - int(target_position[1])
        
    result = piece.get_foresee_move()[next_pos_y][next_pos_x]
    
    response = ""

    if result == 0:
        await ctx.response.send_message("Votre pièce ne peut pas se déplacer ici pour promouvoir !") 
        return
    
    if result == 2:
        piece_ennemy_eaten = game.echequier.get_piece(target_position)

        response+= f"\n{ChessGame.index_to_names.get(str(piece_ennemy_eaten).lower())} ({piece_ennemy_eaten.color.displayString}) mangé par {ChessGame.index_to_names.get(str(piece).lower())} ({piece.color.displayString}) !\n"

    piece.move(target_position)
    
    match promotion:
        case "queen":
            piece = Queen(piece.position, piece.color, piece.echequier)
        case "bishop":
            piece = Bishop(piece.position, piece.color, piece.echequier)
        case "rook":
            piece = Rook(piece.position, piece.color, piece.echequier)
        case "knight":
            piece = Knight(piece.position, piece.color, piece.echequier)

    
    piece.first_move = False

    game.echequier.add_piece(piece)


    response += f"Pion {target_position} promouvoie en {ChessGame.index_to_names.get(str(piece).lower())} !"

    if game.echequier.is_checkmate(piece):
        channel_game = ctx.guild.get_channel(game.channel_id)
        
        user_1 = await client.fetch_user(game.user_1.discord_id)
        user_2 = await client.fetch_user(game.user_2.discord_id)

        winner_name = user_1.name if game.user_1.color == game.color_playing else user_2.name

        game.winner = winner_name
        
        await channel_game.set_permissions(user_1,send_messages=False)
        await channel_game.set_permissions(user_2,send_messages=False)
        await ctx.response.send_message(response + f"\nEchec et mat ! Les {game.color_playing.displayString} l'emportent ! ({winner_name})")
        chess_sql.update_by_id(game.todict(), "games", game.game_id)
        chess_sql.update_by_id(game.echequier.todict(), "echequiers", game.game_id)
        await send_chess_image(game)
        return
        
    await ctx.response.send_message(response + f"\nAu tour des {next_color(ChessGame.Color, game.color_playing).displayString} de jouer !")

    game.color_playing = next_color(ChessGame.Color, game.color_playing)

    game.echequier.reverse_echequier()

    chess_sql.update_by_id(game.todict(), "games", game.game_id)
    chess_sql.update_by_id(game.echequier.todict(), "echequiers", game.game_id)
    await send_chess_image(game)


async def process_foresee(ctx : discord.Interaction, game : Game, user : User, position : str) -> None:
    if not game.echequier.has_piece(position):
        await ctx.response.send_message("Il n'y a pas de pièce à cette case !")
        return
    
    piece = game.echequier.get_piece(position)

    if piece.color != user.color:
        await ctx.response.send_message("Ce n'est pas votre pièce !")
    else:
        await send_chess_image(game, game.echequier.get_raw_mouvement(piece))


async def process_mouvement(ctx : discord.Interaction, game : Game, user : User, position : str, target_position : str) -> None:
    if not game.echequier.has_piece(position):
        await ctx.response.send_message("Il n'y a pas de pièce à cette case !")
        return
    
    piece = game.echequier.get_piece(position)

    if piece.color != user.color:
        await ctx.response.send_message("Ce n'est pas votre pièce !")

    else:
        next_pos_x = ChessGame.letters_to_index[target_position[0]]
        next_pos_y = 8 - int(target_position[1])
        
        if isinstance(piece, Pawn) and int(target_position[1]) == 8:
            await ctx.response.send_message("Votre pion est prêt à promouvoir ! Utilisez la commande /promouvoir. (Action annulée)", ephemeral=True)
            return
        
        result = piece.get_foresee_move()[next_pos_y][next_pos_x]

        if result == 0:
            await ctx.response.send_message("Votre pièce ne peut pas se déplacer ici !")
            return
        
        else:
            
            if game.echequier.is_in_echec(piece, target_position):
                await ctx.response.send_message("Vous ne pouvez pas vous mettre en echec !")
                return

            response = f"{position} vers {target_position}."

            if result == 2:
                piece_ennemy_eaten = game.echequier.get_piece(target_position)


                response+= f"\n{ChessGame.index_to_names.get(str(piece_ennemy_eaten).lower())} ({piece_ennemy_eaten.color.displayString}) mangé par {ChessGame.index_to_names.get(str(piece).lower())} ({piece.color.displayString}) !"

            piece.move(target_position)

            
            # Si 0 possibilités de s'échapper, echec et mat
            if game.echequier.is_checkmate(piece):
                channel_game = ctx.guild.get_channel(game.channel_id)
                
                user_1 = await client.fetch_user(game.user_1.discord_id)
                user_2 = await client.fetch_user(game.user_2.discord_id)

                winner_name = user_1.name if game.user_1.color == game.color_playing else user_2.name

                game.winner = winner_name
                
                await channel_game.set_permissions(user_1,send_messages=False)
                await channel_game.set_permissions(user_2,send_messages=False)
                await ctx.response.send_message(response + f"\nEchec et mat ! Les {game.color_playing.displayString} l'emportent ! ({winner_name})")
                chess_sql.update_by_id(game.todict(), "games", game.game_id)
                chess_sql.update_by_id(game.echequier.todict(), "echequiers", game.game_id)
                await send_chess_image(game)
                return
            
            await ctx.response.send_message(response + f"\nAu tour des {next_color(ChessGame.Color, game.color_playing).displayString} de jouer !")

            game.color_playing = next_color(ChessGame.Color, game.color_playing)

            game.echequier.reverse_echequier()

            chess_sql.update_by_id(game.todict(), "games", game.game_id)
            chess_sql.update_by_id(game.echequier.todict(), "echequiers", game.game_id)
        await send_chess_image(game)


    
async def send_chess_image(game : Game, raw_mouvements=[]) -> None:
    board = chess.Board(game.echequier.get_raw_table())

    # ça veut dire que on va envoyer une image avec les mouvements affichés (/mouvement)
    if len(raw_mouvements) != 0:
        svg_generator = chess.svg.board(
        board,
        fill=raw_mouvements,
        size=1000,
        ) 
    else:
        svg_generator = chess.svg.board(
        board,
        size=1000,
        ) 

    

    chemin_fichier_actuel = os.path.abspath(__file__)

    dossier_parent = os.path.dirname(chemin_fichier_actuel)

    output_file_path = dossier_parent + "//output.svg"

    with open(output_file_path, "w") as f:
        f.write(svg_generator)

    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    shape = builder.insert_image(output_file_path)

    shape.image_data.save(dossier_parent + "//svg-to-png.png")

    await client.get_guild(GUILD_ID).get_channel(game.channel_id).send(file=discord.File(dossier_parent + "//svg-to-png.png", "image_echec.png"))



def validate_chess_move_format(chess_move : str) -> bool:
    pattern = re.compile(r'^[A-H][1-8]$')
    return bool(pattern.match(chess_move))

def next_color(enumeration, current_value):
    elements = list(enumeration)
    current_index = elements.index(current_value)

    next_index = (current_index + 1) % len(elements)

    return elements[next_index]



async def load_games(chess_sql : SQLite, client : MyClient) -> None:
    for game_tuple in chess_sql.list_all("games"):
        id = game_tuple[0]
        channel_id = game_tuple[1]
        user_1_dict = json.loads(game_tuple[2])
        user_2_dict = json.loads(game_tuple[3])
        color_playing = ChessGame.Color.get_by_name(game_tuple[4])
        winner = game_tuple[5]

        # Si y'a un gagnant, la game est terminé et si le salon n'existe pas, la game n'a pas à être load. (non prévu)
        if winner == "" and client.get_guild(GUILD_ID).get_channel(channel_id):
            user_1 = User(user_1_dict["discord_id"], ChessGame.Color.get_by_name(user_1_dict["color"]), user_1_dict["points"])
            user_2 = User(user_2_dict["discord_id"], ChessGame.Color.get_by_name(user_2_dict["color"]), user_2_dict["points"])
            
            game = Game(channel_id, user_1, user_2, id, color_playing, winner)

            for echequier_tuple in chess_sql.find_by({"id" : id}, "echequiers"):
                game_id = echequier_tuple[0]
                channel_id = echequier_tuple[1]
                pieces_info = json.loads(echequier_tuple[2])


                echequier = ChessGame.Echequier(game_id, channel_id)
                
                pieces = []
                for piece_info in pieces_info:
                    type = piece_info[0]
                    position = piece_info[1]
                    color = ChessGame.Color.get_by_name(piece_info[2])
                    first_move = piece_info[3]

                    piece = None
                    match type:
                        case "pawn":
                            piece = Pawn(position, color, echequier)
                        case "rook":
                            piece = Rook(position, color, echequier)
                        case "king":
                            piece = King(position, color, echequier)
                        case "queen":
                            piece = Queen(position, color, echequier)
                        case "bishop":
                            piece = Bishop(position, color, echequier)
                        case "knight":
                            piece = Knight(position, color, echequier)
                    
                    piece.first_move = first_move
                    pieces.append(piece)

                for piece in pieces:
                    echequier.add_piece(piece)

                game.echequier = echequier
            
            games[str(game.channel_id)] = game

    print(f"{len(games)} parties chargées !")

def main() -> None:    
    client.run(token)

if __name__ == "__main__":
    main()
