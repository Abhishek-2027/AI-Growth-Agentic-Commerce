import client from './client'

export const logInteraction = async (eventType, productId = null, query = null, sessionId) => {
  try {
    await client.post('/interactions', {
      event_type: eventType,
      product_id: productId,
      query: query
    }, {
      headers: {
        'X-Session-ID': sessionId
      }
    });
  } catch (err) {
    console.error("Failed to log interaction", err);
  }
};

export const getDashboardRecommendations = async (sessionId) => {
  const { data } = await client.get(`/recommendations/dashboard`, {
    headers: {
      'X-Session-ID': sessionId
    }
  });
  return data;
};

export const getMyPreferences = async (sessionId) => {
  const { data } = await client.get('/interactions/preferences', {
    headers: {
      'X-Session-ID': sessionId
    }
  });
  return data;
};
