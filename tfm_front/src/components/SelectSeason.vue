<template>
  <div class="container">
    <h1>Desempeño de Equipos por temporada</h1>

    <div>
      <!-- Menú superior: Selección de Temporadas -->
      <div v-if="seasons && seasons.length > 0">
        <ul>
          <li v-for="seasonObj in seasons" :key="seasonObj.season">
            <button
              class="season-button"
              @click="selectSeason(seasonObj.season)"
              :class="{ 'active-season': selectedSeason === seasonObj.season }"
            >
              Temporada {{ seasonObj.season }}
            </button>
          </li>
        </ul>
      </div>
      <p v-else>No hay temporadas disponibles.</p>
    </div>

    <div class="content">
      <!-- Selección de Equipos -->
      <div class="sidebar">
        <h2>Equipos - {{ selectedSeason }}</h2>
        <div v-if="teams && teams.length > 0" class="team-selection">
          <ul>
            <li v-for="team in teams" :key="team.team_id">
              <button
                @click="loadTeamPerformance(team.team_id)"
                :class="{ 'active-team': selectedTeam === team.team_id }"
              >
                {{ team.team_name }}
              </button>
            </li>
          </ul>
        </div>
        <p v-else>No hay equipos disponibles para esta temporada.</p>
      </div>

      <!-- Gráfico del desempeño del equipo -->
      <div class="main-content">
        <div v-if="performanceChart" class="performance-chart">
          <img :src="performanceChart" alt="Gráfico de Desempeño" />
        </div>
        <p v-else>Seleccione un equipo para ver su desempeño</p>
      </div>
    </div>
  </div>
</template>

<script>
import { getSeasons, getTeams, getTeamPerformanceChart } from '../services/api';

export default {
  data() {
    return {
      seasons: [],
      teams: [],
      selectedSeason: null,
      selectedTeam: null,
      teamPerformanceImage: null,
      competitionId: this.$route.params.competitionId,
      performanceChart: null,
      teamId: this.$route.params.teamId
    };
  },
  async created() {
    try {
      const response = await getSeasons(this.competitionId);
      console.log('Seasons:', response); // Verificar si las temporadas se están cargando
      this.seasons = response;

      // Verifica si hay temporadas disponibles
      if (this.seasons.length > 0) {
        // Establece la última temporada como la seleccionada
        this.selectedSeason = this.seasons[0].season;
        // Llama a selectSeason para cargar los equipos de la última temporada
        await this.selectSeason(this.selectedSeason);
      }
    } catch (error) {
      console.error('Error loading seasons:', error);
    }
  },
  methods: {
    async selectSeason(season) {
      console.log('Season selected:', season); // Verificar selección de temporada
      this.selectedSeason = season;
      this.selectedTeam = null;
      this.teamPerformanceImage = null;

      try {
        const response = await getTeams(this.competitionId, season);
        console.log('Teams:', response); // Verificar si los equipos se están cargando
        this.teams = response;
      } catch (error) {
        console.error('Error loading teams:', error);
      }
    },

    async loadTeamPerformance(team_id) {
      console.log('Team selected:', team_id); // Verificar selección de equipo
      this.selectedTeam = team_id;
      try {
        const chartData = await getTeamPerformanceChart(this.selectedTeam, this.competitionId);
        this.performanceChart = chartData; 
      } catch (error) {
        console.error('Error al obtener el gráfico de desempeño:', error);
      }
    }
  }
};
</script>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  margin-left: 10px;
}

/* Contenedor que envuelve el sidebar y el contenido principal */
.content {
  display: flex;
  flex-direction: row; /* Alinea los elementos en fila */
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

/* Estilo para el sidebar a la izquierda */
.sidebar {
  width: 25%; /* Ocupa el 25% del ancho de la pantalla */
  border-right: 1px solid #ccc; /* Línea separadora a la derecha */
  padding: 20px;
  box-sizing: border-box; /* Incluye el padding dentro del ancho */
  margin-top: 20px;
}

/* Ajustar para que los botones aparezcan uno debajo del otro */
.team-selection ul {
  list-style: none;
  padding: 10;
  display: block;
}

.team-selection li {
  margin-bottom: 10px;
}

.team-selection button {
  width: 100%; /* Asegura que el botón ocupe todo el ancho disponible */
  padding: 10px;
  background-color: #f0f0f0;
  border: none;
  cursor: pointer;
  text-align: left;
  transition: background-color 0.3s ease;
}

.team-selection button:hover,
.team-selection button.active-team {
  background-color: #d0d0d0;
}

/* Estilo para el contenido principal (gráfico de desempeño) */
.main-content {
  width: 75%; /* Ocupa el 75% del ancho de la pantalla */
  padding: 20px;
  box-sizing: border-box; /* Incluye el padding dentro del ancho */
  display: flex;
  justify-content: center;
  align-items: center;
}

.performance-chart img {
  max-width: 100%;
  height: auto;
}

/* Asegura que la imagen no se desborde */
img {
  max-width: 100%;
  height: auto;
}
</style>
