import React from "react";
import { Performance } from "@/interfaces/entities/Performance";
import { getPerformanceInfo } from "../helpers/getPerformanceInfo";
import { Info } from "lucide-react";
import AuxilliarySection from "@/components/common/details-view/AuxilliarySection";

interface PerformanceViewSectionProps {
  performances: Performance[];
  onDelete: (index: number) => void;
}

const PerformanceViewSection = ({ performances, onDelete }: PerformanceViewSectionProps) => {
  return (
    <>
      {performances.map((performance, index) => (
        <AuxilliarySection
          key={`${performance.id}_${index}`}
          title={performance.performanceTitle}
          icon={<Info className="text-emerald-600 dark:text-emerald-400" />}
          item={performance}
          index={performance.id}
          entityId={"profile"}
          formatData={getPerformanceInfo}
          getItemKey={(performance, idx) => `${performance.id}_${idx}`}
          editPath="performances"
          onDelete={onDelete}
        />
      ))}
    </>
  );
};

export default PerformanceViewSection;
