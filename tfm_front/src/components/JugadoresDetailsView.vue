<template>
  <div>
    <h1>{{ player.name }}</h1>
    <img :src="player.image_url" :alt="player.name">
    <p>Edad: {{ age }}</p>
    <p>Nacionalidad: {{ player.country_of_citizenship }}</p>
    <p>Equipo Actual: {{ player.current_club_name }}</p>
    <p>Posición: {{ player.position }}</p>
    <p>Valor de mercado: €{{ player.market_value_in_eur }}</p>

    <h2>Estadísticas</h2>
    <p>Partidos jugados: {{ stats.games_played }}</p>
    <p>Goles: {{ stats.goals }}</p>
    <p>Asistencias: {{ stats.assists }}</p>

    <h2>Predicciones de Rendimiento</h2>
    <!-- Aquí podrías agregar visualizaciones gráficas basadas en las estadísticas -->
  </div>
</template>

<script>
import { getPlayerById } from '../services/api';

export default {
  data() {
    return {
      player: {},
      stats: {}
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
    } catch (error) {
      console.error('Error fetching player details:', error);
    }
  }
};
</script>