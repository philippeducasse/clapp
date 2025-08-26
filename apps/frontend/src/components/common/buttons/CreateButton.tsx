import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";
import { Plus } from "lucide-react";

interface CreateButtonProps {
  href: string;
  label?: string;
}

const CreateButton = ({ label, href }: CreateButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button variant="default" onClick={handleClick}>
      <Plus />
      {label ?? "Create"}
    </Button>
  );
};

export default CreateButton;
