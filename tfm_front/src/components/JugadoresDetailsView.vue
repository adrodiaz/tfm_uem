<template>
  <div class="player-container">
    <div class="player-header">
      <h1>{{ player.name }}</h1>
    </div>
    <div class="player-details">
      <img :src="player.image_url" :alt="player.name" class="player-image">
      <div class="player-info">
        <p><strong>Edad:</strong> {{ age }}</p>
        <p><strong>Nacionalidad:</strong> {{ player.country_of_citizenship }}</p>
        <p><strong>Equipo Actual:</strong> {{ player.current_club_name }}</p>
        <p><strong>Posición:</strong> {{ player.position }}</p>
        <p><strong>Valor de mercado:</strong> €{{ player.market_value_in_eur }}</p>
      </div>
    </div>

    <div class="stats-container">
      <h2>Estadísticas del Jugador</h2>
      <div class="stats-info">
        <p><strong>Primer año registrado:</strong> {{ stats.first_year }}</p>
        <p><strong>Último año registrado:</strong> {{ stats.last_year }}</p>
        <p><strong>Cantidad estimada de partidos jugados:</strong> {{ stats.estimated_games_played }}</p>
        <p><strong>Partidos con eventos especiales:</strong> {{ stats.games_played }}</p>
        <p><strong>Goles:</strong> {{ stats.goals }}</p>
        <p><strong>Amonestaciones:</strong> {{ stats.cards }}</p>
        <p><strong>Asistencias:</strong> {{ stats.assists }}</p>
      </div>
    </div>

    <h2>Gráficos de Rendimiento</h2>
    <div class="chart-options">
      <button
        v-for="(chartType, index) in chartTypes"
        :key="index"
        @click="selectChart(chartType)"
        :class="{ 'active-chart': selectedChart === chartType }"
      >
        {{ chartType }}
      </button>
    </div>

    <div class="chart-container">
      <div class="main-content">
        <div v-if="performanceChart" class="performance-chart">
          <!-- Imagen del gráfico correspondiente -->
          <img :src="performanceChart" :alt="`Gráfico de ${selectedChart}`" class="chart-image" />
        </div>
        <p v-else>No hay gráficos disponibles. Seleccione un tipo de gráfico para verlo.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { getPlayerById, getPlayerGoalsChart, getPlayerAssistsChart, getPlayerCardsChart } from '../services/api';

export default {
  data() {
    return {
      player: {},
      stats: {},
      chartTypes: ['Goles', 'Asistencias', 'Amonestaciones'],
      selectedChart: 'Goles',
      performanceChart: null,
    };
  },
  computed: {
    age() {
      const today = new Date();
      const birthDate = new Date(this.player.date_of_birth);
      let age = today.getFullYear() - birthDate.getFullYear();
      const month = today.getMonth() - birthDate.getMonth();
      if (month < 0 || (month === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      return age;
    }
  },
  async created() {
    const playerId = this.$route.params.playerId;
    try {
      const data = await getPlayerById(playerId);
      this.player = data.player;
      this.stats = data.stats;

      // Cargar el gráfico de goles por defecto
      this.performanceChart = await getPlayerGoalsChart(playerId);
    } catch (error) {
      console.error('Error fetching player details:', error);
    }
  },
  methods: {
    async selectChart(chartType) {
      this.selectedChart = chartType;
      const playerId = this.player.player_id; // Suponiendo que `player_id` es parte del objeto `player`

      if (chartType === 'Goles') {
        this.performanceChart = await getPlayerGoalsChart(playerId);
      } else if (chartType === 'Asistencias') {
        this.performanceChart = await getPlayerAssistsChart(playerId);
      } else if (chartType === 'Amonestaciones') {
        this.performanceChart = await getPlayerCardsChart(playerId);
      }
    }
  }
};
</script>

<style scoped>
/* Estructura principal del contenedor */
.player-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Encabezado del equipo */
.player-header {
  text-align: center;
  margin-bottom: 20px;
}

.player-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin: 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #d64040;
}

/* Estilo para los detalles del equipo */
.player-details {
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

/* Información detallada del jugador */
.player-info {
  width: 100%;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.player-info p {
  margin: 10px 0;
  font-size: 1.1rem;
  color: #34495e;
}

.player-info strong {
  color: #4d0606;
  font-weight: 600;
}

/* Estilo para la sección de estadísticas */
.stats-container {
  margin-top: 20px; /* Espaciado superior */
  padding: 20px; /* Espaciado interno */
  background-color: #ffffff; /* Color de fondo del contenedor de estadísticas */
  border-radius: 10px; /* Bordes redondeados */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Sombra */
}

.stats-info {
  display: flex;
  flex-direction: column; /* Coloca las estadísticas en una columna */
  gap: 10px; /* Espaciado entre las estadísticas */
}

.stats-info p {
  margin: 0; /* Elimina el margen de los párrafos */
  font-size: 1.1rem; /* Ajusta el tamaño de la fuente */
  color: #000000; /* Color del texto */
}

/* Estilos para los gráficos */
.chart-options {
  margin: 20px 0;
}
.chart-options button {
  margin-right: 10px;
  padding: 10px;
}
.active-chart {
  background-color: #007bff;
  color: white;
}

/* Añadir un poco de espaciado al final */
p:last-child {
  margin-bottom: 0;
}

/* Imagen del jugador */
.player-image {
  max-width: 150px; /* Tamaño de la imagen del jugador */
  height: auto;
  border-radius: 10px;
}

.chart-container {
  margin-top: 20px; /* Espaciado superior para el contenedor de gráficos */
  padding: 20px; /* Espaciado interno */
  background-color: #ffffff; /* Color de fondo del contenedor de gráficos */
  border-radius: 10px; /* Bordes redondeados */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Sombra */
}

.chart-image {
  max-width: 100%; /* Asegura que la imagen no exceda el ancho del contenedor */
  height: auto; /* Mantiene la proporción de la imagen */
  border-radius: 8px; /* Bordes redondeados para la imagen */
}
</style>
