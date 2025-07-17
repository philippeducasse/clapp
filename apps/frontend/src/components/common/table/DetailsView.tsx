import React from "react";
import { SectionCellProps } from "@/interfaces/DetailsView";
import Row from "./Row";

const DetailsView = ({ data }: { data: SectionCellProps[] }) => {
  return data.map((d) => <Row key={d.id} value={d.value} title={d.title} type={d?.type} isLoading={false} />);
};

export default DetailsView;
