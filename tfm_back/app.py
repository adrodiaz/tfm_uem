from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import joblib
import pandas as pd
import pymysql
import io
import matplotlib.pyplot as plt

app = Flask("__TFM__")
CORS(app) 

# Cargar el modelo
model = joblib.load('model.pkl')

# Conexión a la base de datos MySQL
def get_db_connection():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='tfm_bbdd',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

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
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT assists, minutes_played, yellow_cards, red_cards FROM players WHERE player_id = %s"
            cursor.execute(sql, (player_id,))
            player_data = cursor.fetchone()

            if not player_data:
                return jsonify({'error': 'Jugador no encontrado'}), 404
            
            # Hacer la predicción
            input_data = pd.DataFrame([player_data])
            prediction = model.predict(input_data)
            
            return jsonify({'player_id': player_id, 'prediction': prediction[0]})
    finally:
        connection.close()

@app.route('/api/competitions', methods=['GET'])
def get_competitions():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM competition")
            competitions = cursor.fetchall()
            return jsonify(competitions)
    finally:
        connection.close()

@app.route('/api/competitions/<comp_type>', methods=['GET'])
def get_competitions_by_type(comp_type):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM competition WHERE type = %s"
            cursor.execute(sql, (comp_type,))
            competitions = cursor.fetchall()
            return jsonify(competitions)
    finally:
        connection.close()

@app.route('/api/clubs/<competition_id>', methods=['GET'])
def get_clubs_by_competition(competition_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM clubs WHERE domestic_competition_id = %s"
            cursor.execute(sql, (competition_id,))
            clubs = cursor.fetchall()
            return jsonify(clubs)
    finally:
        connection.close()

@app.route('/api/players', methods=['GET'])
def search_players():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            name = request.args.get('name', default=None)
            position = request.args.get('position', default=None)
            club = request.args.get('current_club_name', default=None)
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))

            sql = "SELECT * FROM players WHERE TRUE"
            params = []

            if name:
                sql += " AND name LIKE %s"
                params.append(f"%{name}%")
            if position:
                sql += " AND position = %s"
                params.append(position)
            if club:
                sql += " AND current_club_name LIKE %s"
                params.append(f"%{club}%")

            cursor.execute(sql, params)
            players = cursor.fetchall()

            # Implementar paginación
            start = (page - 1) * per_page
            end = start + per_page
            paginated_players = players[start:end]
            
            return jsonify(paginated_players)
    finally:
        connection.close()

@app.route('/api/games', methods=['GET'])
def get_games_by_competition():
    competition_id = request.args.get('competition_id')
    season = request.args.get('season')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if not competition_id:
                return jsonify({"error": "competition_id is required"}), 400

            if season:
                sql = """
                    SELECT
                        g.game_id,
                        g.competition_id,
                        g.season,
                        g.date,
                        g.round,
                        g.home_club_id,
                        hc.name AS home_club_name,
                        g.away_club_id,
                        ac.name AS away_club_name,
                        g.home_club_goals,
                        g.away_club_goals,
                        g.stadium,
                        g.attendance,
                        g.referee
                    FROM games g
                    JOIN clubs hc ON g.home_club_id = hc.club_id
                    JOIN clubs ac ON g.away_club_id = ac.club_id
                    WHERE g.competition_id = %s AND g.season = %s
                    ORDER BY g.season DESC
                """
                cursor.execute(sql, (competition_id, season))
            else:
                sql = """
                    SELECT
                        g.game_id,
                        g.competition_id,
                        g.season,
                        g.date,
                        g.round,
                        g.home_club_id,
                        hc.name AS home_club_name,
                        g.away_club_id,
                        ac.name AS away_club_name,
                        g.home_club_goals,
                        g.away_club_goals,
                        g.stadium,
                        g.attendance,
                        g.referee
                    FROM games g
                    JOIN clubs hc ON g.home_club_id = hc.club_id
                    JOIN clubs ac ON g.away_club_id = ac.club_id
                    WHERE g.competition_id = %s
                    ORDER BY g.season DESC
                """
                cursor.execute(sql, (competition_id,))

            games = cursor.fetchall()

            if not games:
                return jsonify({"error": "No games found"}), 404

            return jsonify(games)
    finally:
        connection.close()

@app.route('/api/seasons', methods=['GET'])
def get_seasons_by_competition():
    competition_id = request.args.get('competition_id')

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            if not competition_id:
                return jsonify({"error": "competition_id is required"}), 400

            sql = "SELECT DISTINCT season FROM games WHERE competition_id = %s ORDER BY season DESC"
            cursor.execute(sql, (competition_id,))
            seasons = cursor.fetchall()

            if not seasons:
                return jsonify({"error": "No games found for the given competition_id"}), 404

            return jsonify(seasons)
    finally:
        connection.close()
        
        
        
