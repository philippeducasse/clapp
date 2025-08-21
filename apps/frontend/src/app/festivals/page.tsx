"use client";

import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch } from "@/redux/store";
import { selectAllFestivals, selectFestivalsStatus, fetchFestivals } from "@/redux/slices/festivalSlice";
import { FestivalTable } from "../../components/page-components/festival-page/components/view/FestivalTable";
import { DynamicProgress } from "@/components/common/DynamicProgress";

const FestivalsPage = () => {
  const dispatch: AppDispatch = useDispatch();
  const festivals = useSelector(selectAllFestivals);
  const status = useSelector(selectFestivalsStatus);

  useEffect(() => {
    if (status === "idle") {
      dispatch(fetchFestivals());
    }
  }, [status, dispatch]);

  if (status === "loading" || status === "idle") {
    return <DynamicProgress />;
  }

  if (status === "failed") {
    return <div>Error loading festivals.</div>;
  }

  return (
    <div className="container mx-auto py-10">
      <FestivalTable data={festivals} />
    </div>
  );
};

export default FestivalsPage;
