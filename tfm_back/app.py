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
            nationality = request.args.get('country_of_citizenship', default=None)
            min_market_value = request.args.get('minPrice', default=0, type=float)
            max_market_value = request.args.get('maxPrice', default=250000000, type=float)
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 10))

            sql = """
                SELECT p.*, c.name 
                FROM players p
                JOIN clubs c ON p.current_club_id = c.club_id
                WHERE TRUE
            """
            params = []

            if name:
                sql += " AND p.name LIKE %s"
                params.append(f"%{name}%")
            if position:
                sql += " AND p.position = %s"
                params.append(position)
            if club:
                sql += " AND c.name LIKE %s"
                params.append(f"%{club}%")
            if nationality:
                sql += " AND p.country_of_citizenship LIKE %s"
                params.append(f"%{nationality}%")
            if min_market_value is not None and max_market_value is not None:
                sql += " AND p.market_value_in_eur BETWEEN %s AND %s"
                params.extend([min_market_value, max_market_value])

            # Imprimir la consulta SQL y los parámetros (no es necesario decode)
            print("SQL Query:", cursor.mogrify(sql, params))

            cursor.execute(sql, params)
            players = cursor.fetchall()

            # Implementar paginación
            total = len(players)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_players = players[start:end]

            return jsonify({
                "players": paginated_players,
                "total": total
            })
    finally:
        connection.close()


# Endpoint para obtener los detalles de un jugador por su ID
@app.route('/api/players/<int:player_id>', methods=['GET'])
def get_player_by_id(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta para obtener los datos del jugador
            sql_player = """
                SELECT * FROM players WHERE player_id = %s
            """
            cursor.execute(sql_player, (player_id,))
            player = cursor.fetchone()

            if not player:
                return jsonify({'error': 'Jugador no encontrado'}), 404

            # Simular estadísticas, puedes hacer una consulta similar a otra tabla
            stats = {
                "games_played": 100,  # Ejemplo de datos
                "goals": 50,          # Ejemplo de datos
                "assists": 20         # Ejemplo de datos
            }

            # Devolver los datos del jugador junto con las estadísticas
            return jsonify({
                "player": player,
                "stats": stats
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
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
        
        
        
@app.route('/api/teamsSearch', methods=['GET']) 
def get_teams():
    name = request.args.get('name')
    country = request.args.get('country')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta para obtener los equipos
            sql = """
                SELECT
                    c.club_id AS team_id,
                    c.name AS team_name,
                    co.country_name,
                    co.name
                FROM clubs c
                JOIN competition co ON c.domestic_competition_id = co.competition_id
                WHERE 1=1
            """

            params = []

            if name:
                sql += " AND c.name LIKE %s"
                params.append(f"%{name}%")
            
            if country:
                sql += " AND co.country_name LIKE %s"
                params.append(f"%{country}%")

            print("Executing SQL:", sql)  # Para depuración
            print("With parameters:", params)  # Para depuración
            
            cursor.execute(sql, params)
            teams = cursor.fetchall()


            # Implementar paginación
            total = len(teams)
            start = (page - 1) * per_page
            end = start + per_page
            paginated_teams = teams[start:end]
            
            if not teams:
                return jsonify({"teams": [], "total": 0}), 200

            # Contar el total de equipos que coinciden con los filtros
            total_sql = """
                SELECT COUNT(*) FROM clubs c
                JOIN competition co ON c.domestic_competition_id = co.competition_id
                WHERE 1=1
            """

            print("Executing total SQL:", sql)  # Para depuración
            print("With total parameters:", params)  # Para depuración
                        
            return jsonify({
                "teams": paginated_teams,
                "total": total
            })
    except Exception as e:
        # Capturar y registrar detalles del error
        error_message = str(e) if hasattr(e, 'message') else repr(e)
        print("Error occurred:", error_message)  # Para ver cualquier error que ocurra
        return jsonify({"error": error_message}), 500
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

# Función para obtener los detalles del equipo por ID
@app.route('/api/teams/<int:team_id>', methods=['GET'])
def get_team_details(team_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Consultar la base de datos para obtener los detalles del equipo
            query = """
            SELECT 
                name, 
                squad_size, 
                average_age, 
                national_team_players, 
                foreigners_percentage, 
                stadium_name
            FROM Clubs
            WHERE club_id = %s
            """
            cursor.execute(query, (team_id,))
            result = cursor.fetchone()

            if result:
                return jsonify(result), 200
            else:
                return jsonify({"error": "Team not found"}), 404
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500
    finally:
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
