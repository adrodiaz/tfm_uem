<template>
  <div>
    <h1>{{ getCompetitionTitle(compType) }}</h1>
    <div class="grid-container" v-if="competitions.length"> <!-- Agregar v-if aquí -->
      <CompetitionCard
        v-for="competition in competitions"
        :key="competition.competition_id"
        :competition="competition"
      />
    </div>
    <p v-else>No competitions found.</p> <!-- Mantener v-else para mostrar el mensaje -->
  </div>
</template>
  
  <script>
  import { getCompetitionsByType } from '../services/api';
  import CompetitionCard from './CompetitionCard.vue';
  
  export default {
    name: 'CompetitionsByTypeView',
    components: {
      CompetitionCard
    },
    data() {
      return {
        competitions: [],
        compType: this.$route.params.compType
      };
    },
    methods: {
      async fetchCompetitions() {
        try {
          this.competitions = await getCompetitionsByType(this.compType);
        } catch (error) {
          console.error('Error loading competitions:', error);
        }
      },
      getCompetitionTitle(type) {
        const titles = {
          'domestic_cup': 'Copas Locales',
          'uefa_super_cup': 'UEFA Super Copa',
          'domestic_league': 'Ligas Locales',
          'international_cup': 'Copas Internacionales',
          'league_cup': 'Copas de Liga',
          'fifa_club_world_cup': 'FIFA Campeonato Mundial',
          'other': 'Otras Competencias'
        };
        return titles[type] || type;
      }
    },
    async created() {
      await this.fetchCompetitions();
    }
  };
  </script>
  
  