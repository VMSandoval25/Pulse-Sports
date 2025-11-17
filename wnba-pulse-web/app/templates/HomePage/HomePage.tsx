"use client";

import { useDailyPostQuery } from "services/dailyPosts/useDailyPostQuery";


export default function HomePage() {
  const { data, isLoading, error } = useDailyPostQuery();

  console.log(data);

  const day = data?.day ?? "—";
  const summary = data?.summary_text ?? "Summary coming soon.";
  const posts = data?.top_posts ?? [];

  if (isLoading) {
    return (
      <main className="mx-auto max-w-2xl py-8 px-4">
        <h1 className="mb-6 text-4xl font-bold">WNBA Pulse — Loading…</h1>
        <p>Loading today&apos;s recap…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl py-8 px-4">
        <h1 className="mb-6 text-4xl font-bold">WNBA Pulse</h1>
        <p className="text-red-600">Couldn&apos;t load today&apos;s data.</p>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl py-8 px-4">
      <h1 className="mb-6 text-4xl font-bold">WNBA Pulse — {day}</h1>

      <section className="mb-6 rounded-lg border border-gray-300 p-4">
        <h2 className="mb-2 text-2xl font-semibold">Today&apos;s Recap</h2>
        <p>{summary}</p>
      </section>

      <section className="rounded-lg border border-gray-300 p-4">
        <h2 className="mb-4 text-2xl font-semibold">Most Debated Posts</h2>
        <ul className="space-y-2">
          {posts.map((p) => (
            <li
              key={p.url}
              className="flex justify-between gap-3"
            >
              <a
                href={p.url}
                target="_blank"
                className="text-blue-600 hover:underline"
              >
                {p.title}
              </a>
              <span className="whitespace-nowrap">
                ⚡ {p.disagreement?.toFixed?.(2)} · 🔥{" "}
                {p.controversy?.toFixed?.(2)}
              </span>
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
