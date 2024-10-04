import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import numpy as np  # Para manejar NaN

# Cargamos los datasets
appearances = pd.read_csv('D:/UEM/TFM/tfm/data/appearances.csv')
club_games = pd.read_csv('D:/UEM/TFM/tfm/data/club_games.csv')
clubs = pd.read_csv('D:/UEM/TFM/tfm/data/clubs.csv')
competitions = pd.read_csv('D:/UEM/TFM/tfm/data/competitions.csv')
game_events = pd.read_csv('D:/UEM/TFM/tfm/data/game_events.csv')
game_lineups = pd.read_csv('D:/UEM/TFM/tfm/data/game_lineups.csv')
games = pd.read_csv('D:/UEM/TFM/tfm/data/games.csv')
player_valuations = pd.read_csv('D:/UEM/TFM/tfm/data/player_valuations.csv')
players = pd.read_csv('D:/UEM/TFM/tfm/data/players.csv')
transfers = pd.read_csv('D:/UEM/TFM/tfm/data/transfers.csv')

# Eliminamos filas con valores nulos en columnas clave y convertimos fechas

# competitions
competitions.dropna(subset=['competition_id', 'competition_code','name'], inplace=True)
competitions = competitions.replace('', 'null')

# clubs
clubs.dropna(subset=['club_id','domestic_competition_id', 'name'], inplace=True)
clubs = clubs.replace('', 'null')
filtered_clubs_df = clubs[
    (clubs['domestic_competition_id'].isin(competitions['competition_id']))
]

# games
games.dropna(subset=['game_id', 'competition_id','season', 'home_club_id', 'away_club_id'], inplace=True)
games['date'] = pd.to_datetime(games['date'], errors='coerce')
# Eliminamos las columnas 'home_club_name' y 'away_club_name', ya que tenemos los ids
games.drop(columns=['home_club_name', 'away_club_name'], inplace=True)
games = games.replace('', 'null')
# Filtrar el DataFrame de games para que solo incluya los clubes que existen en el DataFrame de clubs
filtered_games_df = games[
    (games['home_club_id'].isin(filtered_clubs_df['club_id'])) & 
    (games['away_club_id'].isin(filtered_clubs_df['club_id']))
]

# game_lineups 
game_lineups.dropna(subset=['game_lineups_id', 'game_id','player_id', 'club_id'], inplace=True)
game_lineups['date'] = pd.to_datetime(game_lineups['date'], errors='coerce')
game_lineups = game_lineups.replace('', 'null')
filtered_game_lineups_df = game_lineups[
    (game_lineups['club_id'].isin(filtered_clubs_df['club_id'])) & 
    (game_lineups['game_id'].isin(filtered_games_df['game_id']))
]

# club_games
club_games.dropna(subset=['game_id', 'club_id','opponent_id'], inplace=True)
filtered_club_games_df = club_games[
    (club_games['club_id'].isin(filtered_clubs_df['club_id'])) & 
    (club_games['opponent_id'].isin(filtered_clubs_df['club_id']))
]

# players
players.dropna(subset=['player_id', 'current_club_id','current_club_domestic_competition_id'], inplace=True)
players['date_of_birth'] = pd.to_datetime(players['date_of_birth'], errors='coerce')
players['contract_expiration_date'] = pd.to_datetime(players['contract_expiration_date'], errors='coerce')
players['contract_expiration_date'] = players['contract_expiration_date'].dt.strftime('%Y-%m-%d')
# Reemplazar NaT (nulos) por NaN de NumPy para evitar problemas
players['contract_expiration_date'] = players['contract_expiration_date'].replace('NaT', np.nan)
players.drop(columns=['current_club_name'], inplace=True)
filtered_players_df = players[
    (players['current_club_id'].isin(filtered_clubs_df['club_id'])) 
]

# game_events
game_events.dropna(subset=['game_event_id', 'date','game_id','club_id','player_id'], inplace=True)
game_events['date'] = pd.to_datetime(game_events['date'], errors='coerce')
game_events.drop(columns=['description'], inplace=True)
# Filtrar por 'club_id' y 'game_id'
filtered_game_events_df = game_events[
    (game_events['club_id'].isin(filtered_clubs_df['club_id']))  & 
    (game_events['game_id'].isin(filtered_games_df['game_id'])) &
    ((game_events['player_in_id'].isnull()) | (game_events['player_in_id'].isin(filtered_players_df['player_id']))) &
    ((game_events['player_assist_id'].isnull()) | (game_events['player_assist_id'].isin(filtered_players_df['player_id'])))
]

