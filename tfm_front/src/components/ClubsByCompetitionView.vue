<template>
    <div>
      <h1>Equipos en {{ competitionName }}</h1>
      <div v-if="clubs.length">
        <div v-for="club in clubs" :key="club.club_id" class="club-card">
          <h3>{{ club.name }}</h3>
          <p>Valor de mercado: {{ club.total_market_value }}</p>
          <p>Tamaño del equipo: {{ club.squad_size }}</p>
          <p>Promedio de edad: {{ club.average_age }}</p>
          <a :href="club.url" target="_blank">Ver más en Transfermarkt</a>
        </div>
      </div>
      <p v-else>No se encontraron equipos para esta competición.</p>
    </div>
  </template>
  
  <script>
  import { getClubsByCompetition } from '../services/api';
  
  export default {
    name: 'ClubsByCompetitionView',
    data() {
      return {
        clubs: [],
        competitionName: ''
      };
    },
    methods: {
      async fetchClubs() {
        try {
          this.clubs = await getClubsByCompetition(this.$route.params.competitionId);
          if (this.clubs.length > 0) {
            this.competitionName = this.clubs[0].competition_name || 'Desconocido';
          }
        } catch (error) {
          console.error('Error loading clubs:', error);
        }
      }
    },
    async created() {
      await this.fetchClubs();
    }
  };
  </script>
  
  <style scoped>
  .club-card {
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 16px;
    background-color: #f9f9f9;
    margin-bottom: 20px;
  }
  </style>
  