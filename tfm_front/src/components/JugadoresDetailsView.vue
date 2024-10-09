<template>
  <div>
    <h1>{{ player.name }}</h1>
    <img :src="player.image_url" :alt="player.name">
    <p>Edad: {{ age }}</p>
    <p>Nacionalidad: {{ player.country_of_citizenship }}</p>
    <p>Equipo Actual: {{ player.current_club_name }}</p>
    <p>Posición: {{ player.position }}</p>
    <p>Valor de mercado: €{{ player.market_value_in_eur }}</p>

    <h2>Estadísticas del Jugador</h2>
    <p>Primer año registrado: {{ stats.first_year }}</p>
    <p>Último año registrado: {{ stats.last_year }}</p>
    <p>Cantidad estimada de partidos jugados: {{ stats.estimated_games_played }}</p>
    <p>Partidos con eventos especiales (Goles, Amonestaciones, Asistencias): {{ stats.games_played }}</p>
    <p>Goles: {{ stats.goals }}</p>
    <p>Amonestaciones: {{ stats.cards }}</p>
    <p>Asistencias: {{ stats.assists }}</p>

    <h2>Predicciones de Rendimiento</h2>
    <div>
      <h3>Gráfico de Goles</h3>
      <img :src="goalsChartUrl" alt="Gráfico de Goles" v-if="goalsChartUrl">
    </div>
    <div>
      <h3>Gráfico de Tarjetas</h3>
      <img :src="cardsChartUrl" alt="Gráfico de Tarjetas" v-if="cardsChartUrl">
    </div>
    <div>
      <h3>Gráfico de Asistencias</h3>
      <img :src="assistsChartUrl" alt="Gráfico de Asistencias" v-if="assistsChartUrl">
    </div>
  </div>
</template>

<script>
import { getPlayerById, getPlayerGoalsChart, getPlayerCardsChart, getPlayerAssistsChart } from '../services/api';

export default {
  data() {
    return {
      player: {},
      stats: {},
      goalsChartUrl: '',
      cardsChartUrl: '',
      assistsChartUrl: ''
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
      this.stats = data.stats; // Asegúrate de obtener las estadísticas del jugador

      // Obtener las URLs de los gráficos usando los métodos de api.js
      this.goalsChartUrl = await getPlayerGoalsChart(playerId);
      this.cardsChartUrl = await getPlayerCardsChart(playerId);
      this.assistsChartUrl = await getPlayerAssistsChart(playerId);
    } catch (error) {
      console.error('Error fetching player details:', error);
    }
  }
};
</script>
