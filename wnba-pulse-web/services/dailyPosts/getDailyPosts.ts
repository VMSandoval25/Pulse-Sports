import axios from "axios";
import endpoints from "app/endpoints";
import { DailyResponse } from "./dailyPosts.typings";

export async function getDailyPostRequest(): Promise<DailyResponse> {
  const url = `${process.env.NEXT_PUBLIC_API_URL}/${endpoints.DAILY}`;

  const res = await axios.get<DailyResponse>(url, {
    withCredentials: false,
  });

  return res.data;
}
