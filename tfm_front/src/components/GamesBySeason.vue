<template>
  <div class="container">
    <h1>Juegos de la Temporada {{ season }}</h1>

    <div class="content">
      <!-- Pestañas a la izquierda con los rounds -->
      <div class="round-tabs">
        <ul>
          <!-- Botón para la Clasificación -->
          <li :class="{ active: selectedRound === 'Clasificación' }" 
              @click="selectRound('Clasificación')">
            Clasificación
          </li>
          <li v-for="(games, round) in groupedGames" :key="round" 
              :class="{ active: round === selectedRound }" 
              @click="selectRound(round)">
            {{ round }}
          </li>          
        </ul>
      </div>

    <!-- Partidos del round seleccionado a la derecha -->
    <div class="game-cards" v-if="selectedRound">
        <h2>{{ selectedRound }}</h2>
        <div v-for="game in groupedGames[selectedRound]" :key="game.game_id" class="game-card">
          <h2>{{ game.home_club_name }} - {{ game.away_club_name }}</h2>
          <p><b>Fecha: </b> {{ formatDate(game.date) }}</p>
          <p><b>Estadio:</b> {{ game.stadium }}</p>
          <p><b>Resultado:</b> {{ game.home_club_goals }} - {{ game.away_club_goals }}</p>
          <p><b>Asistencia:</b> {{ game.attendance }}</p>
          <router-link :to="{ name: 'GameDetails', params: { gameId: game.game_id.toString() } }">
            <button>Ver Detalles</button>
          </router-link>
        </div>
    
        <!-- Mostrar la clasificación si se selecciona 'Clasificación' -->
        <div v-if="selectedRound === 'Clasificación'">
          <table class="standings-table">
            <thead>
              <tr>
                <th>Pos</th>
                <th>Equipo</th>
                <th>Pts</th>
                <th>G</th>
                <th>E</th>
                <th>P</th>
                <th>GF</th>
                <th>GC</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(team, index) in standings" :key="team.teamName">
                <td>{{ index + 1 }}</td>
                <td>{{ team.teamName }}</td>
                <td>{{ team.points }}</td>
                <td>{{ team.wins }}</td>
                <td>{{ team.draws }}</td>
                <td>{{ team.losses }}</td>
                <td>{{ team.goalsFor }}</td>
                <td>{{ team.goalsAgainst }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <p v-else>No hay juegos disponibles para esta temporada.</p>
    </div>    
  </div>
</template>


<script>
import { getGamesByCompetition } from '../services/api'; // Método para obtener juegos

export default {
  data() {
    return {
      games: [], // Juegos cargados desde la API
      groupedGames: {}, // Juegos agrupados por round
      competitionId: this.$route.params.competitionId,
      season: this.$route.params.season,
      selectedRound: 'Clasificación', // Round seleccionado
      standings: [] // Clasificación de la competición
    };
  },
  async mounted() { // Cambiar a mounted en lugar de created
    try {
      const response = await getGamesByCompetition(this.competitionId, this.season);
      this.games = response; // Cargar juegos desde la API
      this.groupGamesByRound(); // Agrupar juegos por rounds
      this.calculateStandings(); // Calcular la clasificación
      
      // Agrupar los partidos por 'round'
      this.groupedGames = this.games.reduce((acc, game) => {
        if (!acc[game.round]) {
          acc[game.round] = [];
        }
        acc[game.round].push(game);
        return acc;
      }, {});

      // Ordenar los rounds (matchdays) numéricamente
      this.groupedGames = Object.fromEntries(
        Object.entries(this.groupedGames).sort(([a], [b]) => {
          const numA = parseInt(a); // Extraer número de la string '1. Matchday', etc.
          const numB = parseInt(b); // Extraer número de la string '2. Matchday', etc.

          return numA - numB; // Ordenar numéricamente
        })
      );
    } catch (error) {
      console.error('Error loading games:', error);
    }
  },
  methods: {
    groupGamesByRound() {
      // Agrupar los juegos por round
      this.groupedGames = this.games.reduce((groups, game) => {
        const round = game.round || 'Unknown Round';
        if (!groups[round]) groups[round] = [];
        groups[round].push(game);
        return groups;
      }, {});
    },
    calculateStandings() {
      // Inicializamos un objeto para cada club con sus estadísticas
      const standings = {};

      this.games.forEach(game => {
        const { home_club_id, away_club_id, home_club_goals, away_club_goals } = game;

        // Asegurarse de que el equipo tiene una entrada en el objeto standings
        if (!standings[home_club_id]) {
          standings[home_club_id] = { teamName: game.home_club_name, wins: 0, draws: 0, losses: 0, points: 0, goalsFor: 0, goalsAgainst: 0 };
        }
        if (!standings[away_club_id]) {
          standings[away_club_id] = { teamName: game.away_club_name, wins: 0, draws: 0, losses: 0, points: 0, goalsFor: 0, goalsAgainst: 0 };
        }

        // Actualizar estadísticas según el resultado del partido
        standings[home_club_id].goalsFor += home_club_goals;
        standings[home_club_id].goalsAgainst += away_club_goals;
        standings[away_club_id].goalsFor += away_club_goals;
        standings[away_club_id].goalsAgainst += home_club_goals;

        if (home_club_goals > away_club_goals) {
          standings[home_club_id].wins++;
          standings[home_club_id].points += 3;
          standings[away_club_id].losses++;
        } else if (home_club_goals < away_club_goals) {
          standings[away_club_id].wins++;
          standings[away_club_id].points += 3;
          standings[home_club_id].losses++;
        } else {
          standings[home_club_id].draws++;
          standings[away_club_id].draws++;
          standings[home_club_id].points++;
          standings[away_club_id].points++;
        }
      });

      // Convertir standings a un array y ordenarlo por puntos
      this.standings = Object.values(standings).sort((a, b) => b.points - a.points);
    },
    selectRound(round) {
      this.selectedRound = round;
    },
    formatDate(dateStr) {
      const date = new Date(dateStr);
      const day = String(date.getDate()).padStart(2, '0');
      const month = String(date.getMonth() + 1).padStart(2, '0'); // Los meses empiezan en 0
      const year = String(date.getFullYear()).slice(-2);
      return `${day}/${month}/${year}`;
    }
  }
};
</script>

<style scoped>

.container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.content {
  display: flex;
  width: 100%;
}

.round-tabs {
  width: 200px; /* Cambia el ancho de la barra lateral para hacerla más compacta */
  border-right: 1px solid #ccc;
  padding: 10px;
}

.round-tabs ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: block; /* Asegura que los elementos se muestren en bloque (verticalmente) */
}

.round-tabs li {
  padding: 10px;
  cursor: pointer;
  background-color: #f0f0f0;
  border-bottom: 1px solid #ddd;
  text-align: center;
  display: block; /* Asegura que los <li> se apilen verticalmente */
  margin-bottom: 10px; /* Añade espacio entre las pestañas para un diseño más limpio */
}

.round-tabs li:hover {
  background-color: #ddd;
}

.round-tabs .active {
  background-color: #007bff;
  color: white;
}


.game-cards {
  flex-grow: 1;
  padding-left: 20px;
}

.game-card {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #f9f9f9;
  margin-bottom: 10px;
}

.standings-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
}

.standings-table th, .standings-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: center;
}

.standings-table th {
  background-color: #f2f2f2;
}
</style>
