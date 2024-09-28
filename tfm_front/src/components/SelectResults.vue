<template>
    <div>
      <h1>Selecciona la Temporada</h1>
      <div v-if="seasons && seasons.length > 0">
        <ul>
          <li v-for="seasonObj in seasons" :key="seasonObj.season">
            <router-link :to="{ name: 'GamesBySeason', params: { competitionId, season: seasonObj.season } }">
              <button class="season-button">Temporada {{ seasonObj.season }}</button>
            </router-link>
          </li>
        </ul>
      </div>
      <p v-else>No hay temporadas disponibles.</p>
    </div>
  </template>
  
  <script>
  import { getSeasons } from '../services/api'; // Método para obtener las temporadas
  
  export default {
    data() {
      return {
        seasons: [],
        competitionId: this.$route.params.competitionId
      };
    },
    async created() {
      try {
        const response = await getSeasons(this.competitionId);
        this.seasons = response;
      } catch (error) {
        console.error('Error loading seasons:', error);
      }
    }
  };
  </script>
  
  <style scoped>
  .season-button {
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin: 5px 0;
    text-align: center;
  }
  
  .season-button:hover {
    background-color: #0056b3;
  }
  
  ul {
    list-style-type: none;
    padding: 0;
  }
  
  li {
    margin-bottom: 10px;
  }
  </style>