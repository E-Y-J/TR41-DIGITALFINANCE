export const getTest = async (client) => {
  const { data } = await client.get("/test");
  console.log("API Test Data:", data);
  return data;
};
