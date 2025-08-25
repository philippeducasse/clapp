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
    <Button
      className="text-emerald-600 border-emerald-600 hover:bg-background hover:text-emerald-500 hover:border-emerald-500 dark:text-emerald-400 dark:border-emerald-400 dark:hover:text-emerald-300 dark:hover:border-emerald-300"
      variant="outline"
      onClick={handleClick}
    >
      <Pencil />
      {label ?? "Edit"}
    </Button>
  );
};

export default EditButton;
