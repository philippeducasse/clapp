import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";
import { Pencil } from "lucide-react";
interface EditButtonProps {
  href: string;
  label?: string;
  className?: string;
}

const EditButton = ({ label, href, className }: EditButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button className={className} variant="secondary" onClick={handleClick}>
      <Pencil />
      {label ?? "Edit"}
    </Button>
  );
};

export default EditButton;
