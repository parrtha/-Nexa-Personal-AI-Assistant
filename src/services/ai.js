export async function askNexa(message) {
  const response = await fetch(
    "http://127.0.0.1:8010/api/chat",
    {
      method: "POST",

      headers: {
        "Content-Type": "application/json",
      },

      body: JSON.stringify({
        message: message,
      }),
    }
  );

  if (!response.ok) {
    throw new Error("Nexa backend error");
  }

  const data = await response.json();

  return {
    response: data.response,
    webResults: data.web_results || [],
  };
}