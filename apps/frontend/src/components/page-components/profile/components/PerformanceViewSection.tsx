import React from "react";
import { Performance } from "@/interfaces/entities/Performance";
import { getPerformanceInfo } from "../helpers/getPerformanceInfo";
import { Music } from "lucide-react";
import AuxilliarySection from "@/components/common/details-view/AuxilliarySection";

interface PerformanceViewSectionProps {
  title: string;
  performances: Performance[];
  entityId: number;
  onDelete: (index: number) => void;
}

const PerformanceViewSection = ({
  title,
  performances,
  entityId,
  onDelete,
}: PerformanceViewSectionProps) => {
  return performances.map((performance) => (
    <AuxilliarySection
      title={title}
      icon={<Music className="text-emerald-600 dark:text-emerald-400" />}
      item={performance}
      entityId={entityId}
      formatData={getPerformanceInfo}
      getItemKey={(performance, idx) => `${performance.id}_${idx}`}
      editPath="performances"
      onDelete={onDelete}
    />
  ));
};

export default PerformanceViewSection;
