<template>
    <div>
      <h1>Juegos de la competición</h1>
      <div v-if="games.length > 0">
        <div v-for="game in games" :key="game.game_id" class="game-card">
          <h3>{{ game.home_club_name }} vs {{ game.away_club_name }}</h3>
          <p>Fecha: {{ game.date }}</p>
          <p>Estadio: {{ game.stadium }}</p>
          <p>Resultado: {{ game.home_club_goals }} - {{ game.away_club_goals }}</p>
          <p>Asistencia: {{ game.attendance }}</p>
          <a :href="game.url" target="_blank">Ver más detalles</a>
        </div>
      </div>
      <p v-else>No se encontraron juegos para esta competición.</p>
    </div>
  </template>
  
  <script>
  import { getGamesByCompetition } from '../services/api';
  
  export default {
    data() {
      return {
        games: [],
      };
    },
    async created() {
      const competitionId = this.$route.params.competitionId;
      try {
        const response = await getGamesByCompetition(competitionId);
        this.games = response;
      } catch (error) {
        console.error('Error loading games:', error);
      }
    },
  };
  </script>
  
  <style scoped>
  .game-card {
    border: 1px solid #ddd;
    padding: 16px;
    margin: 16px;
  }
  </style>
  