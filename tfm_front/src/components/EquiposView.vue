<template>
  <div class="search-container">
    <h1>Buscar Equipos</h1>

    <!-- Formulario de búsqueda -->
    <form @submit.prevent="resetSearch" class="search-form">
      <input v-model="search.name" type="text" placeholder="Nombre del equipo">
      <select v-model="search.country">
        <option value="">Seleccione el país</option>
        <option v-for="(countryName, countryCode) in countries" :key="countryCode" :value="countryCode">
          {{ countryName }}
        </option>
      </select>
      <button type="submit">Buscar</button>
    </form>

    <!-- Resultados de equipos en formato de tarjetas -->
    <div v-if="teams.length > 0">
      <h2>Resultados de la búsqueda</h2>
      <div class="team-grid">
        <div 
          v-for="team in teams" 
          :key="team.team_id" 
          @click="goToTeamDetail(team.team_id)"
          class="team-card"
        >
          <div class="team-info">
            <p class="team-name">{{ team.team_name }}</p>
            <p class="team-country">{{ translateCountry(team.country_name) }}</p>
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
import { getTeams } from '../services/api';
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
      perPage: 20, // Paginación con 10 equipos por página
      hasMoreTeams: false,
      countries: {
        "Germany": "Alemania",
        "Belgium": "Bélgica",
        "Denmark": "Dinamarca",
        "Scotland": "Escocia",
        "Spain": "España",
        "France": "Francia",        
        "Greece": "Grecia",
        "England": "Inglaterra",
        "Italy": "Italia",  
        "Netherlands": "Países Bajos",
        "Portugal": "Portugal",
        "Russia": "Rusia",
        "Turkey": "Turquía",
        "Ukraine": "Ucrania"
      }
    };
  },
  methods: {
    // Método para reiniciar la búsqueda y establecer la página en 1
    async resetSearch() {
      this.page = 1; // Reiniciar a la primera página
      await this.searchTeams(); // Llamar la búsqueda
    },

    // Método para realizar la búsqueda en una página específica
    async searchTeams() {
      // Limpiar los resultados antes de realizar la nueva búsqueda
      this.teams = [];
      try {
        const data = await getTeams(this.search, this.page, this.perPage);
        this.teams = data.teams;
        this.hasMoreTeams = data.total > this.page * this.perPage;
      } catch (error) {
        console.error('Error fetching teams:', error);
      }
    },

    // Traductor de código de país a nombre
    translateCountry(countryCode) {
      return this.countries[countryCode] || "Desconocido";
    },

    // Redirigir a los detalles del equipo
    goToTeamDetail(teamId) {
      console.log("ID de equipo: ", teamId);
      this.$router.push({ name: 'EquipoDetails', params: { teamId } });
    },

    // Ir a la página siguiente
    async nextPage() {
      if (this.hasMoreTeams) {
        this.page++; // Incrementar el número de página
        await this.searchTeams(); // Ejecutar la búsqueda con la nueva página
      }
    },

    // Volver a la página anterior
    async previousPage() {
      if (this.page > 1) {
        this.page--; // Decrementar el número de página
        await this.searchTeams(); // Ejecutar la búsqueda con la nueva página
      }
    }
  }
};
</script>

<style scoped>
/* Estilos del contenedor principal */
.search-container {
  margin: 20px; /* Espacio alrededor del contenedor */
}

/* Estilos del formulario de búsqueda */
.search-form {
  display: grid;
  grid-template-columns: repeat(3, 1fr); /* 3 columnas para los filtros */
  gap: 10px;
  margin-bottom: 20px; /* Espacio debajo del formulario */
  margin-top: 0; /* Asegúrate de que no haya margen superior */
}

.search-form input,
.search-form select {
  padding: 10px;
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 5px;
}

.search-form button {
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  background-color: #d64040;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.search-form button:hover {
  background-color: #eb7f7f;
}

/* Estilos para la cuadrícula de tarjetas de equipos */
.team-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  justify-items: center;
}

.team-card {
  background-color: #d5eef5;
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

.team-country {
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
  background-color: #d64040;
  color: white;
  cursor: pointer;
  border-radius: 5px;
}

.pagination button:disabled {
  background-color: #ccc;
}

.pagination button:hover:enabled {
  background-color: #eb7f7f;
}
</style>
