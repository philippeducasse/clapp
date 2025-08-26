import React from "react";
import BackButton from "../buttons/BackButton";

interface DetailsViewWrapperProps extends React.PropsWithChildren {
  href: string;
}

const DetailsViewWrapper = ({ href, children }: DetailsViewWrapperProps) => {
  return (
    <div className="flex flex-col max-w-6xl mx-auto">
      {children}
      <div className="flex self-end bottom-4 right-4 m-6">
        <BackButton href={href} size={"lg"} />
      </div>
    </div>
  );
};

export default DetailsViewWrapper;
