export async function getDaily() {
  const url = process.env.NEXT_PUBLIC_API_URL + "/daily";
  const res = await fetch(url, { cache: "no-store" });
  return res.json();
}
