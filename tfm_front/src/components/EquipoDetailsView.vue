<template>
  <div class="team-container">
    <div v-if="team">
      <div class="team-header">
        <h1>{{ team.name }}</h1>
      </div>
      <div class="team-details">
        <!-- Información general del equipo -->
        <div class="team-info">
          <p><strong>Nombre:</strong> {{ team.name }}</p>
          <p><strong>Tamaño de la plantilla:</strong> {{ team.squad_size }}</p>
          <p><strong>Promedio de edad:</strong> {{ team.average_age }} años</p>
          <p><strong>Jugadores en selección nacional:</strong> {{ team.national_team_players }}</p>
          <p><strong>Porcentaje de jugadores extranjeros:</strong> {{ team.foreigners_percentage }}%</p>
          <p><strong>Nombre del estadio:</strong> {{ team.stadium_name }}</p>
        </div>
      </div>
    </div>
    <div v-else>
      <p>Cargando información del equipo...</p>
    </div>
  </div>
</template>

<script>
import { getTeamById } from '../services/api'; // Asegúrate de la ruta correcta

export default {
  data() {
    return {
      team: {}
    };
  },
  async created() {
    this.fetchTeamDetails();
  },
  methods: {
    async fetchTeamDetails() {
      const teamId = this.$route.params.teamId;
      try {
        const data = await getTeamById(teamId); // Llamar al método de servicio
        this.team = data; // Asignar directamente los datos recibidos
      } catch (error) {
        console.error("Error fetching team details:", error);
      }
    }
  }
};
</script>

<style scoped>
/* Estructura principal del contenedor */
.team-container {
  max-width: 800px;
  margin: 20px auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* Encabezado del equipo */
.team-header {
  text-align: center;
  margin-bottom: 20px;
}

.team-header h1 {
  font-size: 2.5rem;
  color: #2c3e50;
  margin: 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #d64040;
}

/* Estilo para los detalles del equipo */
.team-details {
  display: flex;
  justify-content: space-between;
  gap: 20px;
}

/* Información detallada del equipo */
.team-info {
  width: 100%;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.team-info p {
  margin: 10px 0;
  font-size: 1.1rem;
  color: #34495e;
}

.team-info strong {
  color: #d64040;
  font-weight: 600;
}

/* Añadir un poco de espaciado al final */
p:last-child {
  margin-bottom: 0;
}
</style>
