export const getUser = async (client) => {
  const { data } = await client.get("/users/me");
  console.log(data);
  return data;
};

export const updateUser = async (client, userData) => {
  const { data } = await client.patch("/users/me", userData);
  return data;
};
