import React from "react";
import { DetailsViewProps } from "@/interfaces/DetailsView";
import Row from "./Row";

const DetailsView = ({ data, title }: DetailsViewProps) => {
  return data.map((d) => <Row value={d.value} title={d.title} type={d?.type} isLoading={false} />);
};

export default DetailsView;
