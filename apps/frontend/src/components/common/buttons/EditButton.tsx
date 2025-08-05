import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";

interface EditButtonProps {
  href: string;
  label?: string;
}

const EditButton = ({ label, href }: EditButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button size="sm" className="bg-slate-600" onClick={handleClick}>
      {label ?? "Edit"}
    </Button>
  );
};

export default EditButton;
