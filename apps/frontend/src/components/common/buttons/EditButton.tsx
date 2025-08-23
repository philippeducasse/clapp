import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";
import { Pencil } from "lucide-react";
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
    <Button className="bg-indigo-600 hover:bg-indigo-500" onClick={handleClick}>
      <Pencil />
      {label ?? "Edit"}
    </Button>
  );
};

export default EditButton;
