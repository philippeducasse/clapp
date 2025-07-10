import { FestivalProvider } from "@/context/FestivalContext";
import festivalApiService from "@/api/festivalApiService";
import { ReactNode } from "react";

export default async function FestivalLayout({ children, params }: { children: ReactNode; params: { id: string } }) {
  const { id } = await params;
  const festivalData = await festivalApiService.getFestival(id);

  return <FestivalProvider value={festivalData}>{children}</FestivalProvider>;
}
