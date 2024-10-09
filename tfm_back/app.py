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


# Endpoint para obtener los 3 jugadores con más goles
@app.route('/api/top_scorers', methods=['GET'])
def get_top_scorers():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Consulta para obtener los 3 jugadores con más goles
            sql = """
                SELECT p.player_id, p.name, p.country_of_birth, p.image_url, COUNT(ge.player_id) AS goals
                FROM players p
                JOIN game_events ge ON p.player_id = ge.player_id
                WHERE ge.type = 'Goals'
                GROUP BY p.player_id
                ORDER BY goals DESC
                LIMIT 3;
            """
            cursor.execute(sql)
            top_scorers = cursor.fetchall()
            print(f"Top scorers encontrados: {top_scorers}")

            if not top_scorers:
                return jsonify({'error': 'No se encontraron jugadores con goles'}), 404

            return jsonify(top_scorers)
    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en los registros
        return jsonify({"error": str(e)}), 500
    finally:
        connection.close()
        

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
            print(f"Jugador encontrado: {player}")

            if not player:
                return jsonify({'error': 'Jugador no encontrado'}), 404

            # Consulta para obtener los goles
            sql_goals = """
                SELECT COUNT(*) FROM game_events
                WHERE player_id = %s AND type = 'Goals'
            """
            try:
                cursor.execute(sql_goals, (player_id,))
                goals = cursor.fetchone()  # Esto puede devolver un diccionario
                print(f"Goles encontrados: {goals}")
                # Accede al valor a través de la clave
                goals_count = goals['COUNT(*)'] if goals else 0
            except Exception as e:
                print(f"Error al obtener goles: {e}")
                goals_count = 0

            # Consulta para obtener las tarjetas
            sql_cards = """
                SELECT COUNT(*) FROM game_events
                WHERE player_id = %s AND type = 'Cards'
            """
            try:
                cursor.execute(sql_cards, (player_id,))
                cards = cursor.fetchone()  # Esto puede devolver un diccionario
                # Accede al valor a través de la clave
                cards_count = cards['COUNT(*)'] if cards else 0
            except Exception as e:
                cards_count = 0

            # Consulta para obtener las asistencias
            sql_assists = """
                SELECT COUNT(*) FROM game_events
                WHERE player_assist_id = %s
            """
            try:
                cursor.execute(sql_assists, (player_id,))
                assists = cursor.fetchone()  # Esto puede devolver un diccionario
                # Accede al valor a través de la clave
                assists_count = assists['COUNT(*)'] if assists else 0
            except Exception as e:
                assists_count = 0

            # Consulta para obtener la cantidad de partidos jugados
            sql_games_played = """
                SELECT COUNT(DISTINCT game_id) FROM game_events
                WHERE player_id = %s OR player_assist_id = %s
            """
            try:
                cursor.execute(sql_games_played, (player_id, player_id))
                games_played = cursor.fetchone()  # Esto puede devolver un diccionario
                # Accede al valor a través de la clave
                games_played_count = games_played['COUNT(DISTINCT game_id)'] if games_played else 0
            except Exception as e:
                games_played_count = 0

            # Devolver los datos del jugador junto con las estadísticas
            stats = {
                "games_played": games_played_count,
                "goals": goals_count,
                "cards": cards_count,
                "assists": assists_count
            }
            
            # Calcular estimación de partidos jugados
            sql_first_year = """
                SELECT MIN(YEAR(date)) AS first_year FROM game_events
                WHERE player_id = %s
            """
            sql_last_year = """
                SELECT MAX(YEAR(date)) AS last_year FROM game_events
                WHERE player_id = %s
            """
            cursor.execute(sql_first_year, (player_id,))
            first_year_result = cursor.fetchone()
            first_year = first_year_result['first_year'] if first_year_result and 'first_year' in first_year_result else None

            cursor.execute(sql_last_year, (player_id,))
            last_year_result = cursor.fetchone()
            last_year = last_year_result['last_year'] if last_year_result and 'last_year' in last_year_result else None

            if first_year is not None and last_year is not None:
                years_played = last_year - first_year + 1  # Incluye el año inicial
                estimated_games_played = years_played * 40  # Promedio de 40 partidos por año
            else:
                first_year = None
                last_year = None
                estimated_games_played = 0

            # Agregar los años y el estimado de partidos a stats
            stats.update({
                "first_year": first_year,
                "last_year": last_year,
                "estimated_games_played": estimated_games_played
            })


            return jsonify({
                "player": player,
                "stats": stats
            })
    except Exception as e:
        print(f"Error: {e}")  # Imprimir el error en los registros
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