# player_valuations 
player_valuations.dropna(subset=['player_id', 'current_club_id','player_club_domestic_competition_id'], inplace=True)
player_valuations['date'] = pd.to_datetime(player_valuations['date'], errors='coerce')
player_valuations = player_valuations.replace('', 'null')
filtered_player_valuations_df = player_valuations[
    (player_valuations['current_club_id'].isin(filtered_clubs_df['club_id']))
]

# appearances
appearances.dropna(subset=['appearance_id','game_id', 'player_id','player_club_id','player_current_club_id','competition_id'], inplace=True)
appearances['date'] = pd.to_datetime(appearances['date'], errors='coerce')
appearances.drop(columns=['player_name'], inplace=True)
filtered_appearances_df = appearances[
    (appearances['player_club_id'].isin(filtered_clubs_df['club_id']))  & 
    (appearances['player_current_club_id'].isin(filtered_clubs_df['club_id']))  & 
    (appearances['competition_id'].isin(competitions['competition_id']))  & 
    (appearances['game_id'].isin(filtered_club_games_df['game_id']))
]

# transfers
transfers.dropna(subset=['player_id', 'transfer_date','from_club_id','to_club_id'], inplace=True)
transfers['transfer_date'] = pd.to_datetime(transfers['transfer_date'], errors='coerce')
transfers.drop(columns=['from_club_name','to_club_name','player_name'], inplace=True)
transfers = transfers.replace('', 'null')
filtered_transfers_df = transfers[
    (transfers['from_club_id'].isin(filtered_clubs_df['club_id'])) & 
    (transfers['to_club_id'].isin(filtered_clubs_df['club_id']))
]

# Guardamos los DataFrames actualizados
competitions.to_csv('D:/UEM/TFM/tfm/data_clean/competitions_clean.csv', index=False)
filtered_appearances_df.to_csv('D:/UEM/TFM/tfm/data_clean/appearances_clean.csv', index=False)
filtered_clubs_df.to_csv('D:/UEM/TFM/tfm/data_clean/clubs_clean.csv', index=False)
filtered_club_games_df.to_csv('D:/UEM/TFM/tfm/data_clean/club_games_clean.csv', index=False)
filtered_games_df.to_csv('D:/UEM/TFM/tfm/data_clean/games_clean.csv', index=False)
filtered_game_events_df.to_csv('D:/UEM/TFM/tfm/data_clean/game_events_clean.csv', index=False)
filtered_game_lineups_df.to_csv('D:/UEM/TFM/tfm/data_clean/game_lineups_clean.csv', index=False)
filtered_players_df.to_csv('D:/UEM/TFM/tfm/data_clean/players_clean.csv', index=False, na_rep='NULL')
filtered_player_valuations_df.to_csv('D:/UEM/TFM/tfm/data_clean/player_valuations_clean.csv', index=False)
filtered_transfers_df.to_csv('D:/UEM/TFM/tfm/data_clean/transfers_clean.csv', index=False)



# Unir los datasets por game_id para obtener información adicional sobre los partidos
#merged_data = pd.merge(appearances, games, on='game_id')

# Seleccionar las columnas más relevantes para el modelo
#features = merged_data[['player_id', 'minutes_played', 'goals', 'assists', 'yellow_cards', 'red_cards', 'date']]
#target = merged_data['goals']  # Como ejemplo, predecir la cantidad de goles

# Convertir la fecha a formato de datetime para obtener información temporal (si es necesario)
#merged_data['date'] = pd.to_datetime(merged_data['date'])

# Filtrar por jugador específico (se puede utilizar para crear un endpoint)
#def filtrar_por_jugador(player_id):
#    return merged_data[merged_data['player_id'] == player_id]

# Dividir los datos en conjuntos de entrenamiento y prueba
#X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)

# Entrenar el modelo
#model = RandomForestRegressor()
#model.fit(X_train, y_train)

# Exportamos los datos mergeados
#merged_data.to_csv('merged_data.csv', index=False)
# Guardar el modelo
#import joblib
#joblib.dump(model, 'model.pkl')