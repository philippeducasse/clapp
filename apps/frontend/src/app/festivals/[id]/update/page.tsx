import React from "react";
import { useFestival } from "@/context/FestivalContext";

const UpdateFestivalView = ({ updatedFields }: { updatedFields: any }) => {
  const festivalData = useFestival();

  return <div>UpdateFestivalView</div>;
};

export default UpdateFestivalView;
