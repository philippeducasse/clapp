import React from "react";
import { SectionCellProps } from "@/interfaces/DetailsView";
import Row from "./Row";

const DetailsView = ({ data }: { data: SectionCellProps[] }) => {
  return data.map((d, idx) => (
    <Row key={`${d.title}/ ${idx}`} value={d.value} title={d.title} type={d?.type} isLoading={false} />
  ));
};

export default DetailsView;
