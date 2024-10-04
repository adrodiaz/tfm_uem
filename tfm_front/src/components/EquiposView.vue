<template>
  <div>
    <h1>Buscar Equipos</h1>

    <!-- Formulario de búsqueda -->
    <form @submit.prevent="searchTeams" class="search-form">
      <input v-model="search.name" type="text" placeholder="Nombre del equipo">
      <input v-model="search.country" type="text" placeholder="País">
      <input v-model="search.competition" type="text" placeholder="Competición">
      <button type="submit">Buscar</button>
    </form>

    <!-- Resultados de equipos en formato de tarjetas -->
    <div v-if="teams.length > 0">
      <h2>Resultados de la búsqueda</h2>
      <div class="team-grid">
        <div 
          v-for="team in teams" 
          :key="team.club_id" 
          @click="goToTeamDetail(team.club_id)"
          class="team-card"
        >
          <div class="team-info">
            <p class="team-name">{{ team.name }}</p>
            <p class="team-country">{{ team.country }}</p>
            <p class="team-competition">{{ team.domestic_competition_id }}</p>
          </div>
        </div>
      </div>

      <!-- Paginación -->
      <div class="pagination">
        <button @click="previousPage" :disabled="page === 1">Anterior</button>
        <button @click="nextPage" :disabled="!hasMoreTeams">Siguiente</button>
      </div>
    </div>
    <div v-else>
      <p>No se encontraron equipos.</p>
    </div>
  </div>
</template>

<script>
import { getTeams } from '../services/api'; // Asegúrate de tener este método en tu API

export default {
  data() {
    return {
      search: {
        name: '',
        country: '',
        competition: ''
      },
      teams: [],
      page: 1,
      perPage: 10, // Paginación con 10 equipos por página
      hasMoreTeams: false
    };
  },
  methods: {
    async searchTeams() {
      // Limpiar los resultados antes de realizar la nueva búsqueda
      this.teams = [];
      this.page = 1; // Reiniciar la página a 1
      
      try {
        const data = await getTeams(this.search, this.page, this.perPage);
        this.teams = data.teams;
        this.hasMoreTeams = data.total > this.page * this.perPage;
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    },
    goToTeamDetail(teamId) {
      this.$router.push({ name: 'EquipoDetails', params: { teamId } });
    },
    async nextPage() {
      if (this.hasMoreTeams) {
        this.page++;
        await this.searchTeams(); // Asegúrate de que se llama correctamente la función con la página actualizada
      }
    },
    async previousPage() {
      if (this.page > 1) {
        this.page--;
        await this.searchTeams(); // Asegúrate de que se llama correctamente la función con la página actualizada
      }
    }
  }
};
</script>

<style scoped>
/* Estilos del formulario de búsqueda */
.search-form {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.search-form input {
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.search-form button {
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.search-form button:hover {
  background-color: #0056b3;
}

/* Estilos para la cuadrícula de tarjetas de equipos */
.team-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr); /* Mostrar 5 equipos por fila */
  gap: 20px;
  justify-items: center;
}

.team-card {
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  width: 200px;
  cursor: pointer;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.team-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.team-info {
  padding: 10px;
  text-align: center;
}

.team-name {
  font-weight: bold;
  font-size: 1.1em;
}

.team-country, .team-competition {
  margin: 5px 0;
  color: #555;
}

/* Paginación */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  gap: 10px;
}

.pagination button {
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.pagination button:disabled {
  background-color: #ccc;
}

.pagination button:hover:enabled {
  background-color: #0056b3;
}
</style>
