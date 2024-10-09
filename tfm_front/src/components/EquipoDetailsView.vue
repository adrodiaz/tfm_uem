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
  max-width: 900px; /* Aumentar el ancho máximo */
  margin: 20px auto;
  padding: 30px; /* Aumentar el relleno */
  background-color: #f9f9f9;
  border-radius: 15px; /* Hacer los bordes más redondeados */
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15); /* Aumentar la sombra */
}

/* Encabezado del equipo */
.team-header {
  text-align: center;
  margin-bottom: 30px; /* Aumentar el margen inferior */
}

.team-header h1 {
  font-size: 3rem; /* Aumentar el tamaño del texto */
  color: #2c3e50;
  margin: 0;
  padding-bottom: 15px; /* Aumentar el relleno inferior */
  border-bottom: 3px solid #d64040; /* Hacer la línea inferior más gruesa */
}

/* Estilo para los detalles del equipo */
.team-details {
  display: flex;
  justify-content: space-between;
  gap: 30px; /* Aumentar el espacio entre los elementos */
}

/* Información detallada del equipo */
.team-info {
  width: 100%;
  padding: 30px; /* Aumentar el relleno */
  background-color: #ffffff;
  border-radius: 15px; /* Hacer los bordes más redondeados */
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.team-info p {
  margin: 15px 0; /* Aumentar el margen */
  font-size: 1.2rem; /* Aumentar el tamaño del texto */
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

