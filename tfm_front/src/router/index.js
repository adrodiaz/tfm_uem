import { createRouter, createWebHistory } from 'vue-router';
import InicioView from '../components/InicioView.vue';
import CompetenciasView from '../components/CompetenciasView.vue';
import EquiposView from '../components/EquiposView.vue';
import JugadoresView from '../components/JugadoresView.vue';
import CompetitionsByTypeView from '../components/CompetitionsByTypeView.vue';
import ClubsByCompetitionView from '../components/ClubsByCompetitionView.vue';
import GameDetails from '../components/GameDetails.vue';
import SelectResults from '../components/SelectResults.vue';

const routes = [
  { path: '/', name: 'Inicio', component: InicioView },
  { path: '/competiciones', component: CompetenciasView },
  { path: '/equipos', component: EquiposView },
  { path: '/jugadores', component: JugadoresView },
  { path: '/competitions/:compType', name: 'CompetitionsByType', component: CompetitionsByTypeView   },
  { path: '/competitions/:competitionId/clubs', name: 'ClubsByCompetition', component: ClubsByCompetitionView },
  { path: '/competitions/:competitionId/games', name: 'GamesByCompetition', component: () => import('../components/GamesByCompetition.vue'), props: true },
  { path: '/competitions/:competitionId/seasons', name: 'SelectSeason', component: () => import('@/components/SelectSeason.vue') },
  { path: '/competitions/:competitionId/results', name: 'SelectResults', component: SelectResults },
  { path: '/competitions/:competitionId/games/:season', name: 'GamesBySeason', component: () => import('@/components/GamesBySeason.vue') },
  { path: '/games/:gameId', name: 'GameDetails', component: GameDetails }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
