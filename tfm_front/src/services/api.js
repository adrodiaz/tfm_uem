import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api';

export const getCompetitions = async () => {
    try {
      const response = await axios.get(`${API_URL}/competitions/`, {
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log('Respuesta de axios:', response.data); // Imprime la respuesta para verificar
      return response.data;
    } catch (error) {
      console.error('Error fetching competitions data:', error);
      throw error;
    }
  };

export const getCompetitionsByType = async (compType) => {
    try {
        const response = await axios.get(`${API_URL}/competitions/${compType}`);
        return response.data;
    } catch (error) {
        console.error('Error fetching filtered competitions data:', error);
        throw error;
    }
};

export const getClubsByCompetition = async (competitionId) => {
    try {
      const response = await axios.get(`${API_URL}/clubs/${competitionId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching clubs data:', error);
      throw error;
    }
  };

  // Función para obtener jugadores con parámetros de búsqueda, paginación incluida
export const getPlayers = async (searchParams, page = 1, perPage = 10) => {
  try {
    const response = await axios.get(`${API_URL}/players`, {
      params: {
        ...searchParams,
        page,
        per_page: perPage
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching players:', error);
    throw error;
  }
};

// Función para obtener detalles de un jugador por su ID
export const getPlayerById = async (playerId) => {
  try {
    const response = await axios.get(`${API_URL}/players/${playerId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching player details:', error);
    throw error;
  }
};

export const getTeams = async (search, page, perPage) => {
  const response = await axios.get(`${API_URL}/teamsSearch`, {
    params: {
      name: search.name,
      country: search.country,
      competition: search.competition,
      page: page,
      per_page: perPage
    }
  });
  return response.data;
};

// Obtener temporadas por competición
export const getSeasons = async (competitionId) => {
  try {
    const response = await axios.get(`${API_URL}/seasons`, {
      params: { competition_id: competitionId },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching seasons:', error);
    throw error;
  }
};

// Obtener juegos por competición y temporada
export async function getGamesByCompetition(competitionId, season) {
  try {
    const response = await fetch(`${API_URL}/games?competition_id=${competitionId}&season=${season}`);
    if (!response.ok) {
      throw new Error('Error fetching games');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching games:', error);
    throw error;
  }
}

export const getTeamsBySeason = async (competitionId, season) => {
  try {
    const response = await axios.get(`${API_URL}/teams`, {
      params: { competition_id: competitionId, season: season }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching teams:', error);
    throw error;
  }
};

export const getTeamPerformanceChart = async (teamId, competitionId) => {
  try {
    const response = await axios.get(`${API_URL}/team_performance_chart`, {
      params: {
        team_id: teamId,
        competition_id: competitionId,
      },
      responseType: 'blob', // Aquí especificamos que queremos un blob
    });

    // Crear un URL de la imagen a partir del blob
    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl; // Devolvemos la URL de la imagen
  } catch (error) {
    console.error('Error fetching team performance chart:', error);
    throw error; // Lanza el error para que se pueda manejar en el componente
  }
};

export const getTeamGoalsChart = async (teamId, competitionId) => {
  try {
    const response = await axios.get(`${API_URL}/team_goals_scored_chart`, {
      params: {
        team_id: teamId,
        competition_id: competitionId,
      },
      responseType: 'blob', // Aquí especificamos que queremos un blob
    });

    // Crear un URL de la imagen a partir del blob
    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl; // Devolvemos la URL de la imagen
  } catch (error) {
    console.error('Error fetching team performance chart:', error);
    throw error; // Lanza el error para que se pueda manejar en el componente
  }
};

export const getTeamConcededGoalsChart = async (teamId, competitionId) => {
  try {
    const response = await axios.get(`${API_URL}/team_goals_conceded_chart`, {
      params: {
        team_id: teamId,
        competition_id: competitionId,
      },
      responseType: 'blob', // Aquí especificamos que queremos un blob
    });

    // Crear un URL de la imagen a partir del blob
    const imageUrl = URL.createObjectURL(response.data);
    return imageUrl; // Devolvemos la URL de la imagen
  } catch (error) {
    console.error('Error fetching team performance chart:', error);
    throw error; // Lanza el error para que se pueda manejar en el componente
  }
};