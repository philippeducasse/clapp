import FestivalView from "./festival-view";
import festivalApiSerivice from "@/api/festivalApiService";
// This is a Server Component responsible for fetching data.
// It receives the route parameters as an argument from Next.js.

// The main page component is now a simple async function.
export default async function FestivalDetailPage({ params }: { params: { id: string } }) {
  // 1. Fetch the data on the server
  const festivalData = await festivalApiSerivice.getFestival(params.id);

  // 2. Pass the data as props to the Client Component
  return <FestivalView festival={festivalData} />;
}
