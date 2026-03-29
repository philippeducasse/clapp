import { Button } from "../../ui/button";
import { useRouter } from "next/navigation";
import React from "react";
import { Plus } from "lucide-react";

interface CreateButtonProps {
  href: string;
  label?: string;
  className?: string;
}

const CreateButton = ({ label, href, className }: CreateButtonProps) => {
  const router = useRouter();

  const handleClick = () => {
    router.push(href);
  };

  return (
    <Button variant="default" onClick={handleClick} className={className}>
      <Plus className="text-primary dark:text-foreground" />
      {label ?? "Create"}
    </Button>
  );
};

export default CreateButton;