@app.route('/api/teams', methods=['GET'])
def get_teams_by_competition_and_season():
    competition_id = request.args.get('competition_id')
    season = request.args.get('season')

    if not competition_id or not season:
        return jsonify({"error": "competition_id and season are required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    c.club_id AS team_id,
                    c.name AS team_name
                FROM clubs c
                JOIN games g ON g.home_club_id = c.club_id OR g.away_club_id = c.club_id
                WHERE g.competition_id = %s AND g.season = %s
                GROUP BY c.club_id, c.name
            """
            cursor.execute(sql, (competition_id, season))
            teams = cursor.fetchall()
            
            if not teams:
                return jsonify({"error": "No teams found"}), 404

            return jsonify(teams)
    finally:
        connection.close()

# Devolver el rendimiento de cada equipo por temporada
@app.route('/api/team_performance_chart', methods=['GET'])
def get_team_performance_chart():
    team_id = request.args.get('team_id')
    competition_id = request.args.get('competition_id')

    if not team_id or not competition_id:
        return jsonify({"error": "team_id and competition_id are required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    g.season,
                    SUM(CASE 
                        WHEN g.home_club_id = %s AND g.home_club_goals > g.away_club_goals THEN 3
                        WHEN g.away_club_id = %s AND g.away_club_goals > g.home_club_goals THEN 3
                        WHEN g.home_club_goals = g.away_club_goals THEN 1
                        ELSE 0
                    END) AS points
                FROM games g
                WHERE (g.home_club_id = %s OR g.away_club_id = %s)
                  AND g.competition_id = %s
                GROUP BY g.season
                ORDER BY g.season;
            """
            cursor.execute(sql, (team_id, team_id, team_id, team_id, competition_id))
            performance = cursor.fetchall()

            if not performance:
                return jsonify({"error": "No performance data found"}), 404

            # Crear el gráfico
            seasons = [row['season'] for row in performance]
            points = [row['points'] for row in performance]

            plt.figure(figsize=(10, 6))
            plt.plot(seasons, points, marker='o', label='Puntos')
            plt.xlabel('Temporada')
            plt.ylabel('Puntos')
            plt.title('Desempeño del equipo a lo largo de las temporadas')
            plt.grid(True)
            plt.legend()

            # Guardar la gráfica en un objeto de memoria
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            # Devolver la gráfica como respuesta
            return send_file(img, mimetype='image/png')
    finally:
        connection.close()
        

# Devolver la cantidad de goles de equipo por temporada
@app.route('/api/team_goals_scored_chart', methods=['GET'])
def get_team_goals_scored_chart():
    team_id = request.args.get('team_id')
    competition_id = request.args.get('competition_id')

    if not team_id or not competition_id:
        return jsonify({"error": "team_id and competition_id are required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    g.season,
                    SUM(CASE 
                        WHEN g.home_club_id = %s THEN g.home_club_goals
                        WHEN g.away_club_id = %s THEN g.away_club_goals
                        ELSE 0
                    END) AS goals_scored
                FROM games g
                WHERE (g.home_club_id = %s OR g.away_club_id = %s)
                  AND g.competition_id = %s
                GROUP BY g.season
                ORDER BY g.season;
            """
            cursor.execute(sql, (team_id, team_id, team_id, team_id, competition_id))
            goals_data = cursor.fetchall()

            if not goals_data:
                return jsonify({"error": "No goals scored data found"}), 404

            # Crear el gráfico
            seasons = [row['season'] for row in goals_data]
            goals_scored = [row['goals_scored'] for row in goals_data]

            plt.figure(figsize=(10, 6))
            plt.plot(seasons, goals_scored, marker='o', color='green', label='Goles realizados')
            plt.xlabel('Temporada')
            plt.ylabel('Goles Realizados')
            plt.title('Goles realizados por temporada')
            plt.grid(True)
            plt.legend()

            # Guardar la gráfica en un objeto de memoria
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            # Devolver la gráfica como respuesta
            return send_file(img, mimetype='image/png')
    finally:
        connection.close()
        
@app.route('/api/team_goals_conceded_chart', methods=['GET'])
def get_team_goals_conceded_chart():
    team_id = request.args.get('team_id')
    competition_id = request.args.get('competition_id')

    if not team_id or not competition_id:
        return jsonify({"error": "team_id and competition_id are required"}), 400

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT
                    g.season,
                    SUM(CASE 
                        WHEN g.home_club_id = %s THEN g.away_club_goals
                        WHEN g.away_club_id = %s THEN g.home_club_goals
                        ELSE 0
                    END) AS goals_conceded
                FROM games g
                WHERE (g.home_club_id = %s OR g.away_club_id = %s)
                  AND g.competition_id = %s
                GROUP BY g.season
                ORDER BY g.season;
            """
            cursor.execute(sql, (team_id, team_id, team_id, team_id, competition_id))
            goals_data = cursor.fetchall()

            if not goals_data:
                return jsonify({"error": "No goals conceded data found"}), 404

            # Crear el gráfico
            seasons = [row['season'] for row in goals_data]
            goals_conceded = [row['goals_conceded'] for row in goals_data]

            plt.figure(figsize=(10, 6))
            plt.plot(seasons, goals_conceded, marker='o', color='red', label='Goles recibidos')
            plt.xlabel('Temporada')
            plt.ylabel('Goles Recibidos')
            plt.title('Goles recibidos por temporada')
            plt.grid(True)
            plt.legend()

            # Guardar la gráfica en un objeto de memoria
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            # Devolver la gráfica como respuesta
            return send_file(img, mimetype='image/png')
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
