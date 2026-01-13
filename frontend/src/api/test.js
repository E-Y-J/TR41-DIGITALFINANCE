export const getTest = async (client) => {
  const { data } = await client.get("/test");
  return data;
};
