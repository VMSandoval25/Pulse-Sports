export interface Sentiment {
  pos: number;
  neu: number;
  neg: number;
}

export interface TopPost {
  url: string;
  title: string;
  disagreement?: number;
  controversy?: number;
}

export interface DailyResponse {
  day: string;
  summary_text: string;

  top_entities: any[]; // you can refine later
  top_topics: any[];

  sentiment_overall: Sentiment;
  top_posts: TopPost[];
}