#Graficos de estadisticas de jugadores:
@app.route('/api/player_goals_chart/<int:player_id>', methods=['GET'])
def get_player_goals_chart(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT YEAR(date) AS year, COUNT(*) AS goals
                FROM game_events
                WHERE player_id = %s AND type = 'Goals'
                GROUP BY year
                ORDER BY year;
            """
            cursor.execute(sql, (player_id,))
            goals_data = cursor.fetchall()
            print(f"Goles por año: {goals_data}")
                
            if not goals_data:
                return jsonify({"error": "No data found for goals"}), 404

            # Crear gráfico de goles
            years = [row['year'] for row in goals_data]
            goals = [row['goals'] for row in goals_data]

            plt.figure(figsize=(10, 6))
            plt.plot(years, goals, marker='o', color='green', label='Goles')
            plt.xlabel('Año')
            plt.ylabel('Goles')
            plt.title('Goles por año')
            plt.grid(True)
            plt.legend()

            # Guardar la gráfica en un objeto de memoria
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            return send_file(img, mimetype='image/png')
    finally:
        connection.close()


@app.route('/api/player_cards_chart/<int:player_id>', methods=['GET'])
def get_player_cards_chart(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT YEAR(date) AS year, COUNT(*) AS cards
                FROM game_events
                WHERE player_id = %s AND type = 'Cards'
                GROUP BY year
                ORDER BY year;
            """
            cursor.execute(sql, (player_id,))
            cards_data = cursor.fetchall()

            if not cards_data:
                return jsonify({"error": "No data found for cards"}), 404

            # Crear gráfico de tarjetas
            years = [row['year'] for row in cards_data]
            cards = [row['cards'] for row in cards_data]

            plt.figure(figsize=(10, 6))
            plt.plot(years, cards, marker='o', color='red', label='Tarjetas')
            plt.xlabel('Año')
            plt.ylabel('Tarjetas')
            plt.title('Tarjetas por año')
            plt.grid(True)
            plt.legend()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            return send_file(img, mimetype='image/png')
    finally:
        connection.close()


@app.route('/api/player_assists_chart/<int:player_id>', methods=['GET'])
def get_player_assists_chart(player_id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = """
                SELECT YEAR(date) AS year, COUNT(*) AS assists
                FROM game_events
                WHERE player_assist_id = %s
                GROUP BY year
                ORDER BY year;
            """
            cursor.execute(sql, (player_id,))
            assists_data = cursor.fetchall()

            if not assists_data:
                return jsonify({"error": "No data found for assists"}), 404

            # Crear gráfico de asistencias
            years = [row['year'] for row in assists_data]
            assists = [row['assists'] for row in assists_data]

            plt.figure(figsize=(10, 6))
            plt.plot(years, assists, marker='o', color='blue', label='Asistencias')
            plt.xlabel('Año')
            plt.ylabel('Asistencias')
            plt.title('Asistencias por año')
            plt.grid(True)
            plt.legend()

            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)

            return send_file(img, mimetype='image/png')
    finally:
        connection.close()

# Endpoint para obtener las predicciones del rendimiento del jugador
@app.route('/api/players/<int:player_id>/predictions', methods=['GET'])
def get_player_predictions(player_id):
    try:
        # Llamada a la función que predice el rendimiento del jugador
        predictions = predict_player_performance(player_id)
        
        # Retorna las predicciones en formato JSON
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
########################################
# ENTRENAMIENTO DE MODELOS PREDICTIVOS #
########################################

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

def predict_player_performance(player_id):
    # Obtenemos la conexión a la base de datos
    connection = get_db_connection()
    
    try:
        # Establecemos un cursor para las consultas
        with connection.cursor() as cursor:
            # SQL para obtener goles, asistencias y tarjetas por temporada
            sql_goals = """
                SELECT YEAR(date) AS year, COUNT(*) AS goals
                FROM game_events
                WHERE player_id = %s AND type = 'Goals'
                GROUP BY year
                ORDER BY year;
            """
            
            sql_assists = """
                SELECT YEAR(date) AS year, COUNT(*) AS assists
                FROM game_events
                WHERE player_assist_id = %s
                GROUP BY year
                ORDER BY year;
            """
            
            sql_cards = """
                SELECT YEAR(date) AS year, COUNT(*) AS cards
                FROM game_events
                WHERE player_id = %s AND type = 'Cards'
                GROUP BY year
                ORDER BY year;
            """
            
            # Estimación del número de partidos jugados
            sql_first_year = """
                SELECT MIN(YEAR(date)) AS first_year FROM game_events
                WHERE player_id = %s
            """
            sql_last_year = """
                SELECT MAX(YEAR(date)) AS last_year FROM game_events
                WHERE player_id = %s
            """
            
            # Obtenemos goles por año
            cursor.execute(sql_goals, (player_id,))
            goals_data = cursor.fetchall()

            # Obtenemos asistencias por año
            cursor.execute(sql_assists, (player_id,))
            assists_data = cursor.fetchall()

            # Obtenemos tarjetas por año
            cursor.execute(sql_cards, (player_id,))
            cards_data = cursor.fetchall()

            # Obtenemos el primer y último año de la carrera del jugador
            cursor.execute(sql_first_year, (player_id,))
            first_year_result = cursor.fetchone()
            first_year = first_year_result['first_year'] if first_year_result else None

            cursor.execute(sql_last_year, (player_id,))
            last_year_result = cursor.fetchone()
            last_year = last_year_result['last_year'] if last_year_result else None

            if first_year is not None and last_year is not None:
                years_played = last_year - first_year + 1
                estimated_games_played = years_played * 40
            else:
                estimated_games_played = 0

            # Convertimos los datos a DataFrame para facilitar el manejo
            df_goals = pd.DataFrame(goals_data, columns=['year', 'goals'])
            df_assists = pd.DataFrame(assists_data, columns=['year', 'assists'])
            df_cards = pd.DataFrame(cards_data, columns=['year', 'cards'])

            # Unimos los datos por año para tener un dataset completo
            df = pd.merge(df_goals, df_assists, on='year', how='outer').fillna(0)
            df = pd.merge(df, df_cards, on='year', how='outer').fillna(0)

            # Ahora usamos el total de partidos jugados en la carrera para hacer la predicción
            X = df[['assists', 'cards']]  # Features
            y = df['goals']  # Label (goles)

            # Dividimos los datos en entrenamiento y prueba
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Entrenamos un modelo de regresión lineal
            model = LinearRegression()
            model.fit(X_train, y_train)

            # Realizamos la predicción para los próximos 40 partidos
            # Podemos usar el promedio de asistencias y tarjetas como valores futuros estimados
            average_assists = df['assists'].mean()
            average_cards = df['cards'].mean()

            predicted_goals_2024 = model.predict([[average_assists, average_cards]])

            # Hacemos lo mismo para asistencias y tarjetas si deseas predecir esas estadísticas también
            predicted_assists_2024 = average_assists * (40 / estimated_games_played) if estimated_games_played > 0 else 0
            predicted_cards_2024 = average_cards * (40 / estimated_games_played) if estimated_games_played > 0 else 0

            # Devolvemos los resultados
            return {
                "predicted_goals_2024": round(predicted_goals_2024[0],2),  # Predicción para goles
                "predicted_assists_2024": round(predicted_assists_2024,2),  # Predicción para asistencias
                "predicted_cards_2024": round(predicted_cards_2024,2)  # Predicción para tarjetas
            }
    
    except Exception as e:
        print(f"Error while predicting player performance: {e}")
        return None
    
    finally:
        # Asegurarse de cerrar la conexión a la base de datos
        connection.close()


if __name__ == '__main__':
    app.run(debug=True)
