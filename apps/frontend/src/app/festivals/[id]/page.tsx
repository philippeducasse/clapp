import FestivalView from "./festival-view";
import festivalApiService from "@/api/festivalApiService";
// This is a Server Component responsible for fetching data.
// It receives the route parameters as an argument from Next.js.

// The main page component is now a simple async function.
// Next.js automatically treats [id] as a dynamic route segment,
// and it will inject the id into the params argument of the component in page.tsx.
export default async function FestivalDetailPage({ params }: { params: { id: string } }) {
  // 1. Fetch the data on the server
  const { id } = await params;
  const festivalData = await festivalApiService.getFestival(id);

  // 2. Pass the data as props to the Client Component
  return <FestivalView festival={festivalData} />;
}
