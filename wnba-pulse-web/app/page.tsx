async function getDaily() {
  const url = process.env.NEXT_PUBLIC_API_URL + "/daily";
  const res = await fetch(url, { cache: "no-store" });
  return res.json();
}
export default async function Page() {
  const data = await getDaily();
  const day = data?.day ?? "—";
  const summary = data?.summary_text ?? "Summary coming soon.";
  const posts = data?.top_posts ?? [];
  return (
    <main style={{maxWidth: 720, margin: "2rem auto", padding: "1rem"}}>
      <h1>WNBA Pulse — {day}</h1>
      <section style={{border:"1px solid #ddd", padding:"1rem", borderRadius:8}}>
        <h2>Today’s Recap</h2>
        <p>{summary}</p>
      </section>
      <section style={{border:"1px solid #ddd", padding:"1rem", borderRadius:8, marginTop:"1rem"}}>
        <h2>Most Debated Posts</h2>
        <ul>
          {posts.map((p:any, i:number)=>(
            <li key={i} style={{display:"flex", justifyContent:"space-between", gap:12, margin:"0.5rem 0"}}>
              <a href={p.url} target="_blank">{p.title}</a>
              <span>⚡ {p.disagreement?.toFixed?.(2)} · 🔥 {p.controversy?.toFixed?.(2)}</span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
