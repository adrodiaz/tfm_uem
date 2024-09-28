from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask("__TFM__")
CORS(app) 

# Cargar el modelo
model = joblib.load('model.pkl')

# Cargar el dataset de jugadores
merged_data = pd.read_csv('merged_data.csv') 

@app.route('/')
def home():
    return "Bienvenido a la predicción del rendimiento de jugadores de fútbol"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    input_data = pd.DataFrame([data])
    prediction = model.predict(input_data)
    return jsonify({'prediction': prediction[0]})

@app.route('/predict/<int:player_id>', methods=['GET'])
def predict_player(player_id):
    # Buscar los datos del jugador por player_id
    player_data = merged_data[merged_data['player_id'] == player_id]
    
    if player_data.empty:
        return jsonify({'error': 'Jugador no encontrado'}), 404
    
    # Seleccionar solo las columnas necesarias para la predicción
    input_data = player_data[['assists', 'minutes_played', 'yellow_cards', 'red_cards']]  # Reemplaza con las características relevantes

    # Hacer la predicción
    prediction = model.predict(input_data)
    
    # Devolver el resultado como JSON
    return jsonify({'player_id': player_id, 'prediction': prediction[0]})

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
  # Lee el archivo CSV
  competitions = pd.read_csv('D:/UEM/TFM/tfm/data/competitions.csv')
  # Convierte el DataFrame a JSON
  competitions_json = competitions.to_json(orient='records')
  # Retorna directamente el JSON
  return competitions_json

@app.route('/api/competitions/<comp_type>', methods=['GET'])
def get_competitions_by_type(comp_type):
    # Lee el archivo CSV
    competitions = pd.read_csv('D:/UEM/TFM/tfm/data/competitions.csv')
    # Filtra por el tipo de competición
    filtered_competitions = competitions[competitions['type'] == comp_type]
    # Convierte el DataFrame filtrado a JSON
    competitions_json = filtered_competitions.to_json(orient='records')
    # Retorna directamente el JSON
    return competitions_json



## Devolvemos los equipos segun el ID de la competicion
@app.route('/api/clubs/<competition_id>', methods=['GET'])
def get_clubs_by_competition(competition_id):
    # Lee el archivo CSV
    clubs = pd.read_csv('D:/UEM/TFM/tfm/data/clubs.csv')
    # Filtra los equipos por el id de la competición
    filtered_clubs = clubs[clubs['domestic_competition_id'] == competition_id]
    # Convierte el DataFrame filtrado a JSON
    clubs_json = filtered_clubs.to_json(orient='records')
    return clubs_json


@app.route('/api/players', methods=['GET'])
def search_players():
    # Lee el archivo CSV
    players = pd.read_csv('D:/UEM/TFM/tfm/data/players.csv')

    # Obtén los parámetros de búsqueda de la URL
    name = request.args.get('name', default=None)
    position = request.args.get('position', default=None)
    club = request.args.get('current_club_name', default=None)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Filtrar los jugadores basado en los parámetros proporcionados
    if name:
        players = players[players['name'].str.contains(name, case=False, na=False)]
    if position:
        players = players[players['position'] == position]
    if club:
        players = players[players['current_club_name'].str.contains(club, case=False, na=False)]

    # Convierte el DataFrame filtrado a JSON (como un objeto, no cadena)
    players_json = players.to_json(orient='records')
    return players_json

# Endpoint para obtener los juegos por competition_id
@app.route('/api/games', methods=['GET'])
def get_games_by_competition():
    competition_id = request.args.get('competition_id')

    # Cargar el archivo games.csv al iniciar la aplicación
    games_df = pd.read_csv('D:/UEM/TFM/tfm/data/games.csv')
    
    if competition_id:
        # Filtrar los juegos por competition_id
        filtered_games = games_df[games_df['competition_id'] == competition_id]
        # Ordenar los juegos por temporada de más reciente a más antigua
        sorted_games = filtered_games.sort_values(by='season', ascending=False)
        
        # Convertir a JSON
        games_list = sorted_games.to_json(orient='records')
        return games_list
    else:
        return jsonify({"error": "competition_id is required"}), 400

@app.route('/api/seasons', methods=['GET'])
def get_seasons_by_competition():
    try:
        competition_id = request.args.get('competition_id')

        # Verificar si competition_id es válido
        if not competition_id:
            return jsonify({"error": "competition_id is required"}), 400

        # Cargar el archivo games.csv
        games_df = pd.read_csv('D:/UEM/TFM/tfm/data/games.csv')

        # Asegurarse de que el competition_id sea del mismo tipo (convertir a numérico si es necesario)
        games_df['competition_id'] = games_df['competition_id'].astype(str)
        competition_id = str(competition_id)

        # Filtrar los juegos por competition_id
        filtered_games = games_df[games_df['competition_id'] == competition_id]

        # Verificar si hay juegos para esa competición
        if filtered_games.empty:
            return jsonify({"error": "No games found for the given competition_id"}), 404

        # Obtener las temporadas únicas y ordenarlas de más reciente a más antigua
        seasons = sorted(filtered_games['season'].unique(), reverse=True)

        # Convertir los valores de la temporada a enteros y luego a DataFrame
        seasons_df = pd.DataFrame(seasons, columns=['season'])

        # Convertir el DataFrame a JSON y devolverlo
        return seasons_df.to_json(orient='records')

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)
