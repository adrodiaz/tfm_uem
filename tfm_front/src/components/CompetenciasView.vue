<template>
  <div>
    <h1>Competiciones</h1>
    <div class="grid-container">
      <router-link
        v-for="type in competitionTypes"
        :key="type"
        :to="{ name: 'CompetitionsByType', params: { compType: type } }"
        class="card-link"
      >
        <div class="card">
          <h2>{{ getCompetitionTitle(type) }}</h2>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompetenciasView',
  data() {
    return {
      competitionTypes: [
        'domestic_league',
        'domestic_cup',
        'international_cup',
        'other'
      ],
    };
  },
  methods: {
    getCompetitionTitle(type) {
      const titles = {
        'domestic_cup': 'Copas Locales',
        'domestic_league': 'Ligas Locales',
        'international_cup': 'Torneos Internacionales',
        'other': 'Otras Competiciones'
      };
      return titles[type] || type;
    }
  }
};
</script>

<style>
.grid-container {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-10px) scale(1.05);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

/* Asegura que el router-link no afecte la apariencia de la tarjeta */
.card-link {
  text-decoration: none;
  color: inherit; /* Mantiene el color del texto y elimina el subrayado */
  display: block; /* Esto asegura que el enlace cubra toda la tarjeta */
}

.card-link:hover {
  text-decoration: none; /* Elimina cualquier subrayado al pasar el ratón */
}

.card h2 {
  text-decoration: none; /* Asegura que el título no tenga subrayado */
  color: inherit;
}

.card-link:hover h2 {
  text-decoration: none; /* Refuerza que no se subraye al pasar el ratón */
}
</style>
